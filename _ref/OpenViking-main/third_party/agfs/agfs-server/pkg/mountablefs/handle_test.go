package mountablefs

import (
	"testing"

	"github.com/c4pt0r/agfs/agfs-server/pkg/filesystem"
	"github.com/c4pt0r/agfs/agfs-server/pkg/plugin/api"
	"github.com/c4pt0r/agfs/agfs-server/pkg/plugins/memfs"
)

// TestGlobalHandleIDUniqueness tests that handle IDs are globally unique
// across multiple mounted plugin instances, even when plugins generate
// conflicting local handle IDs
func TestGlobalHandleIDUniqueness(t *testing.T) {
	// Create MountableFS with multiple MemoryFS instances mounted
	mfs := NewMountableFS(api.PoolConfig{})

	// Create two separate MemFS plugin instances
	// Each will have its own MemoryFS with independent handle ID counters
	plugin1 := memfs.NewMemFSPlugin()
	plugin2 := memfs.NewMemFSPlugin()

	// Initialize them
	err := plugin1.Initialize(map[string]interface{}{})
	if err != nil {
		t.Fatalf("Failed to initialize plugin1: %v", err)
	}
	err = plugin2.Initialize(map[string]interface{}{})
	if err != nil {
		t.Fatalf("Failed to initialize plugin2: %v", err)
	}

	// Get the underlying MemoryFS instances
	memfs1 := plugin1.GetFileSystem().(*memfs.MemoryFS)
	memfs2 := plugin2.GetFileSystem().(*memfs.MemoryFS)

	// Mount at different paths
	err = mfs.Mount("/fs1", plugin1)
	if err != nil {
		t.Fatalf("Failed to mount fs1: %v", err)
	}

	err = mfs.Mount("/fs2", plugin2)
	if err != nil {
		t.Fatalf("Failed to mount fs2: %v", err)
	}

	// Create files in both filesystems
	err = memfs1.Create("/test1.txt")
	if err != nil {
		t.Fatalf("Failed to create file in fs1: %v", err)
	}

	err = memfs2.Create("/test2.txt")
	if err != nil {
		t.Fatalf("Failed to create file in fs2: %v", err)
	}

	// Open handles in both filesystems
	// Both underlying filesystems will generate local handle ID = 1
	handle1, err := mfs.OpenHandle("/fs1/test1.txt", filesystem.O_RDWR, 0644)
	if err != nil {
		t.Fatalf("Failed to open handle in fs1: %v", err)
	}
	defer handle1.Close()

	handle2, err := mfs.OpenHandle("/fs2/test2.txt", filesystem.O_RDWR, 0644)
	if err != nil {
		t.Fatalf("Failed to open handle in fs2: %v", err)
	}
	defer handle2.Close()

	// Verify that the global IDs are different
	id1 := handle1.ID()
	id2 := handle2.ID()

	if id1 == id2 {
		t.Errorf("Handle IDs should be globally unique, but both are %d", id1)
	}

	t.Logf("Handle 1 global ID: %d, Handle 2 global ID: %d", id1, id2)

	// Verify we can retrieve handles by their global IDs
	retrieved1, err := mfs.GetHandle(id1)
	if err != nil {
		t.Fatalf("Failed to retrieve handle 1: %v", err)
	}
	if retrieved1.ID() != id1 {
		t.Errorf("Retrieved handle 1 has wrong ID: expected %d, got %d", id1, retrieved1.ID())
	}

	retrieved2, err := mfs.GetHandle(id2)
	if err != nil {
		t.Fatalf("Failed to retrieve handle 2: %v", err)
	}
	if retrieved2.ID() != id2 {
		t.Errorf("Retrieved handle 2 has wrong ID: expected %d, got %d", id2, retrieved2.ID())
	}

	// Verify paths are correct
	if retrieved1.Path() != "/fs1/test1.txt" {
		t.Errorf("Handle 1 path incorrect: expected /fs1/test1.txt, got %s", retrieved1.Path())
	}
	if retrieved2.Path() != "/fs2/test2.txt" {
		t.Errorf("Handle 2 path incorrect: expected /fs2/test2.txt, got %s", retrieved2.Path())
	}

	// Test that we can write and read through the handles
	testData1 := []byte("data from fs1")
	n, err := handle1.Write(testData1)
	if err != nil {
		t.Fatalf("Failed to write to handle 1: %v", err)
	}
	if n != len(testData1) {
		t.Errorf("Write to handle 1: expected %d bytes, wrote %d", len(testData1), n)
	}

	testData2 := []byte("data from fs2")
	n, err = handle2.Write(testData2)
	if err != nil {
		t.Fatalf("Failed to write to handle 2: %v", err)
	}
	if n != len(testData2) {
		t.Errorf("Write to handle 2: expected %d bytes, wrote %d", len(testData2), n)
	}

	// Seek back to beginning
	_, err = handle1.Seek(0, 0)
	if err != nil {
		t.Fatalf("Failed to seek handle 1: %v", err)
	}
	_, err = handle2.Seek(0, 0)
	if err != nil {
		t.Fatalf("Failed to seek handle 2: %v", err)
	}

	// Read back and verify
	buf1 := make([]byte, len(testData1))
	n, err = handle1.Read(buf1)
	if err != nil {
		t.Fatalf("Failed to read from handle 1: %v", err)
	}
	if string(buf1[:n]) != string(testData1) {
		t.Errorf("Read from handle 1: expected %s, got %s", testData1, buf1[:n])
	}

	buf2 := make([]byte, len(testData2))
	n, err = handle2.Read(buf2)
	if err != nil {
		t.Fatalf("Failed to read from handle 2: %v", err)
	}
	if string(buf2[:n]) != string(testData2) {
		t.Errorf("Read from handle 2: expected %s, got %s", testData2, buf2[:n])
	}

	// Close handles
	err = mfs.CloseHandle(id1)
	if err != nil {
		t.Fatalf("Failed to close handle 1: %v", err)
	}

	err = mfs.CloseHandle(id2)
	if err != nil {
		t.Fatalf("Failed to close handle 2: %v", err)
	}

	// Verify handles are no longer accessible
	_, err = mfs.GetHandle(id1)
	if err != filesystem.ErrNotFound {
		t.Errorf("Expected ErrNotFound for closed handle 1, got: %v", err)
	}

	_, err = mfs.GetHandle(id2)
	if err != filesystem.ErrNotFound {
		t.Errorf("Expected ErrNotFound for closed handle 2, got: %v", err)
	}
}

