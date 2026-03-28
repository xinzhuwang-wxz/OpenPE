package filesystem

import (
	"fmt"
	"io"
)

// BaseFileSystem provides default implementations for optional interfaces
// File systems can embed this struct to get fallback implementations
// that simulate advanced features using basic operations
type BaseFileSystem struct {
	FS FileSystem
}

// NewBaseFileSystem creates a new BaseFileSystem wrapping the given FileSystem
func NewBaseFileSystem(fs FileSystem) *BaseFileSystem {
	return &BaseFileSystem{FS: fs}
}

// WriteAt provides a default implementation of RandomWriter using Read + Modify + Write
// This is inefficient but provides compatibility for file systems that don't natively support it
func (b *BaseFileSystem) WriteAt(path string, data []byte, offset int64) (int64, error) {
	if offset < 0 {
		return 0, fmt.Errorf("invalid offset: %d", offset)
	}

	// Get current file info
	stat, err := b.FS.Stat(path)
	if err != nil {
		// File doesn't exist, create it with padding
		if offset > 0 {
			// Create file with zero padding + data
			padded := make([]byte, offset+int64(len(data)))
			copy(padded[offset:], data)
			_, err = b.FS.Write(path, padded, -1, WriteFlagCreate|WriteFlagTruncate)
		} else {
			_, err = b.FS.Write(path, data, -1, WriteFlagCreate|WriteFlagTruncate)
		}
		if err != nil {
			return 0, err
		}
		return int64(len(data)), nil
	}

	// Read current content
	currentData, err := b.FS.Read(path, 0, -1)
	if err != nil && err != io.EOF {
		return 0, err
	}

	// Calculate new size
	newSize := offset + int64(len(data))
	if newSize < stat.Size {
		newSize = stat.Size
	}

	// Create new content
	newData := make([]byte, newSize)
	copy(newData, currentData)
	copy(newData[offset:], data)

	// Write back
	_, err = b.FS.Write(path, newData, -1, WriteFlagTruncate)
	if err != nil {
		return 0, err
	}

	return int64(len(data)), nil
}

// Truncate provides a default implementation using Read + Resize + Write
func (b *BaseFileSystem) Truncate(path string, size int64) error {
	if size < 0 {
		return fmt.Errorf("invalid size: %d", size)
	}

	// Check if file exists
	stat, err := b.FS.Stat(path)
	if err != nil {
		return err
	}

	if stat.IsDir {
		return fmt.Errorf("is a directory: %s", path)
	}

	// Read current content
	currentData, err := b.FS.Read(path, 0, -1)
	if err != nil && err != io.EOF {
		return err
	}

	// Resize
	var newData []byte
	if size <= int64(len(currentData)) {
		newData = currentData[:size]
	} else {
		newData = make([]byte, size)
		copy(newData, currentData)
		// Rest is automatically zero-filled
	}

	// Write back
	_, err = b.FS.Write(path, newData, -1, WriteFlagTruncate)
	return err
}

// Touch provides a default implementation that creates or updates a file
func (b *BaseFileSystem) Touch(path string) error {
	// Check if file exists
	stat, err := b.FS.Stat(path)
	if err != nil {
		// File doesn't exist, create empty file
		_, err = b.FS.Write(path, []byte{}, -1, WriteFlagCreate)
		return err
	}

	if stat.IsDir {
		return fmt.Errorf("cannot touch directory: %s", path)
	}

	// Read and write back to update timestamp
	data, err := b.FS.Read(path, 0, -1)
	if err != nil && err != io.EOF {
		return err
	}

	_, err = b.FS.Write(path, data, -1, WriteFlagNone)
	return err
}

// Sync provides a no-op default implementation
// Most in-memory or network file systems don't need explicit sync
func (b *BaseFileSystem) Sync(path string) error {
	// Default: no-op, as most virtual file systems don't need sync
	return nil
}

// GetCapabilities returns default capabilities
func (b *BaseFileSystem) GetCapabilities() Capabilities {
	return DefaultCapabilities()
}

// GetPathCapabilities returns default capabilities for any path
func (b *BaseFileSystem) GetPathCapabilities(path string) Capabilities {
	return b.GetCapabilities()
}

// === BaseFileHandle ===

// BaseFileHandle provides a default FileHandle implementation
// that uses the underlying FileSystem's Read/Write methods
type BaseFileHandle struct {
	id       int64
	path     string
	flags    OpenFlag
	fs       FileSystem
	position int64
	closed   bool
}

