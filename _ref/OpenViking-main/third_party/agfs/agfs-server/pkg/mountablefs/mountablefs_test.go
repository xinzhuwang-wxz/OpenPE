package mountablefs

import (
	"testing"

	"github.com/c4pt0r/agfs/agfs-server/pkg/filesystem"
	"github.com/c4pt0r/agfs/agfs-server/pkg/plugin"
	"github.com/c4pt0r/agfs/agfs-server/pkg/plugin/api"
)

// MockPlugin implements plugin.ServicePlugin for testing
type MockPlugin struct {
	name string
}

func (p *MockPlugin) Name() string {
	return p.name
}

func (p *MockPlugin) Validate(cfg map[string]interface{}) error {
	return nil
}

func (p *MockPlugin) Initialize(cfg map[string]interface{}) error {
	return nil
}

func (p *MockPlugin) GetFileSystem() filesystem.FileSystem {
	return nil
}

func (p *MockPlugin) GetReadme() string {
	return "Mock Plugin"
}

func (p *MockPlugin) GetConfigParams() []plugin.ConfigParameter {
	return nil
}

func (p *MockPlugin) Shutdown() error {
	return nil
}

func TestMountableFSRouting(t *testing.T) {
	mfs := NewMountableFS(api.PoolConfig{})

	p1 := &MockPlugin{name: "plugin1"}
	p2 := &MockPlugin{name: "plugin2"}
	pRoot := &MockPlugin{name: "rootPlugin"}

	// Test 1: Basic Mount
	err := mfs.Mount("/data", p1)
	if err != nil {
		t.Fatalf("Failed to mount: %v", err)
	}

	// Test 2: Exact Match
	mount, relPath, found := mfs.findMount("/data")
	if !found {
		t.Errorf("Expected to find mount at /data")
	}
	if mount.Plugin != p1 {
		t.Errorf("Expected plugin1, got %s", mount.Plugin.Name())
	}
	if relPath != "/" {
		t.Errorf("Expected relPath /, got %s", relPath)
	}

	// Test 3: Subpath Match
	mount, relPath, found = mfs.findMount("/data/file.txt")
	if !found {
		t.Errorf("Expected to find mount at /data/file.txt")
	}
	if mount.Plugin != p1 {
		t.Errorf("Expected plugin1, got %s", mount.Plugin.Name())
	}
	if relPath != "/file.txt" {
		t.Errorf("Expected relPath /file.txt, got %s", relPath)
	}

	// Test 4: Partial Match (Should Fail)
	mount, _, found = mfs.findMount("/dataset")
	if found {
		t.Errorf("Should NOT find mount for /dataset (partial match of /data)")
	}

	// Test 5: Nested Mounts / Longest Prefix
	err = mfs.Mount("/data/users", p2)
	if err != nil {
		t.Fatalf("Failed to mount nested: %v", err)
	}

	// /data should still map to p1
	mount, _, found = mfs.findMount("/data/config")
	if !found || mount.Plugin != p1 {
		t.Errorf("Expected /data/config to map to plugin1")
	}

	// /data/users should map to p2
	mount, relPath, found = mfs.findMount("/data/users/alice")
	if !found {
		t.Errorf("Expected to find mount at /data/users/alice")
	}
	if mount.Plugin != p2 {
		t.Errorf("Expected plugin2, got %s", mount.Plugin.Name())
	}
	if relPath != "/alice" {
		t.Errorf("Expected relPath /alice, got %s", relPath)
	}

	// Test 6: Root Mount
	err = mfs.Mount("/", pRoot)
	if err != nil {
		t.Fatalf("Failed to mount root: %v", err)
	}

	// /other should map to root
	mount, relPath, found = mfs.findMount("/other/file")
	if !found {
		t.Errorf("Expected to find mount at /other/file")
	}
	if mount.Plugin != pRoot {
		t.Errorf("Expected rootPlugin, got %s", mount.Plugin.Name())
	}
	if relPath != "/other/file" {
		t.Errorf("Expected relPath /other/file, got %s", relPath)
	}

	// /data/users/alice should still map to p2 (longest match)
	mount, _, found = mfs.findMount("/data/users/alice")
	if !found || mount.Plugin != p2 {
		t.Errorf("Root mount broke specific mount routing")
	}

	// Test 7: Unmount
	err = mfs.Unmount("/data")
	if err != nil {
		t.Fatalf("Failed to unmount: %v", err)
	}

	// /data/file should now fall back to Root because /data is gone
	mount, _, found = mfs.findMount("/data/file")
	if !found {
		t.Errorf("Expected /data/file to be found (fallback to root)")
	}
	if mount.Plugin != pRoot {
		t.Errorf("Expected fallback to rootPlugin, got %s", mount.Plugin.Name())
	}

	// /data/users should still exist
	mount, _, found = mfs.findMount("/data/users/bob")
	if !found || mount.Plugin != p2 {
		t.Errorf("Unmounting parent should not affect child mount")
	}
}
