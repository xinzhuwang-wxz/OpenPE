package filesystem

// Capabilities describes the features supported by a file system
type Capabilities struct {
	// Basic capabilities
	SupportsRandomWrite bool // Supports offset write (pwrite)
	SupportsTruncate    bool // Supports file truncation
	SupportsSync        bool // Supports sync/fsync
	SupportsTouch       bool // Supports efficient touch operation
	SupportsFileHandle  bool // Supports FileHandle interface

	// Special semantics
	IsAppendOnly      bool // Only supports append operations (e.g., QueueFS enqueue)
	IsReadDestructive bool // Read has side effects (e.g., QueueFS dequeue)
	IsObjectStore     bool // Object store semantics, no offset write (e.g., S3FS)
	IsBroadcast       bool // Supports multiple reader fanout (e.g., StreamFS)
	IsReadOnly        bool // Read-only file system

	// Streaming capabilities
	SupportsStreamRead  bool // Supports streaming read (Streamer interface)
	SupportsStreamWrite bool // Supports streaming write
}

// CapabilityProvider is implemented by file systems that can report their capabilities
type CapabilityProvider interface {
	// GetCapabilities returns the overall capabilities of the file system
	GetCapabilities() Capabilities

	// GetPathCapabilities returns capabilities for a specific path
	// Some paths may have different capabilities than the overall file system
	// (e.g., QueueFS /queue/enqueue is append-only, /queue/dequeue is read-destructive)
	GetPathCapabilities(path string) Capabilities
}

// === Extension Interfaces ===

// RandomWriter is implemented by file systems that support random position writes
// This is required for efficient FUSE pwrite support
type RandomWriter interface {
	// WriteAt writes data at the specified offset without affecting other parts of the file
	// This is similar to POSIX pwrite
	WriteAt(path string, data []byte, offset int64) (int64, error)
}

// Truncater is implemented by file systems that support file truncation
type Truncater interface {
	// Truncate changes the size of the file
	// If size is less than current size, data is removed from the end
	// If size is greater than current size, file is extended with zero bytes
	Truncate(path string, size int64) error
}

// Syncer is implemented by file systems that support data synchronization
type Syncer interface {
	// Sync ensures all data for the file is written to persistent storage
	Sync(path string) error
}

// === Special Semantics Interfaces ===

// AppendOnlyFS marks file systems where certain paths only support append operations
// This is useful for queue-like services where data can only be added, not modified
type AppendOnlyFS interface {
	// IsAppendOnly returns true if the specified path only supports append operations
	IsAppendOnly(path string) bool
}

// ReadDestructiveFS marks file systems where read operations have side effects
// This is useful for queue-like services where reading removes data
type ReadDestructiveFS interface {
	// IsReadDestructive returns true if reading from the path has side effects
	// (e.g., dequeue operation removes the message)
	IsReadDestructive(path string) bool
}

// ObjectStoreFS marks file systems with object store semantics
// Object stores typically don't support random writes or truncation
type ObjectStoreFS interface {
	// IsObjectStore returns true if this is an object store (e.g., S3)
	// Object stores require full object replacement for writes
	IsObjectStore() bool
}

// BroadcastFS marks file systems that support multiple reader fanout
// This is useful for streaming services where multiple clients receive the same data
type BroadcastFS interface {
	// IsBroadcast returns true if the path supports broadcast/fanout to multiple readers
	IsBroadcast(path string) bool
}

// ReadOnlyFS marks file systems or paths that are read-only
type ReadOnlyFS interface {
	// IsReadOnly returns true if the specified path is read-only
	IsReadOnly(path string) bool
}

// === Default Capabilities ===

// DefaultCapabilities returns a Capabilities struct with common defaults
// This represents a basic read/write file system without special features
func DefaultCapabilities() Capabilities {
	return Capabilities{
		SupportsRandomWrite: false,
		SupportsTruncate:    false,
		SupportsSync:        false,
		SupportsTouch:       false,
		SupportsFileHandle:  false,
		IsAppendOnly:        false,
		IsReadDestructive:   false,
		IsObjectStore:       false,
		IsBroadcast:         false,
		IsReadOnly:          false,
		SupportsStreamRead:  false,
		SupportsStreamWrite: false,
	}
}

// FullPOSIXCapabilities returns capabilities for a fully POSIX-compliant file system
func FullPOSIXCapabilities() Capabilities {
	return Capabilities{
		SupportsRandomWrite: true,
		SupportsTruncate:    true,
		SupportsSync:        true,
		SupportsTouch:       true,
		SupportsFileHandle:  true,
		IsAppendOnly:        false,
		IsReadDestructive:   false,
		IsObjectStore:       false,
		IsBroadcast:         false,
		IsReadOnly:          false,
		SupportsStreamRead:  true,
		SupportsStreamWrite: true,
	}
}