// TestMultipleHandlesSameFile tests opening multiple handles to the same file
func TestMultipleHandlesSameFile(t *testing.T) {
	mfs := NewMountableFS(api.PoolConfig{})

	plugin1 := memfs.NewMemFSPlugin()
	err := plugin1.Initialize(map[string]interface{}{})
	if err != nil {
		t.Fatalf("Failed to initialize plugin: %v", err)
	}

	err = mfs.Mount("/fs", plugin1)
	if err != nil {
		t.Fatalf("Failed to mount fs: %v", err)
	}

	// Get the underlying MemoryFS
	memfs1 := plugin1.GetFileSystem().(*memfs.MemoryFS)

	// Create a file
	err = memfs1.Create("/shared.txt")
	if err != nil {
		t.Fatalf("Failed to create file: %v", err)
	}

	// Open multiple handles to the same file
	handle1, err := mfs.OpenHandle("/fs/shared.txt", filesystem.O_RDWR, 0644)
	if err != nil {
		t.Fatalf("Failed to open handle 1: %v", err)
	}
	defer handle1.Close()

	handle2, err := mfs.OpenHandle("/fs/shared.txt", filesystem.O_RDWR, 0644)
	if err != nil {
		t.Fatalf("Failed to open handle 2: %v", err)
	}
	defer handle2.Close()

	handle3, err := mfs.OpenHandle("/fs/shared.txt", filesystem.O_RDONLY, 0644)
	if err != nil {
		t.Fatalf("Failed to open handle 3: %v", err)
	}
	defer handle3.Close()

	// All handles should have different global IDs
	ids := []int64{handle1.ID(), handle2.ID(), handle3.ID()}
	for i := 0; i < len(ids); i++ {
		for j := i + 1; j < len(ids); j++ {
			if ids[i] == ids[j] {
				t.Errorf("Handles %d and %d have same ID: %d", i, j, ids[i])
			}
		}
	}

	t.Logf("Three handles to same file have IDs: %v", ids)

	// Verify all handles point to the same file
	for i, h := range []filesystem.FileHandle{handle1, handle2, handle3} {
		if h.Path() != "/fs/shared.txt" {
			t.Errorf("Handle %d has wrong path: %s", i, h.Path())
		}
	}
}
