package fusefs

import (
	"context"
	"errors"
	"fmt"
	"io"
	"sync"
	"sync/atomic"
	"time"

	agfs "github.com/c4pt0r/agfs/agfs-sdk/go"
	log "github.com/sirupsen/logrus"
)

// handleType indicates whether a handle is remote (server-side) or local (client-side fallback)
type handleType int

const (
	handleTypeRemote       handleType = iota // Server supports HandleFS
	handleTypeRemoteStream                   // Server supports HandleFS with streaming
	handleTypeLocal                          // Server doesn't support HandleFS, use local wrapper
)

// handleInfo stores information about an open handle
type handleInfo struct {
	htype      handleType
	agfsHandle int64 // For remote handles: server-side handle ID
	path       string
	flags      agfs.OpenFlag
	mode       uint32
	// Read buffer for local handles - caches first read to avoid multiple server requests
	readBuffer []byte
	// Stream reader for streaming handles
	streamReader io.ReadCloser
	// Buffer for stream reads (sliding window to prevent memory leak)
	streamBuffer []byte
	streamBase   int64 // Base offset of streamBuffer[0] in the logical stream
	// Context for cancelling background goroutines
	streamCtx    context.Context
	streamCancel context.CancelFunc
}

// HandleManager manages the mapping between FUSE handles and AGFS handles
type HandleManager struct {
	client *agfs.Client
	mu     sync.RWMutex
	// Map FUSE handle ID to handle info
	handles map[uint64]*handleInfo
	// Counter for generating unique FUSE handle IDs
	nextHandle uint64
}

// NewHandleManager creates a new handle manager
func NewHandleManager(client *agfs.Client) *HandleManager {
	return &HandleManager{
		client:     client,
		handles:    make(map[uint64]*handleInfo),
		nextHandle: 1,
	}
}

// Open opens a file and returns a FUSE handle ID
// If the server supports HandleFS, it uses server-side handles
// Otherwise, it falls back to local handle management
func (hm *HandleManager) Open(path string, flags agfs.OpenFlag, mode uint32) (uint64, error) {
	// Try to open handle on server first
	agfsHandle, err := hm.client.OpenHandle(path, flags, mode)

	// Generate FUSE handle ID
	fuseHandle := atomic.AddUint64(&hm.nextHandle, 1)

	hm.mu.Lock()
	defer hm.mu.Unlock()

	if err != nil {
		// Check if error is because HandleFS is not supported
		if errors.Is(err, agfs.ErrNotSupported) {
			// Fall back to local handle management
			log.Debugf("HandleFS not supported for %s, using local handle", path)
			hm.handles[fuseHandle] = &handleInfo{
				htype: handleTypeLocal,
				path:  path,
				flags: flags,
				mode:  mode,
			}
			return fuseHandle, nil
		}
		log.Debugf("Failed to open handle for %s: %v", path, err)
		return 0, fmt.Errorf("failed to open handle: %w", err)
	}

	log.Debugf("Opened remote handle for %s (handle=%d)", path, agfsHandle)

	// Try to open streaming connection for read handles
	if flags&agfs.OpenFlagWriteOnly == 0 {
		streamReader, streamErr := hm.client.ReadHandleStream(agfsHandle)
		if streamErr == nil {
			ctx, cancel := context.WithCancel(context.Background())
			log.Debugf("Opened stream for handle %d on %s", agfsHandle, path)
			hm.handles[fuseHandle] = &handleInfo{
				htype:        handleTypeRemoteStream,
				agfsHandle:   agfsHandle,
				path:         path,
				flags:        flags,
				mode:         mode,
				streamReader: streamReader,
				streamCtx:    ctx,
				streamCancel: cancel,
			}
			return fuseHandle, nil
		}
		log.Debugf("Failed to open stream for %s, using regular handle: %v", path, streamErr)
	}

	// Server supports HandleFS but not streaming (or write handle)
	hm.handles[fuseHandle] = &handleInfo{
		htype:      handleTypeRemote,
		agfsHandle: agfsHandle,
		path:       path,
		flags:      flags,
		mode:       mode,
	}

	return fuseHandle, nil
}

// Close closes a handle
func (hm *HandleManager) Close(fuseHandle uint64) error {
	hm.mu.Lock()
	info, ok := hm.handles[fuseHandle]
	if !ok {
		hm.mu.Unlock()
		return fmt.Errorf("handle %d not found", fuseHandle)
	}
	delete(hm.handles, fuseHandle)
	hm.mu.Unlock()

	// Cancel context to stop any background goroutines
	if info.streamCancel != nil {
		info.streamCancel()
	}

	// Close stream reader if present
	if info.streamReader != nil {
		info.streamReader.Close()
	}

	// Clear buffer to release memory
	info.streamBuffer = nil

	// Remote handles: close on server
	if info.htype == handleTypeRemote || info.htype == handleTypeRemoteStream {
		if err := hm.client.CloseHandle(info.agfsHandle); err != nil {
			return fmt.Errorf("failed to close handle: %w", err)
		}
		return nil
	}

	// Local handles: nothing to do on close since writes are sent immediately
	return nil
}

