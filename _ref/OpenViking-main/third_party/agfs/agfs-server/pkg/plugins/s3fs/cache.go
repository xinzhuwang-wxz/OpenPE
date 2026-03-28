package s3fs

import (
	"container/list"
	"sync"
	"time"

	"github.com/c4pt0r/agfs/agfs-server/pkg/filesystem"
)

// DirCacheEntry represents a cached directory listing
type DirCacheEntry struct {
	Files   []filesystem.FileInfo
	ModTime time.Time
}

// StatCacheEntry represents a cached stat result
type StatCacheEntry struct {
	Info    *filesystem.FileInfo
	ModTime time.Time
}

// ListDirCache implements an LRU cache for directory listings
type ListDirCache struct {
	mu        sync.RWMutex
	cache     map[string]*list.Element
	lruList   *list.List
	maxSize   int
	ttl       time.Duration
	enabled   bool
	hitCount  uint64
	missCount uint64
}

// dirCacheItem is the value stored in the LRU list
type dirCacheItem struct {
	path  string
	entry *DirCacheEntry
}

// NewListDirCache creates a new directory listing cache
func NewListDirCache(maxSize int, ttl time.Duration, enabled bool) *ListDirCache {
	if maxSize <= 0 {
		maxSize = 1000
	}
	if ttl <= 0 {
		ttl = 30 * time.Second
	}

	return &ListDirCache{
		cache:   make(map[string]*list.Element),
		lruList: list.New(),
		maxSize: maxSize,
		ttl:     ttl,
		enabled: enabled,
	}
}

// Get retrieves a cached directory listing
func (c *ListDirCache) Get(path string) ([]filesystem.FileInfo, bool) {
	if !c.enabled {
		return nil, false
	}

	c.mu.Lock()
	defer c.mu.Unlock()

	elem, ok := c.cache[path]
	if !ok {
		c.missCount++
		return nil, false
	}

	item := elem.Value.(*dirCacheItem)

	// Check if entry is expired
	if time.Since(item.entry.ModTime) > c.ttl {
		c.lruList.Remove(elem)
		delete(c.cache, path)
		c.missCount++
		return nil, false
	}

	// Move to front (most recently used)
	c.lruList.MoveToFront(elem)
	c.hitCount++

	// Return a copy to prevent external modification
	files := make([]filesystem.FileInfo, len(item.entry.Files))
	copy(files, item.entry.Files)
	return files, true
}

// Put adds a directory listing to the cache
func (c *ListDirCache) Put(path string, files []filesystem.FileInfo) {
	if !c.enabled {
		return
	}

	c.mu.Lock()
	defer c.mu.Unlock()

	// Check if entry already exists
	if elem, ok := c.cache[path]; ok {
		item := elem.Value.(*dirCacheItem)
		item.entry.Files = files
		item.entry.ModTime = time.Now()
		c.lruList.MoveToFront(elem)
		return
	}

	// Create new entry
	entry := &DirCacheEntry{
		Files:   files,
		ModTime: time.Now(),
	}

	item := &dirCacheItem{
		path:  path,
		entry: entry,
	}

	elem := c.lruList.PushFront(item)
	c.cache[path] = elem

	// Evict oldest entry if cache is full
	if c.lruList.Len() > c.maxSize {
		oldest := c.lruList.Back()
		if oldest != nil {
			c.lruList.Remove(oldest)
			oldestItem := oldest.Value.(*dirCacheItem)
			delete(c.cache, oldestItem.path)
		}
	}
}

// Invalidate removes a specific path from the cache
func (c *ListDirCache) Invalidate(path string) {
	if !c.enabled {
		return
	}

	c.mu.Lock()
	defer c.mu.Unlock()

	if elem, ok := c.cache[path]; ok {
		c.lruList.Remove(elem)
		delete(c.cache, path)
	}
}

// InvalidatePrefix removes all paths with the given prefix from cache
func (c *ListDirCache) InvalidatePrefix(prefix string) {
	if !c.enabled {
		return
	}

	c.mu.Lock()
	defer c.mu.Unlock()

	toDelete := make([]string, 0)
	for path := range c.cache {
		if path == prefix || (len(path) > len(prefix) && path[:len(prefix)] == prefix && path[len(prefix)] == '/') {
			toDelete = append(toDelete, path)
		}
	}

	for _, path := range toDelete {
		if elem, ok := c.cache[path]; ok {
			c.lruList.Remove(elem)
			delete(c.cache, path)
		}
	}
}

