package filesystem

// FileHandle represents an open file handle with stateful operations
// This interface is used for FUSE-like operations that require maintaining
// file position and state across multiple read/write operations
type FileHandle interface {
	// ID returns the unique identifier of this handle (used for REST API)
	ID() int64

	// Path returns the file path this handle is associated with
	Path() string

	// Read reads up to len(buf) bytes from the current position
	Read(buf []byte) (int, error)

	// ReadAt reads len(buf) bytes from the specified offset (pread)
	ReadAt(buf []byte, offset int64) (int, error)

	// Write writes data at the current position
	Write(data []byte) (int, error)

	// WriteAt writes data at the specified offset (pwrite)
	WriteAt(data []byte, offset int64) (int, error)

	// Seek moves the read/write position
	// whence: 0 = SEEK_SET (from start), 1 = SEEK_CUR (from current), 2 = SEEK_END (from end)
	Seek(offset int64, whence int) (int64, error)

	// Sync synchronizes the file data to storage
	Sync() error

	// Close closes the handle and releases resources
	Close() error

	// Stat returns file information
	Stat() (*FileInfo, error)

	// Flags returns the open flags used when opening this handle
	Flags() OpenFlag
}

// HandleFS is implemented by file systems that support stateful file handles
// This is optional - file systems that don't support handles can still work
// with the basic FileSystem interface
type HandleFS interface {
	FileSystem

	// OpenHandle opens a file and returns a handle for stateful operations
	// flags: OpenFlag bits (O_RDONLY, O_WRONLY, O_RDWR, O_APPEND, O_CREATE, O_EXCL, O_TRUNC)
	// mode: file permission mode (used when creating new files)
	OpenHandle(path string, flags OpenFlag, mode uint32) (FileHandle, error)

	// GetHandle retrieves an existing handle by its ID
	// Returns ErrNotFound if the handle doesn't exist or has expired
	GetHandle(id int64) (FileHandle, error)

	// CloseHandle closes a handle by its ID
	// This is equivalent to calling handle.Close() but can be used when
	// only the ID is available (e.g., from REST API)
	CloseHandle(id int64) error
}
