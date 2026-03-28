package filesystem

import (
	"testing"
)

func TestWriteFlag(t *testing.T) {
	tests := []struct {
		name     string
		flags    WriteFlag
		expected map[string]bool
	}{
		{
			name:  "None flag",
			flags: WriteFlagNone,
			expected: map[string]bool{
				"append":    false,
				"create":    false,
				"exclusive": false,
				"truncate":  false,
				"sync":      false,
			},
		},
		{
			name:  "Append flag",
			flags: WriteFlagAppend,
			expected: map[string]bool{
				"append":    true,
				"create":    false,
				"exclusive": false,
				"truncate":  false,
				"sync":      false,
			},
		},
		{
			name:  "Create and Truncate flags",
			flags: WriteFlagCreate | WriteFlagTruncate,
			expected: map[string]bool{
				"append":    false,
				"create":    true,
				"exclusive": false,
				"truncate":  true,
				"sync":      false,
			},
		},
		{
			name:  "All flags",
			flags: WriteFlagAppend | WriteFlagCreate | WriteFlagExclusive | WriteFlagTruncate | WriteFlagSync,
			expected: map[string]bool{
				"append":    true,
				"create":    true,
				"exclusive": true,
				"truncate":  true,
				"sync":      true,
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := (tt.flags & WriteFlagAppend) != 0; got != tt.expected["append"] {
				t.Errorf("Append flag: got %v, want %v", got, tt.expected["append"])
			}
			if got := (tt.flags & WriteFlagCreate) != 0; got != tt.expected["create"] {
				t.Errorf("Create flag: got %v, want %v", got, tt.expected["create"])
			}
			if got := (tt.flags & WriteFlagExclusive) != 0; got != tt.expected["exclusive"] {
				t.Errorf("Exclusive flag: got %v, want %v", got, tt.expected["exclusive"])
			}
			if got := (tt.flags & WriteFlagTruncate) != 0; got != tt.expected["truncate"] {
				t.Errorf("Truncate flag: got %v, want %v", got, tt.expected["truncate"])
			}
			if got := (tt.flags & WriteFlagSync) != 0; got != tt.expected["sync"] {
				t.Errorf("Sync flag: got %v, want %v", got, tt.expected["sync"])
			}
		})
	}
}

func TestWriteFlagValues(t *testing.T) {
	// Ensure flags have correct bit values
	if WriteFlagNone != 0 {
		t.Errorf("WriteFlagNone should be 0, got %d", WriteFlagNone)
	}
	if WriteFlagAppend != 1 {
		t.Errorf("WriteFlagAppend should be 1, got %d", WriteFlagAppend)
	}
	if WriteFlagCreate != 2 {
		t.Errorf("WriteFlagCreate should be 2, got %d", WriteFlagCreate)
	}
	if WriteFlagExclusive != 4 {
		t.Errorf("WriteFlagExclusive should be 4, got %d", WriteFlagExclusive)
	}
	if WriteFlagTruncate != 8 {
		t.Errorf("WriteFlagTruncate should be 8, got %d", WriteFlagTruncate)
	}
	if WriteFlagSync != 16 {
		t.Errorf("WriteFlagSync should be 16, got %d", WriteFlagSync)
	}
}