// NewBaseFileHandle creates a new BaseFileHandle
func NewBaseFileHandle(id int64, path string, flags OpenFlag, fs FileSystem) *BaseFileHandle {
	return &BaseFileHandle{
		id:       id,
		path:     path,
		flags:    flags,
		fs:       fs,
		position: 0,
		closed:   false,
	}
}

// ID returns the handle ID
func (h *BaseFileHandle) ID() int64 {
	return h.id
}

// Path returns the file path
func (h *BaseFileHandle) Path() string {
	return h.path
}

// Flags returns the open flags
func (h *BaseFileHandle) Flags() OpenFlag {
	return h.flags
}

// Read reads from the current position
func (h *BaseFileHandle) Read(buf []byte) (int, error) {
	if h.closed {
		return 0, fmt.Errorf("handle is closed")
	}
	if h.flags&O_WRONLY != 0 {
		return 0, fmt.Errorf("handle not open for reading")
	}

	data, err := h.fs.Read(h.path, h.position, int64(len(buf)))
	if err != nil && err != io.EOF {
		return 0, err
	}

	n := copy(buf, data)
	h.position += int64(n)

	if err == io.EOF {
		return n, io.EOF
	}
	return n, nil
}

// ReadAt reads from the specified offset
func (h *BaseFileHandle) ReadAt(buf []byte, offset int64) (int, error) {
	if h.closed {
		return 0, fmt.Errorf("handle is closed")
	}
	if h.flags&O_WRONLY != 0 {
		return 0, fmt.Errorf("handle not open for reading")
	}

	data, err := h.fs.Read(h.path, offset, int64(len(buf)))
	if err != nil && err != io.EOF {
		return 0, err
	}

	n := copy(buf, data)
	if err == io.EOF {
		return n, io.EOF
	}
	return n, nil
}

// Write writes at the current position
func (h *BaseFileHandle) Write(data []byte) (int, error) {
	if h.closed {
		return 0, fmt.Errorf("handle is closed")
	}
	if h.flags == O_RDONLY {
		return 0, fmt.Errorf("handle not open for writing")
	}

	var offset int64 = h.position
	var flags WriteFlag = WriteFlagNone

	if h.flags&O_APPEND != 0 {
		flags |= WriteFlagAppend
		offset = -1
	}

	n, err := h.fs.Write(h.path, data, offset, flags)
	if err != nil {
		return 0, err
	}

	if h.flags&O_APPEND == 0 {
		h.position += n
	}

	return int(n), nil
}

// WriteAt writes at the specified offset
func (h *BaseFileHandle) WriteAt(data []byte, offset int64) (int, error) {
	if h.closed {
		return 0, fmt.Errorf("handle is closed")
	}
	if h.flags == O_RDONLY {
		return 0, fmt.Errorf("handle not open for writing")
	}

	n, err := h.fs.Write(h.path, data, offset, WriteFlagNone)
	if err != nil {
		return 0, err
	}

	return int(n), nil
}

// Seek changes the current position
func (h *BaseFileHandle) Seek(offset int64, whence int) (int64, error) {
	if h.closed {
		return 0, fmt.Errorf("handle is closed")
	}

	stat, err := h.fs.Stat(h.path)
	if err != nil {
		return 0, err
	}

	var newPos int64
	switch whence {
	case 0: // SEEK_SET
		newPos = offset
	case 1: // SEEK_CUR
		newPos = h.position + offset
	case 2: // SEEK_END
		newPos = stat.Size + offset
	default:
		return 0, fmt.Errorf("invalid whence: %d", whence)
	}

	if newPos < 0 {
		return 0, fmt.Errorf("negative position: %d", newPos)
	}

	h.position = newPos
	return h.position, nil
}

// Sync syncs the file
func (h *BaseFileHandle) Sync() error {
	if h.closed {
		return fmt.Errorf("handle is closed")
	}

	if syncer, ok := h.fs.(Syncer); ok {
		return syncer.Sync(h.path)
	}
	return nil
}

// Close closes the handle
func (h *BaseFileHandle) Close() error {
	if h.closed {
		return nil
	}
	h.closed = true
	return nil
}

// Stat returns file information
func (h *BaseFileHandle) Stat() (*FileInfo, error) {
	if h.closed {
		return nil, fmt.Errorf("handle is closed")
	}
	return h.fs.Stat(h.path)
}

// Ensure BaseFileHandle implements FileHandle
var _ FileHandle = (*BaseFileHandle)(nil)
