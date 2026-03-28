package filesystem

import (
	"io"
	"time"
)

// WriteFlag defines write behavior flags (similar to POSIX open flags)
type WriteFlag uint32

const (
	// WriteFlagNone is the default behavior: overwrite the file
	WriteFlagNone WriteFlag = 0

	// WriteFlagAppend appends data to the end of the file (ignores offset)
	WriteFlagAppend WriteFlag = 1 << 0

	// WriteFlagCreate creates the file if it doesn't exist
	WriteFlagCreate WriteFlag = 1 << 1

	// WriteFlagExclusive fails if the file already exists (used with WriteFlagCreate)
	WriteFlagExclusive WriteFlag = 1 << 2

	// WriteFlagTruncate truncates the file before writing
	WriteFlagTruncate WriteFlag = 1 << 3

	// WriteFlagSync syncs the file after writing (fsync)
	WriteFlagSync WriteFlag = 1 << 4
)

// OpenFlag defines file open flags (similar to os.O_* flags)
type OpenFlag int

const (
	O_RDONLY OpenFlag = 0
	O_WRONLY OpenFlag = 1
	O_RDWR   OpenFlag = 2
	O_APPEND OpenFlag = 1 << 3
	O_CREATE OpenFlag = 1 << 4
	O_EXCL   OpenFlag = 1 << 5
	O_TRUNC  OpenFlag = 1 << 6
)

// MetaData represents structured metadata for files and directories
type MetaData struct {
	Name    string            // Plugin name or identifier
	Type    string            // Type classification of the file/directory
	Content map[string]string // Additional extensible metadata
}

// FileInfo represents file metadata similar to os.FileInfo
type FileInfo struct {
	Name    string
	Size    int64
	Mode    uint32
	ModTime time.Time
	IsDir   bool
	Meta    MetaData // Structured metadata for additional information
}

// FileSystem defines the interface for a POSIX-like file system
type FileSystem interface {
	// Create creates a new file
	Create(path string) error

	// Mkdir creates a new directory
	Mkdir(path string, perm uint32) error

	// Remove removes a file or empty directory
	Remove(path string) error

	// RemoveAll removes a path and any children it contains
	RemoveAll(path string) error

	// Read reads file content with optional offset and size
	// offset: starting position (0 means from beginning)
	// size: number of bytes to read (-1 means read all)
	// Returns io.EOF if offset+size >= file size (reached end of file)
	Read(path string, offset int64, size int64) ([]byte, error)

	// Write writes data to a file with optional offset and flags
	// offset: write position (-1 means overwrite or append depending on flags)
	// flags: WriteFlag bits controlling behavior (create, truncate, append, sync)
	// Returns: number of bytes written and error
	Write(path string, data []byte, offset int64, flags WriteFlag) (int64, error)

	// ReadDir lists the contents of a directory
	ReadDir(path string) ([]FileInfo, error)

	// Stat returns file information
	Stat(path string) (*FileInfo, error)

	// Rename renames/moves a file or directory
	Rename(oldPath, newPath string) error

	// Chmod changes file permissions
	Chmod(path string, mode uint32) error

	// Open opens a file for reading
	Open(path string) (io.ReadCloser, error)

	// OpenWrite opens a file for writing
	OpenWrite(path string) (io.WriteCloser, error)
}

// StreamReader represents a readable stream with support for chunked reads
// This interface is used by streaming file systems (e.g., streamfs) to provide
// real-time data streaming with fanout capability
type StreamReader interface {
	// ReadChunk reads the next chunk of data with a timeout
	// Returns (data, isEOF, error)
	// - data: the chunk data (may be nil if timeout or EOF)
	// - isEOF: true if stream is closed/ended
	// - error: io.EOF for normal stream end, "read timeout" for timeout, or other errors
	ReadChunk(timeout time.Duration) ([]byte, bool, error)

	// Close closes this reader and releases associated resources
	Close() error
}

// Streamer is implemented by file systems that support streaming reads
// Streaming allows multiple readers to consume data in real-time as it's written
type Streamer interface {
	// OpenStream opens a stream for reading
	// Returns a StreamReader that can read chunks progressively
	// Multiple readers can open the same stream for fanout/broadcast scenarios
	OpenStream(path string) (StreamReader, error)
}

// Toucher is implemented by file systems that support efficient touch operations
// Touch updates the modification time without reading/writing the entire file content
type Toucher interface {
	// Touch updates the modification time of a file
	// If the file doesn't exist, it should be created as an empty file
	// Returns error if the operation fails
	Touch(path string) error
}