func TestOpenFlag(t *testing.T) {
	tests := []struct {
		name     string
		flags    OpenFlag
		expected map[string]bool
	}{
		{
			name:  "Read only",
			flags: O_RDONLY,
			expected: map[string]bool{
				"read":     true,
				"write":    false,
				"rdwr":     false,
				"append":   false,
				"create":   false,
				"excl":     false,
				"truncate": false,
			},
		},
		{
			name:  "Write only",
			flags: O_WRONLY,
			expected: map[string]bool{
				"read":     false,
				"write":    true,
				"rdwr":     false,
				"append":   false,
				"create":   false,
				"excl":     false,
				"truncate": false,
			},
		},
		{
			name:  "Read/Write with Create and Truncate",
			flags: O_RDWR | O_CREATE | O_TRUNC,
			expected: map[string]bool{
				"read":     false,
				"write":    false,
				"rdwr":     true,
				"append":   false,
				"create":   true,
				"excl":     false,
				"truncate": true,
			},
		},
		{
			name:  "Write with Append and Create",
			flags: O_WRONLY | O_APPEND | O_CREATE,
			expected: map[string]bool{
				"read":     false,
				"write":    true,
				"rdwr":     false,
				"append":   true,
				"create":   true,
				"excl":     false,
				"truncate": false,
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Check access mode (lower 2 bits)
			accessMode := tt.flags & 0x3
			if tt.expected["rdwr"] && accessMode != O_RDWR {
				t.Errorf("Expected O_RDWR mode")
			}
			if tt.expected["write"] && accessMode != O_WRONLY {
				t.Errorf("Expected O_WRONLY mode")
			}
			if tt.expected["read"] && accessMode != O_RDONLY {
				t.Errorf("Expected O_RDONLY mode")
			}

			// Check flag bits
			if got := (tt.flags & O_APPEND) != 0; got != tt.expected["append"] {
				t.Errorf("O_APPEND: got %v, want %v", got, tt.expected["append"])
			}
			if got := (tt.flags & O_CREATE) != 0; got != tt.expected["create"] {
				t.Errorf("O_CREATE: got %v, want %v", got, tt.expected["create"])
			}
			if got := (tt.flags & O_EXCL) != 0; got != tt.expected["excl"] {
				t.Errorf("O_EXCL: got %v, want %v", got, tt.expected["excl"])
			}
			if got := (tt.flags & O_TRUNC) != 0; got != tt.expected["truncate"] {
				t.Errorf("O_TRUNC: got %v, want %v", got, tt.expected["truncate"])
			}
		})
	}
}

func TestOpenFlagValues(t *testing.T) {
	// Ensure flags have correct values matching POSIX conventions
	if O_RDONLY != 0 {
		t.Errorf("O_RDONLY should be 0, got %d", O_RDONLY)
	}
	if O_WRONLY != 1 {
		t.Errorf("O_WRONLY should be 1, got %d", O_WRONLY)
	}
	if O_RDWR != 2 {
		t.Errorf("O_RDWR should be 2, got %d", O_RDWR)
	}
	if O_APPEND != 8 {
		t.Errorf("O_APPEND should be 8, got %d", O_APPEND)
	}
	if O_CREATE != 16 {
		t.Errorf("O_CREATE should be 16, got %d", O_CREATE)
	}
	if O_EXCL != 32 {
		t.Errorf("O_EXCL should be 32, got %d", O_EXCL)
	}
	if O_TRUNC != 64 {
		t.Errorf("O_TRUNC should be 64, got %d", O_TRUNC)
	}
}

func TestFileInfo(t *testing.T) {
	info := FileInfo{
		Name:  "test.txt",
		Size:  1024,
		Mode:  0644,
		IsDir: false,
		Meta: MetaData{
			Name: "memfs",
			Type: "file",
			Content: map[string]string{
				"key": "value",
			},
		},
	}

	if info.Name != "test.txt" {
		t.Errorf("Name: got %s, want test.txt", info.Name)
	}
	if info.Size != 1024 {
		t.Errorf("Size: got %d, want 1024", info.Size)
	}
	if info.Mode != 0644 {
		t.Errorf("Mode: got %o, want 644", info.Mode)
	}
	if info.IsDir {
		t.Error("IsDir should be false")
	}
	if info.Meta.Name != "memfs" {
		t.Errorf("Meta.Name: got %s, want memfs", info.Meta.Name)
	}
	if info.Meta.Content["key"] != "value" {
		t.Errorf("Meta.Content[key]: got %s, want value", info.Meta.Content["key"])
	}
}
