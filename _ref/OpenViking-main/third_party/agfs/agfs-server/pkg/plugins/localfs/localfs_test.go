package localfs

import (
	"bytes"
	"io"
	"os"
	"path/filepath"
	"testing"

	"github.com/c4pt0r/agfs/agfs-server/pkg/filesystem"
)

// readIgnoreEOF reads file content, ignoring io.EOF which is expected at end of file
func readIgnoreEOF(fs *LocalFS, path string) ([]byte, error) {
	content, err := fs.Read(path, 0, -1)
	if err == io.EOF {
		return content, nil
	}
	return content, err
}

func setupTestDir(t *testing.T) (string, func()) {
	t.Helper()
	dir, err := os.MkdirTemp("", "localfs-test-*")
	if err != nil {
		t.Fatalf("Failed to create temp dir: %v", err)
	}
	return dir, func() {
		os.RemoveAll(dir)
	}
}

func newTestFS(t *testing.T, dir string) *LocalFS {
	t.Helper()
	fs, err := NewLocalFS(dir)
	if err != nil {
		t.Fatalf("NewLocalFS failed: %v", err)
	}
	return fs
}

func TestLocalFSCreate(t *testing.T) {
	dir, cleanup := setupTestDir(t)
	defer cleanup()

	fs := newTestFS(t, dir)

	// Create a file
	err := fs.Create("/test.txt")
	if err != nil {
		t.Fatalf("Create failed: %v", err)
	}

	// Verify file exists
	info, err := fs.Stat("/test.txt")
	if err != nil {
		t.Fatalf("Stat failed: %v", err)
	}
	if info.IsDir {
		t.Error("Expected file, got directory")
	}
	if info.Size != 0 {
		t.Errorf("Expected size 0, got %d", info.Size)
	}

	// Verify on disk
	_, err = os.Stat(filepath.Join(dir, "test.txt"))
	if err != nil {
		t.Fatalf("File not created on disk: %v", err)
	}
}

func TestLocalFSWriteBasic(t *testing.T) {
	dir, cleanup := setupTestDir(t)
	defer cleanup()

	fs := newTestFS(t, dir)
	path := "/test.txt"

	// Write with create flag
	data := []byte("Hello, World!")
	n, err := fs.Write(path, data, -1, filesystem.WriteFlagCreate|filesystem.WriteFlagTruncate)
	if err != nil {
		t.Fatalf("Write failed: %v", err)
	}
	if n != int64(len(data)) {
		t.Errorf("Write returned %d, want %d", n, len(data))
	}

	// Read back
	content, err := readIgnoreEOF(fs, path)
	if err != nil {
		t.Fatalf("Read failed: %v", err)
	}
	if !bytes.Equal(content, data) {
		t.Errorf("Read content mismatch: got %q, want %q", content, data)
	}
}

func TestLocalFSWriteWithOffset(t *testing.T) {
	dir, cleanup := setupTestDir(t)
	defer cleanup()

	fs := newTestFS(t, dir)
	path := "/test.txt"

	// Create file with initial content
	_, err := fs.Write(path, []byte("Hello, World!"), -1, filesystem.WriteFlagCreate)
	if err != nil {
		t.Fatalf("Initial write failed: %v", err)
	}

	// Write at offset (pwrite-style)
	_, err = fs.Write(path, []byte("XXXXX"), 7, filesystem.WriteFlagNone)
	if err != nil {
		t.Fatalf("Write at offset failed: %v", err)
	}

	// Read back
	content, err := readIgnoreEOF(fs, path)
	if err != nil {
		t.Fatalf("Read failed: %v", err)
	}
	expected := "Hello, XXXXX!"
	if string(content) != expected {
		t.Errorf("Content mismatch: got %q, want %q", string(content), expected)
	}
}

