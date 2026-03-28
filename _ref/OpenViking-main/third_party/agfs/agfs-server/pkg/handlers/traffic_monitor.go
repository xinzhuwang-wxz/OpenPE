package handlers

import (
	"sync"
	"sync/atomic"
	"time"
)

// TrafficMonitor monitors network traffic for all handlers
type TrafficMonitor struct {
	// Byte counters (atomic)
	bytesRead    atomic.Int64
	bytesWritten atomic.Int64

	// Time-based statistics
	mu              sync.RWMutex
	lastCheckTime   time.Time
	lastBytesRead   int64
	lastBytesWritten int64

	// Current rates (bytes per second)
	currentReadRate  float64
	currentWriteRate float64

	// Peak rates
	peakReadRate  float64
	peakWriteRate float64

	// Total statistics
	totalBytesRead    int64
	totalBytesWritten int64
	startTime         time.Time
}

// NewTrafficMonitor creates a new traffic monitor
func NewTrafficMonitor() *TrafficMonitor {
	now := time.Now()
	tm := &TrafficMonitor{
		lastCheckTime: now,
		startTime:     now,
	}

	// Start background rate calculator
	go tm.updateRates()

	return tm
}

// RecordRead records bytes read (download/downstream)
func (tm *TrafficMonitor) RecordRead(bytes int64) {
	tm.bytesRead.Add(bytes)
}

// RecordWrite records bytes written (upload/upstream)
func (tm *TrafficMonitor) RecordWrite(bytes int64) {
	tm.bytesWritten.Add(bytes)
}

// updateRates periodically calculates current transfer rates
func (tm *TrafficMonitor) updateRates() {
	ticker := time.NewTicker(1 * time.Second)
	defer ticker.Stop()

	for range ticker.C {
		tm.calculateRates()
	}
}

// calculateRates calculates current transfer rates
func (tm *TrafficMonitor) calculateRates() {
	tm.mu.Lock()
	defer tm.mu.Unlock()

	now := time.Now()
	elapsed := now.Sub(tm.lastCheckTime).Seconds()

	if elapsed <= 0 {
		return
	}

	// Get current counters
	currentRead := tm.bytesRead.Load()
	currentWrite := tm.bytesWritten.Load()

	// Calculate rates (bytes per second)
	readDelta := currentRead - tm.lastBytesRead
	writeDelta := currentWrite - tm.lastBytesWritten

	tm.currentReadRate = float64(readDelta) / elapsed
	tm.currentWriteRate = float64(writeDelta) / elapsed

	// Update peak rates
	if tm.currentReadRate > tm.peakReadRate {
		tm.peakReadRate = tm.currentReadRate
	}
	if tm.currentWriteRate > tm.peakWriteRate {
		tm.peakWriteRate = tm.currentWriteRate
	}

	// Update totals
	tm.totalBytesRead += readDelta
	tm.totalBytesWritten += writeDelta

	// Update last check values
	tm.lastCheckTime = now
	tm.lastBytesRead = currentRead
	tm.lastBytesWritten = currentWrite
}

// TrafficStats contains traffic statistics
type TrafficStats struct {
	// Current rates in bytes/s
	DownstreamBps int64 `json:"downstream_bps"` // Download rate (bytes/second)
	UpstreamBps   int64 `json:"upstream_bps"`   // Upload rate (bytes/second)

	// Peak rates in bytes/s
	PeakDownstreamBps int64 `json:"peak_downstream_bps"` // Peak download rate (bytes/second)
	PeakUpstreamBps   int64 `json:"peak_upstream_bps"`   // Peak upload rate (bytes/second)

	// Total transferred in bytes
	TotalDownloadBytes int64 `json:"total_download_bytes"`
	TotalUploadBytes   int64 `json:"total_upload_bytes"`

	// Uptime
	UptimeSeconds int64 `json:"uptime_seconds"`
}

// GetStats returns current traffic statistics
func (tm *TrafficMonitor) GetStats() interface{} {
	tm.mu.RLock()
	defer tm.mu.RUnlock()

	return TrafficStats{
		DownstreamBps:      int64(tm.currentReadRate),
		UpstreamBps:        int64(tm.currentWriteRate),
		PeakDownstreamBps:  int64(tm.peakReadRate),
		PeakUpstreamBps:    int64(tm.peakWriteRate),
		TotalDownloadBytes: tm.totalBytesRead,
		TotalUploadBytes:   tm.totalBytesWritten,
		UptimeSeconds:      int64(time.Since(tm.startTime).Seconds()),
	}
}