// Read reads data from a handle
func (hm *HandleManager) Read(fuseHandle uint64, offset int64, size int) ([]byte, error) {
	hm.mu.Lock()
	info, ok := hm.handles[fuseHandle]
	if !ok {
		hm.mu.Unlock()
		return nil, fmt.Errorf("handle %d not found", fuseHandle)
	}

	// Streaming handle: read from stream
	if info.htype == handleTypeRemoteStream && info.streamReader != nil {
		return hm.readFromStream(info, offset, size)
	}

	if info.htype == handleTypeRemote {
		hm.mu.Unlock()
		// Use server-side handle
		data, err := hm.client.ReadHandle(info.agfsHandle, offset, size)
		if err != nil {
			return nil, fmt.Errorf("failed to read handle: %w", err)
		}
		return data, nil
	}

	// Local handle: cache the first read and return from cache for subsequent reads
	// This is critical for special filesystems like queuefs where each read
	// should be an independent atomic operation (e.g., each read from dequeue
	// should consume only one message, not multiple)
	if info.readBuffer == nil {
		// First read: fetch ALL data from server and cache (use size=-1 to read all)
		path := info.path
		hm.mu.Unlock()

		data, err := hm.client.Read(path, 0, -1) // Read all data
		if err != nil {
			return nil, fmt.Errorf("failed to read file: %w", err)
		}

		// Cache the data
		hm.mu.Lock()
		// Re-check if handle still exists
		info, ok = hm.handles[fuseHandle]
		if ok {
			info.readBuffer = data
		}
		hm.mu.Unlock()

		// Return requested portion
		if offset >= int64(len(data)) {
			return []byte{}, nil
		}
		end := offset + int64(size)
		if end > int64(len(data)) {
			end = int64(len(data))
		}
		return data[offset:end], nil
	}

	// Return from cache or empty for subsequent reads
	if info.readBuffer != nil {
		if offset >= int64(len(info.readBuffer)) {
			hm.mu.Unlock()
			return []byte{}, nil // EOF
		}
		end := offset + int64(size)
		if end > int64(len(info.readBuffer)) {
			end = int64(len(info.readBuffer))
		}
		result := info.readBuffer[offset:end]
		hm.mu.Unlock()
		return result, nil
	}

	// No cached data and offset > 0, return empty
	hm.mu.Unlock()
	return []byte{}, nil
}

// streamReadResult holds the result of a stream read operation
type streamReadResult struct {
	n   int
	err error
	buf []byte
}

// Maximum buffer size before trimming (1MB sliding window)
const maxStreamBufferSize = 1 * 1024 * 1024

// readFromStream reads data from a streaming handle
// Must be called with hm.mu held
// Uses sliding window buffer to prevent memory leak
func (hm *HandleManager) readFromStream(info *handleInfo, offset int64, size int) ([]byte, error) {
	// Convert absolute offset to relative offset in buffer
	relOffset := offset - info.streamBase

	// Fast path: if we already have data at the requested offset, return immediately
	if relOffset >= 0 && relOffset < int64(len(info.streamBuffer)) {
		end := relOffset + int64(size)
		if end > int64(len(info.streamBuffer)) {
			end = int64(len(info.streamBuffer))
		}
		result := make([]byte, end-relOffset)
		copy(result, info.streamBuffer[relOffset:end])

		// Trim old data if buffer is too large (sliding window)
		hm.trimStreamBuffer(info, offset+int64(size))

		hm.mu.Unlock()
		return result, nil
	}

	// Check if requested offset is before our buffer (data already trimmed)
	if relOffset < 0 {
		hm.mu.Unlock()
		log.Warnf("Requested offset %d is before buffer base %d (data already trimmed)", offset, info.streamBase)
		return []byte{}, nil
	}

	// No data at offset yet, need to read from stream
	hm.mu.Unlock()

	// Use context for cancellation
	ctx := info.streamCtx
	if ctx == nil {
		ctx = context.Background()
	}

	readTimeout := 5 * time.Second
	buf := make([]byte, 64*1024) // 64KB chunks
	resultCh := make(chan streamReadResult, 1)

	go func() {
		n, err := info.streamReader.Read(buf)
		select {
		case resultCh <- streamReadResult{n: n, err: err, buf: buf}:
		case <-ctx.Done():
			// Context cancelled, goroutine exits cleanly
		}
	}()

	var n int
	var err error
	var readBuf []byte
	select {
	case result := <-resultCh:
		n = result.n
		err = result.err
		readBuf = result.buf
	case <-time.After(readTimeout):
		// Timeout - no data available
		return []byte{}, nil
	case <-ctx.Done():
		// Handle closed
		return []byte{}, nil
	}

	hm.mu.Lock()
	if n > 0 {
		info.streamBuffer = append(info.streamBuffer, readBuf[:n]...)
	}

	if err != nil && err != io.EOF {
		hm.mu.Unlock()
		return nil, fmt.Errorf("failed to read from stream: %w", err)
	}

	// Recalculate relative offset after potential buffer changes
	relOffset = offset - info.streamBase

	// Return whatever data we have at the requested offset
	if relOffset < 0 || relOffset >= int64(len(info.streamBuffer)) {
		hm.mu.Unlock()
		return []byte{}, nil // EOF or no data at this offset
	}

	end := relOffset + int64(size)
	if end > int64(len(info.streamBuffer)) {
		end = int64(len(info.streamBuffer))
	}

	result := make([]byte, end-relOffset)
	copy(result, info.streamBuffer[relOffset:end])

	// Trim old data if buffer is too large
	hm.trimStreamBuffer(info, offset+int64(size))

	hm.mu.Unlock()
	return result, nil
}