func TestLocalFSWriteExtend(t *testing.T) {
	dir, cleanup := setupTestDir(t)
	defer cleanup()

	fs := newTestFS(t, dir)
	path := "/test.txt"

	// Create file with initial content
	_, err := fs.Write(path, []byte("Hello"), -1, filesystem.WriteFlagCreate)
	if err != nil {
		t.Fatalf("Initial write failed: %v", err)
	}

	// Write at offset beyond file size (should extend with zeros)
	_, err = fs.Write(path, []byte("World"), 10, filesystem.WriteFlagNone)
	if err != nil {
		t.Fatalf("Write at extended offset failed: %v", err)
	}

	// Read back
	content, err := readIgnoreEOF(fs, path)
	if err != nil {
		t.Fatalf("Read failed: %v", err)
	}
	if len(content) != 15 {
		t.Errorf("Expected length 15, got %d", len(content))
	}
	// Check beginning and end
	if string(content[:5]) != "Hello" {
		t.Errorf("Beginning mismatch: got %q", string(content[:5]))
	}
	if string(content[10:]) != "World" {
		t.Errorf("End mismatch: got %q", string(content[10:]))
	}
	// Middle should be zeros
	for i := 5; i < 10; i++ {
		if content[i] != 0 {
			t.Errorf("Expected zero at position %d, got %d", i, content[i])
		}
	}
}

func TestLocalFSWriteAppend(t *testing.T) {
	dir, cleanup := setupTestDir(t)
	defer cleanup()

	fs := newTestFS(t, dir)
	path := "/test.txt"

	// Create file with initial content
	_, err := fs.Write(path, []byte("Hello"), -1, filesystem.WriteFlagCreate)
	if err != nil {
		t.Fatalf("Initial write failed: %v", err)
	}

	// Append data
	_, err = fs.Write(path, []byte(", World!"), 0, filesystem.WriteFlagAppend)
	if err != nil {
		t.Fatalf("Append failed: %v", err)
	}

	// Read back
	content, err := readIgnoreEOF(fs, path)
	if err != nil {
		t.Fatalf("Read failed: %v", err)
	}
	expected := "Hello, World!"
	if string(content) != expected {
		t.Errorf("Content mismatch: got %q, want %q", string(content), expected)
	}
}

func TestLocalFSWriteTruncate(t *testing.T) {
	dir, cleanup := setupTestDir(t)
	defer cleanup()

	fs := newTestFS(t, dir)
	path := "/test.txt"

	// Create file with initial content
	_, err := fs.Write(path, []byte("Hello, World!"), -1, filesystem.WriteFlagCreate)
	if err != nil {
		t.Fatalf("Initial write failed: %v", err)
	}

	// Write with truncate
	_, err = fs.Write(path, []byte("Hi"), -1, filesystem.WriteFlagTruncate)
	if err != nil {
		t.Fatalf("Truncate write failed: %v", err)
	}

	// Read back
	content, err := readIgnoreEOF(fs, path)
	if err != nil {
		t.Fatalf("Read failed: %v", err)
	}
	if string(content) != "Hi" {
		t.Errorf("Content mismatch: got %q, want %q", string(content), "Hi")
	}
}

func TestLocalFSWriteCreateExclusive(t *testing.T) {
	dir, cleanup := setupTestDir(t)
	defer cleanup()

	fs := newTestFS(t, dir)
	path := "/test.txt"

	// Create new file with exclusive flag
	_, err := fs.Write(path, []byte("Hello"), -1, filesystem.WriteFlagCreate|filesystem.WriteFlagExclusive)
	if err != nil {
		t.Fatalf("Exclusive create failed: %v", err)
	}

	// Second exclusive create should fail
	_, err = fs.Write(path, []byte("World"), -1, filesystem.WriteFlagCreate|filesystem.WriteFlagExclusive)
	if err == nil {
		t.Error("Expected error for exclusive create on existing file")
	}
}

func TestLocalFSWriteNonExistent(t *testing.T) {
	dir, cleanup := setupTestDir(t)
	defer cleanup()

	fs := newTestFS(t, dir)
	path := "/nonexistent.txt"

	// Write to non-existent file with offset (no default create behavior) should fail
	// Note: LocalFS has backward compatibility: flags==None && offset<0 auto-creates
	_, err := fs.Write(path, []byte("Hello"), 0, filesystem.WriteFlagNone)
	if err == nil {
		t.Error("Expected error for writing to non-existent file without create flag")
	}

	// Write with create flag should succeed
	_, err = fs.Write(path, []byte("Hello"), -1, filesystem.WriteFlagCreate)
	if err != nil {
		t.Fatalf("Write with create flag failed: %v", err)
	}
}

