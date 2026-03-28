//go:build !windows

package loader

import "github.com/ebitengine/purego"

func openLibrary(path string) (uintptr, error) {
	// RTLD_NOW = resolve all symbols immediately
	// RTLD_LOCAL = symbols not available for subsequently loaded libraries
	const (
		RTLD_NOW   = 0x2
		RTLD_LOCAL = 0x0
	)
	return purego.Dlopen(path, RTLD_NOW|RTLD_LOCAL)
}
