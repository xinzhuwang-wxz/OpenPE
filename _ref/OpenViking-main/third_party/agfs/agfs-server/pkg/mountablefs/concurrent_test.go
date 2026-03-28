package mountablefs

import (
	"sync"
	"testing"

	"github.com/c4pt0r/agfs/agfs-server/pkg/filesystem"
	"github.com/c4pt0r/agfs/agfs-server/pkg/plugin/api"
	"github.com/c4pt0r/agfs/agfs-server/pkg/plugins/memfs"
)

// TestConcurrentHandleIDUniqueness tests that handle IDs are unique
// even under heavy concurrent load
func TestConcurrentHandleIDUniqueness(t *testing.T) {
	mfs := NewMountableFS(api.PoolConfig{})

	// Create and mount a single memfs instance
	plugin := memfs.NewMemFSPlugin()
	err := plugin.Initialize(map[string]interface{}{})
	if err != nil {
		t.Fatalf("Failed to initialize plugin: %v", err)
	}

	err = mfs.Mount("/fs", plugin)
	if err != nil {
		t.Fatalf("Failed to mount fs: %v", err)
	}

	// Get the underlying MemoryFS
	fs := plugin.GetFileSystem().(*memfs.MemoryFS)

	// Create multiple files for concurrent access
	numFiles := 10
	for i := 0; i < numFiles; i++ {
		err = fs.Create("/file" + string(rune('0'+i)) + ".txt")
		if err != nil {
			t.Fatalf("Failed to create file %d: %v", i, err)
		}
	}

	// Concurrently open many handles
	numGoroutines := 100
	handlesPerGoroutine := 10

	// Collect all generated handle IDs
	var mu sync.Mutex
	allIDs := make([]int64, 0, numGoroutines*handlesPerGoroutine)

	var wg sync.WaitGroup
	wg.Add(numGoroutines)

	for g := 0; g < numGoroutines; g++ {
		go func(goroutineID int) {
			defer wg.Done()

			localIDs := make([]int64, 0, handlesPerGoroutine)

			// Each goroutine opens multiple handles
			for i := 0; i < handlesPerGoroutine; i++ {
				fileIdx := (goroutineID*handlesPerGoroutine + i) % numFiles
				path := "/fs/file" + string(rune('0'+fileIdx)) + ".txt"

				handle, err := mfs.OpenHandle(path, filesystem.O_RDWR, 0644)
				if err != nil {
					t.Errorf("Goroutine %d: Failed to open handle %d: %v", goroutineID, i, err)
					return
				}

				localIDs = append(localIDs, handle.ID())

				// Close the handle immediately to test close/reopen scenarios
				// Note: ID should NOT be reused
				if i%2 == 0 {
					handle.Close()
				}
			}

			// Add to global collection
			mu.Lock()
			allIDs = append(allIDs, localIDs...)
			mu.Unlock()
		}(g)
	}

	wg.Wait()

	// Verify all IDs are unique
	expectedCount := numGoroutines * handlesPerGoroutine
	if len(allIDs) != expectedCount {
		t.Errorf("Expected %d handle IDs, got %d", expectedCount, len(allIDs))
	}

	// Check for duplicates
	idSet := make(map[int64]bool)
	duplicates := make([]int64, 0)

	for _, id := range allIDs {
		if idSet[id] {
			duplicates = append(duplicates, id)
		}
		idSet[id] = true
	}

	if len(duplicates) > 0 {
		t.Errorf("Found %d duplicate handle IDs: %v", len(duplicates), duplicates)
	}

	// Verify IDs are in expected range [1, expectedCount]
	for id := range idSet {
		if id < 1 || id > int64(expectedCount) {
			t.Errorf("Handle ID %d is out of expected range [1, %d]", id, expectedCount)
		}
	}

	t.Logf("Successfully generated %d unique handle IDs concurrently", len(allIDs))
	t.Logf("ID range: [%d, %d]", 1, expectedCount)
}