func TestLocalFSReadWithOffset(t *testing.T) {
	dir, cleanup := setupTestDir(t)
	defer cleanup()

	fs := newTestFS(t, dir)
	path := "/test.txt"

	data := []byte("Hello, World!")
	_, err := fs.Write(path, data, -1, filesystem.WriteFlagCreate)
	if err != nil {
		t.Fatalf("Write failed: %v", err)
	}

	// Read from offset
	content, err := fs.Read(path, 7, 5)
	if err != nil && err != io.EOF {
		t.Fatalf("Read with offset failed: %v", err)
	}
	if string(content) != "World" {
		t.Errorf("Read content mismatch: got %q, want %q", string(content), "World")
	}

	// Read all from offset
	content, err = fs.Read(path, 7, -1)
	if err != nil && err != io.EOF {
		t.Fatalf("Read all from offset failed: %v", err)
	}
	if string(content) != "World!" {
		t.Errorf("Read content mismatch: got %q, want %q", string(content), "World!")
	}
}

func TestLocalFSMkdir(t *testing.T) {
	dir, cleanup := setupTestDir(t)
	defer cleanup()

	fs := newTestFS(t, dir)

	// Create directory
	err := fs.Mkdir("/testdir", 0755)
	if err != nil {
		t.Fatalf("Mkdir failed: %v", err)
	}

	// Verify directory exists
	info, err := fs.Stat("/testdir")
	if err != nil {
		t.Fatalf("Stat failed: %v", err)
	}
	if !info.IsDir {
		t.Error("Expected directory, got file")
	}

	// Verify on disk
	diskInfo, err := os.Stat(filepath.Join(dir, "testdir"))
	if err != nil {
		t.Fatalf("Directory not created on disk: %v", err)
	}
	if !diskInfo.IsDir() {
		t.Error("Disk entry is not a directory")
	}
}

func TestLocalFSRemove(t *testing.T) {
	dir, cleanup := setupTestDir(t)
	defer cleanup()

	fs := newTestFS(t, dir)

	// Create and remove file
	err := fs.Create("/test.txt")
	if err != nil {
		t.Fatalf("Create failed: %v", err)
	}

	err = fs.Remove("/test.txt")
	if err != nil {
		t.Fatalf("Remove failed: %v", err)
	}

	// Verify file is removed
	_, err = fs.Stat("/test.txt")
	if err == nil {
		t.Error("Expected error for removed file")
	}

	// Verify on disk
	_, err = os.Stat(filepath.Join(dir, "test.txt"))
	if !os.IsNotExist(err) {
		t.Error("File should not exist on disk")
	}
}

func TestLocalFSRename(t *testing.T) {
	dir, cleanup := setupTestDir(t)
	defer cleanup()

	fs := newTestFS(t, dir)

	// Create file
	data := []byte("Hello, World!")
	_, err := fs.Write("/old.txt", data, -1, filesystem.WriteFlagCreate)
	if err != nil {
		t.Fatalf("Write failed: %v", err)
	}

	// Rename
	err = fs.Rename("/old.txt", "/new.txt")
	if err != nil {
		t.Fatalf("Rename failed: %v", err)
	}

	// Verify old path doesn't exist
	_, err = fs.Stat("/old.txt")
	if err == nil {
		t.Error("Old path should not exist")
	}

	// Verify new path exists with same content
	content, err := fs.Read("/new.txt", 0, -1)
	if err != nil && err != io.EOF {
		t.Fatalf("Read new path failed: %v", err)
	}
	if !bytes.Equal(content, data) {
		t.Errorf("Content mismatch after rename")
	}
}

func TestLocalFSReadDir(t *testing.T) {
	dir, cleanup := setupTestDir(t)
	defer cleanup()

	fs := newTestFS(t, dir)

	// Create some files and directories
	fs.Mkdir("/dir1", 0755)
	fs.Create("/file1.txt")
	fs.Create("/file2.txt")

	// Read root directory
	infos, err := fs.ReadDir("/")
	if err != nil {
		t.Fatalf("ReadDir failed: %v", err)
	}

	if len(infos) != 3 {
		t.Errorf("Expected 3 entries, got %d", len(infos))
	}

	// Verify entries
	names := make(map[string]bool)
	for _, info := range infos {
		names[info.Name] = true
	}

	if !names["dir1"] || !names["file1.txt"] || !names["file2.txt"] {
		t.Errorf("Missing expected entries: %v", names)
	}
}