// Clear removes all entries from the cache
func (c *ListDirCache) Clear() {
	if !c.enabled {
		return
	}

	c.mu.Lock()
	defer c.mu.Unlock()

	c.cache = make(map[string]*list.Element)
	c.lruList = list.New()
}

// StatCache implements an LRU cache for stat results
type StatCache struct {
	mu        sync.RWMutex
	cache     map[string]*list.Element
	lruList   *list.List
	maxSize   int
	ttl       time.Duration
	enabled   bool
	hitCount  uint64
	missCount uint64
}

// statCacheItem is the value stored in the LRU list
type statCacheItem struct {
	path  string
	entry *StatCacheEntry
}

// NewStatCache creates a new stat result cache
func NewStatCache(maxSize int, ttl time.Duration, enabled bool) *StatCache {
	if maxSize <= 0 {
		maxSize = 5000
	}
	if ttl <= 0 {
		ttl = 60 * time.Second
	}

	return &StatCache{
		cache:   make(map[string]*list.Element),
		lruList: list.New(),
		maxSize: maxSize,
		ttl:     ttl,
		enabled: enabled,
	}
}

// Get retrieves a cached stat result
func (c *StatCache) Get(path string) (*filesystem.FileInfo, bool) {
	if !c.enabled {
		return nil, false
	}

	c.mu.Lock()
	defer c.mu.Unlock()

	elem, ok := c.cache[path]
	if !ok {
		c.missCount++
		return nil, false
	}

	item := elem.Value.(*statCacheItem)

	// Check if entry is expired
	if time.Since(item.entry.ModTime) > c.ttl {
		c.lruList.Remove(elem)
		delete(c.cache, path)
		c.missCount++
		return nil, false
	}

	// Move to front
	c.lruList.MoveToFront(elem)
	c.hitCount++

	// Return a copy
	info := *item.entry.Info
	return &info, true
}

// Put adds a stat result to the cache
func (c *StatCache) Put(path string, info *filesystem.FileInfo) {
	if !c.enabled || info == nil {
		return
	}

	c.mu.Lock()
	defer c.mu.Unlock()

	// Check if entry already exists
	if elem, ok := c.cache[path]; ok {
		item := elem.Value.(*statCacheItem)
		item.entry.Info = info
		item.entry.ModTime = time.Now()
		c.lruList.MoveToFront(elem)
		return
	}

	// Create new entry
	entry := &StatCacheEntry{
		Info:    info,
		ModTime: time.Now(),
	}

	item := &statCacheItem{
		path:  path,
		entry: entry,
	}

	elem := c.lruList.PushFront(item)
	c.cache[path] = elem

	// Evict oldest entry if cache is full
	if c.lruList.Len() > c.maxSize {
		oldest := c.lruList.Back()
		if oldest != nil {
			c.lruList.Remove(oldest)
			oldestItem := oldest.Value.(*statCacheItem)
			delete(c.cache, oldestItem.path)
		}
	}
}

// Invalidate removes a specific path from the cache
func (c *StatCache) Invalidate(path string) {
	if !c.enabled {
		return
	}

	c.mu.Lock()
	defer c.mu.Unlock()

	if elem, ok := c.cache[path]; ok {
		c.lruList.Remove(elem)
		delete(c.cache, path)
	}
}

// InvalidatePrefix removes all paths with the given prefix from cache
func (c *StatCache) InvalidatePrefix(prefix string) {
	if !c.enabled {
		return
	}

	c.mu.Lock()
	defer c.mu.Unlock()

	toDelete := make([]string, 0)
	for path := range c.cache {
		if path == prefix || (len(path) > len(prefix) && path[:len(prefix)] == prefix && path[len(prefix)] == '/') {
			toDelete = append(toDelete, path)
		}
	}

	for _, path := range toDelete {
		if elem, ok := c.cache[path]; ok {
			c.lruList.Remove(elem)
			delete(c.cache, path)
		}
	}
}

// Clear removes all entries from the cache
func (c *StatCache) Clear() {
	if !c.enabled {
		return
	}

	c.mu.Lock()
	defer c.mu.Unlock()

	c.cache = make(map[string]*list.Element)
	c.lruList = list.New()
}
