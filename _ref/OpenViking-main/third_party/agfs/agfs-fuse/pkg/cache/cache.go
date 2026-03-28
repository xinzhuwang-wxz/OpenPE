package cache

import (
	"sync"
	"time"

	agfs "github.com/c4pt0r/agfs/agfs-sdk/go"
)

// entry represents a cache entry with expiration
type entry struct {
	value      interface{}
	expiration time.Time
}

// isExpired checks if the entry has expired
func (e *entry) isExpired() bool {
	return time.Now().After(e.expiration)
}

// Cache is a simple TTL cache
type Cache struct {
	mu      sync.RWMutex
	entries map[string]*entry
	ttl     time.Duration
}

// NewCache creates a new cache with the given TTL
func NewCache(ttl time.Duration) *Cache {
	c := &Cache{
		entries: make(map[string]*entry),
		ttl:     ttl,
	}

	// Start cleanup goroutine
	go c.cleanup()

	return c
}

// Set stores a value in the cache
func (c *Cache) Set(key string, value interface{}) {
	c.mu.Lock()
	defer c.mu.Unlock()

	c.entries[key] = &entry{
		value:      value,
		expiration: time.Now().Add(c.ttl),
	}
}

// Get retrieves a value from the cache
func (c *Cache) Get(key string) (interface{}, bool) {
	c.mu.RLock()
	defer c.mu.RUnlock()

	e, ok := c.entries[key]
	if !ok {
		return nil, false
	}

	if e.isExpired() {
		return nil, false
	}

	return e.value, true
}

// Delete removes a value from the cache
func (c *Cache) Delete(key string) {
	c.mu.Lock()
	defer c.mu.Unlock()

	delete(c.entries, key)
}

// DeletePrefix removes all entries with the given prefix
func (c *Cache) DeletePrefix(prefix string) {
	c.mu.Lock()
	defer c.mu.Unlock()

	for key := range c.entries {
		if len(key) >= len(prefix) && key[:len(prefix)] == prefix {
			delete(c.entries, key)
		}
	}
}

// Clear removes all entries from the cache
func (c *Cache) Clear() {
	c.mu.Lock()
	defer c.mu.Unlock()

	c.entries = make(map[string]*entry)
}

// cleanup periodically removes expired entries
func (c *Cache) cleanup() {
	ticker := time.NewTicker(c.ttl)
	defer ticker.Stop()

	for range ticker.C {
		c.mu.Lock()
		now := time.Now()
		for key, e := range c.entries {
			if now.After(e.expiration) {
				delete(c.entries, key)
			}
		}
		c.mu.Unlock()
	}
}

// MetadataCache caches file metadata
type MetadataCache struct {
	cache *Cache
}

// NewMetadataCache creates a new metadata cache
func NewMetadataCache(ttl time.Duration) *MetadataCache {
	return &MetadataCache{
		cache: NewCache(ttl),
	}
}

// Get retrieves file info from cache
func (mc *MetadataCache) Get(path string) (*agfs.FileInfo, bool) {
	value, ok := mc.cache.Get(path)
	if !ok {
		return nil, false
	}
	info, ok := value.(*agfs.FileInfo)
	return info, ok
}

// Set stores file info in cache
func (mc *MetadataCache) Set(path string, info *agfs.FileInfo) {
	mc.cache.Set(path, info)
}

// Invalidate removes file info from cache
func (mc *MetadataCache) Invalidate(path string) {
	mc.cache.Delete(path)
}

// InvalidatePrefix invalidates all paths with the given prefix
func (mc *MetadataCache) InvalidatePrefix(prefix string) {
	mc.cache.DeletePrefix(prefix)
}

// Clear clears all cached metadata
func (mc *MetadataCache) Clear() {
	mc.cache.Clear()
}

// DirectoryCache caches directory listings
type DirectoryCache struct {
	cache *Cache
}

// NewDirectoryCache creates a new directory cache
func NewDirectoryCache(ttl time.Duration) *DirectoryCache {
	return &DirectoryCache{
		cache: NewCache(ttl),
	}
}

// Get retrieves directory listing from cache
func (dc *DirectoryCache) Get(path string) ([]agfs.FileInfo, bool) {
	value, ok := dc.cache.Get(path)
	if !ok {
		return nil, false
	}
	files, ok := value.([]agfs.FileInfo)
	return files, ok
}

// Set stores directory listing in cache
func (dc *DirectoryCache) Set(path string, files []agfs.FileInfo) {
	dc.cache.Set(path, files)
}

// Invalidate removes directory listing from cache
func (dc *DirectoryCache) Invalidate(path string) {
	dc.cache.Delete(path)
}

// InvalidatePrefix invalidates all directories with the given prefix
func (dc *DirectoryCache) InvalidatePrefix(prefix string) {
	dc.cache.DeletePrefix(prefix)
}

// Clear clears all cached directories
func (dc *DirectoryCache) Clear() {
	dc.cache.Clear()
}
