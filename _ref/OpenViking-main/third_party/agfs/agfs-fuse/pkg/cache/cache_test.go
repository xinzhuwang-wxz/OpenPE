package cache

import (
	"testing"
	"time"

	agfs "github.com/c4pt0r/agfs/agfs-sdk/go"
)

func TestCacheBasicOperations(t *testing.T) {
	c := NewCache(100 * time.Millisecond)

	// Test Set and Get
	c.Set("key1", "value1")
	value, ok := c.Get("key1")
	if !ok || value != "value1" {
		t.Errorf("Expected value1, got %v (ok=%v)", value, ok)
	}

	// Test Get non-existent key
	_, ok = c.Get("key2")
	if ok {
		t.Error("Expected key2 to not exist")
	}

	// Test Delete
	c.Delete("key1")
	_, ok = c.Get("key1")
	if ok {
		t.Error("Expected key1 to be deleted")
	}
}

func TestCacheTTL(t *testing.T) {
	c := NewCache(50 * time.Millisecond)

	c.Set("key1", "value1")

	// Should be available immediately
	_, ok := c.Get("key1")
	if !ok {
		t.Error("Expected key1 to exist")
	}

	// Wait for expiration
	time.Sleep(100 * time.Millisecond)

	// Should be expired
	_, ok = c.Get("key1")
	if ok {
		t.Error("Expected key1 to be expired")
	}
}

func TestCacheDeletePrefix(t *testing.T) {
	c := NewCache(1 * time.Second)

	c.Set("/foo/bar", "1")
	c.Set("/foo/baz", "2")
	c.Set("/bar/qux", "3")

	c.DeletePrefix("/foo")

	// /foo/* should be deleted
	_, ok := c.Get("/foo/bar")
	if ok {
		t.Error("Expected /foo/bar to be deleted")
	}
	_, ok = c.Get("/foo/baz")
	if ok {
		t.Error("Expected /foo/baz to be deleted")
	}

	// /bar/qux should still exist
	_, ok = c.Get("/bar/qux")
	if !ok {
		t.Error("Expected /bar/qux to exist")
	}
}

func TestMetadataCache(t *testing.T) {
	mc := NewMetadataCache(1 * time.Second)

	info := &agfs.FileInfo{
		Name:  "test.txt",
		Size:  123,
		IsDir: false,
	}

	// Test Set and Get
	mc.Set("/test.txt", info)
	cached, ok := mc.Get("/test.txt")
	if !ok || cached.Name != "test.txt" || cached.Size != 123 {
		t.Errorf("Expected cached info to match, got %+v (ok=%v)", cached, ok)
	}

	// Test Invalidate
	mc.Invalidate("/test.txt")
	_, ok = mc.Get("/test.txt")
	if ok {
		t.Error("Expected /test.txt to be invalidated")
	}
}

func TestDirectoryCache(t *testing.T) {
	dc := NewDirectoryCache(1 * time.Second)

	files := []agfs.FileInfo{
		{Name: "file1.txt", Size: 100, IsDir: false},
		{Name: "file2.txt", Size: 200, IsDir: false},
	}

	// Test Set and Get
	dc.Set("/dir", files)
	cached, ok := dc.Get("/dir")
	if !ok || len(cached) != 2 {
		t.Errorf("Expected 2 cached files, got %d (ok=%v)", len(cached), ok)
	}

	// Test Invalidate
	dc.Invalidate("/dir")
	_, ok = dc.Get("/dir")
	if ok {
		t.Error("Expected /dir to be invalidated")
	}
}

func TestCacheConcurrency(t *testing.T) {
	c := NewCache(1 * time.Second)

	done := make(chan bool)

	// Writer goroutine
	go func() {
		for i := 0; i < 1000; i++ {
			c.Set("key", i)
		}
		done <- true
	}()

	// Reader goroutine
	go func() {
		for i := 0; i < 1000; i++ {
			c.Get("key")
		}
		done <- true
	}()

	// Wait for both to complete
	<-done
	<-done

	// If we got here without panic, concurrency is safe
}