// TestHandleIDNeverReused tests that closed handle IDs are never reused
func TestHandleIDNeverReused(t *testing.T) {
	mfs := NewMountableFS(api.PoolConfig{})

	plugin := memfs.NewMemFSPlugin()
	err := plugin.Initialize(map[string]interface{}{})
	if err != nil {
		t.Fatalf("Failed to initialize plugin: %v", err)
	}

	err = mfs.Mount("/fs", plugin)
	if err != nil {
		t.Fatalf("Failed to mount fs: %v", err)
	}

	fs := plugin.GetFileSystem().(*memfs.MemoryFS)
	err = fs.Create("/test.txt")
	if err != nil {
		t.Fatalf("Failed to create file: %v", err)
	}

	// Open and close handles multiple times
	seenIDs := make(map[int64]bool)
	numIterations := 100

	for i := 0; i < numIterations; i++ {
		handle, err := mfs.OpenHandle("/fs/test.txt", filesystem.O_RDWR, 0644)
		if err != nil {
			t.Fatalf("Iteration %d: Failed to open handle: %v", i, err)
		}

		id := handle.ID()

		// Check that this ID has never been seen before
		if seenIDs[id] {
			t.Fatalf("Handle ID %d was reused on iteration %d!", id, i)
		}
		seenIDs[id] = true

		// Close the handle
		err = handle.Close()
		if err != nil {
			t.Fatalf("Iteration %d: Failed to close handle: %v", i, err)
		}
	}

	// Verify we got a strictly increasing sequence
	expectedIDs := make([]int64, numIterations)
	for i := 0; i < numIterations; i++ {
		expectedIDs[i] = int64(i + 1)
	}

	for _, expectedID := range expectedIDs {
		if !seenIDs[expectedID] {
			t.Errorf("Expected to see handle ID %d, but it was not generated", expectedID)
		}
	}

	t.Logf("Successfully verified that %d sequential handle IDs were never reused", numIterations)
}

// TestMultipleMountsHandleIDUniqueness tests handle ID uniqueness across multiple mounts
func TestMultipleMountsHandleIDUniqueness(t *testing.T) {
	mfs := NewMountableFS(api.PoolConfig{})

	// Create and mount multiple memfs instances
	numMounts := 10
	plugins := make([]filesystem.FileSystem, numMounts)

	for i := 0; i < numMounts; i++ {
		plugin := memfs.NewMemFSPlugin()
		err := plugin.Initialize(map[string]interface{}{})
		if err != nil {
			t.Fatalf("Failed to initialize plugin %d: %v", i, err)
		}

		mountPath := "/fs" + string(rune('0'+i))
		err = mfs.Mount(mountPath, plugin)
		if err != nil {
			t.Fatalf("Failed to mount fs%d: %v", i, err)
		}

		fs := plugin.GetFileSystem().(*memfs.MemoryFS)
		err = fs.Create("/test.txt")
		if err != nil {
			t.Fatalf("Failed to create file in fs%d: %v", i, err)
		}

		plugins[i] = fs
	}

	// Open handles from all mounts concurrently
	var wg sync.WaitGroup
	var mu sync.Mutex
	allIDs := make([]int64, 0, numMounts*10)

	for i := 0; i < numMounts; i++ {
		wg.Add(1)
		go func(mountIdx int) {
			defer wg.Done()

			mountPath := "/fs" + string(rune('0'+mountIdx))

			// Open 10 handles from this mount
			for j := 0; j < 10; j++ {
				handle, err := mfs.OpenHandle(mountPath+"/test.txt", filesystem.O_RDWR, 0644)
				if err != nil {
					t.Errorf("Mount %d: Failed to open handle %d: %v", mountIdx, j, err)
					return
				}

				mu.Lock()
				allIDs = append(allIDs, handle.ID())
				mu.Unlock()

				// Keep some handles open, close others
				if j%3 == 0 {
					handle.Close()
				}
			}
		}(i)
	}

	wg.Wait()

	// Verify all IDs are unique
	idSet := make(map[int64]bool)
	for _, id := range allIDs {
		if idSet[id] {
			t.Errorf("Duplicate handle ID found: %d", id)
		}
		idSet[id] = true
	}

	t.Logf("Generated %d unique handle IDs across %d mounts", len(allIDs), numMounts)
}