// trimStreamBuffer removes old data from the buffer to prevent memory leak
// Must be called with hm.mu held
func (hm *HandleManager) trimStreamBuffer(info *handleInfo, consumedUpTo int64) {
	if len(info.streamBuffer) <= maxStreamBufferSize {
		return
	}

	// Keep only data after the consumed position (with some margin)
	trimPoint := consumedUpTo - info.streamBase
	if trimPoint <= 0 {
		return
	}

	// Keep at least 64KB of already-read data for potential re-reads
	margin := int64(64 * 1024)
	if trimPoint > margin {
		trimPoint -= margin
	} else {
		trimPoint = 0
	}

	if trimPoint > 0 && trimPoint < int64(len(info.streamBuffer)) {
		// Trim the buffer
		newBuffer := make([]byte, int64(len(info.streamBuffer))-trimPoint)
		copy(newBuffer, info.streamBuffer[trimPoint:])
		info.streamBuffer = newBuffer
		info.streamBase += trimPoint
		log.Debugf("Trimmed stream buffer: new base=%d, new size=%d", info.streamBase, len(info.streamBuffer))
	}
}

// Write writes data to a handle
func (hm *HandleManager) Write(fuseHandle uint64, data []byte, offset int64) (int, error) {
	hm.mu.Lock()
	info, ok := hm.handles[fuseHandle]
	if !ok {
		hm.mu.Unlock()
		return 0, fmt.Errorf("handle %d not found", fuseHandle)
	}

	if info.htype == handleTypeRemote {
		hm.mu.Unlock()
		// Use server-side handle (write directly)
		written, err := hm.client.WriteHandle(info.agfsHandle, data, offset)
		if err != nil {
			return 0, fmt.Errorf("failed to write handle: %w", err)
		}
		return written, nil
	}

	// Local handle: send data directly to server for each write
	// This is critical for special filesystems like queuefs where each write
	// should be an independent atomic operation (e.g., each write to enqueue
	// should create a separate queue message)
	path := info.path
	hm.mu.Unlock()

	// Send directly to server
	_, err := hm.client.Write(path, data)
	if err != nil {
		return 0, fmt.Errorf("failed to write to server: %w", err)
	}

	return len(data), nil
}

// Sync syncs a handle
func (hm *HandleManager) Sync(fuseHandle uint64) error {
	hm.mu.Lock()
	info, ok := hm.handles[fuseHandle]
	if !ok {
		hm.mu.Unlock()
		return fmt.Errorf("handle %d not found", fuseHandle)
	}

	// Remote handles: sync on server
	if info.htype == handleTypeRemote {
		hm.mu.Unlock()
		if err := hm.client.SyncHandle(info.agfsHandle); err != nil {
			return fmt.Errorf("failed to sync handle: %w", err)
		}
		return nil
	}

	// Local handles: nothing to sync since writes are sent immediately
	hm.mu.Unlock()
	return nil
}

// CloseAll closes all open handles
func (hm *HandleManager) CloseAll() error {
	hm.mu.Lock()
	handles := make(map[uint64]*handleInfo)
	for k, v := range hm.handles {
		handles[k] = v
	}
	hm.handles = make(map[uint64]*handleInfo)
	hm.mu.Unlock()

	var lastErr error
	for _, info := range handles {
		// Cancel context to stop background goroutines
		if info.streamCancel != nil {
			info.streamCancel()
		}
		// Close stream reader if present
		if info.streamReader != nil {
			info.streamReader.Close()
		}
		// Clear buffer to release memory
		info.streamBuffer = nil
		if info.htype == handleTypeRemote || info.htype == handleTypeRemoteStream {
			if err := hm.client.CloseHandle(info.agfsHandle); err != nil {
				lastErr = err
			}
		}
	}

	return lastErr
}

// Count returns the number of open handles
func (hm *HandleManager) Count() int {
	hm.mu.RLock()
	defer hm.mu.RUnlock()
	return len(hm.handles)
}

