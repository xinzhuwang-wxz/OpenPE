package plugin

import (
	"github.com/c4pt0r/agfs/agfs-server/pkg/filesystem"
)

// ConfigParameter describes a configuration parameter for a plugin
type ConfigParameter struct {
	Name        string `json:"name"`        // Parameter name
	Type        string `json:"type"`        // Parameter type (string, int, bool, etc.)
	Required    bool   `json:"required"`    // Whether the parameter is required
	Default     string `json:"default"`     // Default value (as string)
	Description string `json:"description"` // Parameter description
}

// ServicePlugin defines the interface for a service that can be mounted to a path
// Each plugin acts as a virtual file system providing service-specific operations
type ServicePlugin interface {
	// Name returns the plugin name
	Name() string

	// Validate validates the plugin configuration before initialization
	// This method should check all required parameters and validate their types/values
	// Returns an error if the configuration is invalid
	Validate(config map[string]interface{}) error

	// Initialize initializes the plugin with optional configuration
	// This method is called after Validate succeeds
	Initialize(config map[string]interface{}) error

	// GetFileSystem returns the FileSystem implementation for this plugin
	// This allows the plugin to handle file operations in a service-specific way
	GetFileSystem() filesystem.FileSystem

	// GetReadme returns the README content for this plugin
	// This provides documentation about the plugin's functionality and usage
	GetReadme() string

	// GetConfigParams returns the list of configuration parameters supported by this plugin
	// This provides metadata about what configuration options are available
	GetConfigParams() []ConfigParameter

	// Shutdown gracefully shuts down the plugin
	Shutdown() error
}

// MountPoint represents a mounted service plugin
type MountPoint struct {
	Path   string
	Plugin ServicePlugin
}

// PluginMetadata contains information about a plugin
type PluginMetadata struct {
	Name        string
	Version     string
	Description string
	Author      string
}