func TestLocalFSChmod(t *testing.T) {
	dir, cleanup := setupTestDir(t)
	defer cleanup()

	fs := newTestFS(t, dir)

	// Create file
	fs.Create("/test.txt")

	// Change mode
	err := fs.Chmod("/test.txt", 0600)
	if err != nil {
		t.Fatalf("Chmod failed: %v", err)
	}

	// Verify mode on disk
	diskInfo, err := os.Stat(filepath.Join(dir, "test.txt"))
	if err != nil {
		t.Fatalf("Stat failed: %v", err)
	}
	// Only check user permission bits (platform differences)
	if diskInfo.Mode().Perm()&0700 != 0600 {
		t.Errorf("Mode mismatch: got %o", diskInfo.Mode().Perm())
	}
}

// Note: Truncate, WriteAt, Sync, GetCapabilities, and Touch are optional extension interfaces
// LocalFS may or may not implement them. These tests are skipped for now.

func TestLocalFSOpenWrite(t *testing.T) {
	dir, cleanup := setupTestDir(t)
	defer cleanup()

	fs := newTestFS(t, dir)

	// Create file
	fs.Create("/test.txt")

	// Open for writing
	w, err := fs.OpenWrite("/test.txt")
	if err != nil {
		t.Fatalf("OpenWrite failed: %v", err)
	}

	// Write through the writer
	data := []byte("Hello, World!")
	n, err := w.Write(data)
	if err != nil {
		t.Fatalf("Writer.Write failed: %v", err)
	}
	if n != len(data) {
		t.Errorf("Write returned %d, want %d", n, len(data))
	}

	// Close the writer
	err = w.Close()
	if err != nil {
		t.Fatalf("Writer.Close failed: %v", err)
	}

	// Verify content
	content, err := fs.Read("/test.txt", 0, -1)
	if err != nil && err != io.EOF {
		t.Fatalf("Read failed: %v", err)
	}
	if !bytes.Equal(content, data) {
		t.Errorf("Content mismatch: got %q, want %q", content, data)
	}
}

func TestLocalFSOpen(t *testing.T) {
	dir, cleanup := setupTestDir(t)
	defer cleanup()

	fs := newTestFS(t, dir)

	// Create file with content
	data := []byte("Hello, World!")
	_, err := fs.Write("/test.txt", data, -1, filesystem.WriteFlagCreate)
	if err != nil {
		t.Fatalf("Write failed: %v", err)
	}

	// Open for reading
	r, err := fs.Open("/test.txt")
	if err != nil {
		t.Fatalf("Open failed: %v", err)
	}

	// Read through the reader
	buf := make([]byte, 100)
	n, err := r.Read(buf)
	if err != nil {
		t.Fatalf("Reader.Read failed: %v", err)
	}
	if n != len(data) {
		t.Errorf("Read returned %d, want %d", n, len(data))
	}
	if !bytes.Equal(buf[:n], data) {
		t.Errorf("Content mismatch: got %q, want %q", buf[:n], data)
	}

	// Close
	err = r.Close()
	if err != nil {
		t.Fatalf("Reader.Close failed: %v", err)
	}
}

func TestLocalFSRemoveAll(t *testing.T) {
	dir, cleanup := setupTestDir(t)
	defer cleanup()

	fs := newTestFS(t, dir)

	// Create nested structure
	fs.Mkdir("/testdir", 0755)
	fs.Mkdir("/testdir/subdir", 0755)
	fs.Create("/testdir/file1.txt")
	fs.Create("/testdir/subdir/file2.txt")

	// RemoveAll
	err := fs.RemoveAll("/testdir")
	if err != nil {
		t.Fatalf("RemoveAll failed: %v", err)
	}

	// Verify removed
	_, err = fs.Stat("/testdir")
	if err == nil {
		t.Error("Directory should be removed")
	}
}
