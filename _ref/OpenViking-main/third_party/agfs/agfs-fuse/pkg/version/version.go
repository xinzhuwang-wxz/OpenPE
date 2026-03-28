package version

// Version information
var (
	Version   = "dev"
	GitCommit = "unknown"
	BuildTime = "unknown"
)

// GetVersion returns the version string
func GetVersion() string {
	return Version
}

// GetFullVersion returns the full version string with git commit and build time
func GetFullVersion() string {
	return Version + " (" + GitCommit + ", built " + BuildTime + ")"
}
