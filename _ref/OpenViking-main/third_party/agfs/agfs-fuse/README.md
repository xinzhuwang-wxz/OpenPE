# AGFS FUSE [WIP]

A FUSE filesystem implementation for mounting AGFS servers on Linux.

## Platform Support

Currently supports **Linux only**.

## Prerequisites

- Go 1.21.1 or higher
- FUSE development libraries
- Linux kernel with FUSE support

Install FUSE on your system:
```bash
# Debian/Ubuntu
sudo apt-get install fuse3 libfuse3-dev

# RHEL/Fedora/CentOS
sudo dnf install fuse3 fuse3-devel

# Arch Linux
sudo pacman -S fuse3
```

## Quick Start

### Build

```bash
# Using Makefile (recommended)
make build

# Or build directly with Go
go build -o build/agfs-fuse ./cmd/agfs-fuse
```

### Install (Optional)

```bash
# Install to /usr/local/bin
make install
```

### Mount

```bash
# Basic usage
./build/agfs-fuse --agfs-server-url http://localhost:8080 --mount /mnt/agfs

# With custom cache TTL
./build/agfs-fuse --agfs-server-url http://localhost:8080 --mount /mnt/agfs --cache-ttl=10s

# Enable debug output
./build/agfs-fuse --agfs-server-url http://localhost:8080 --mount /mnt/agfs --debug

# Allow other users to access the mount
./build/agfs-fuse --agfs-server-url http://localhost:8080 --mount /mnt/agfs --allow-other
```

### Unmount

Press `Ctrl+C` in the terminal where agfs-fuse is running, or use:
```bash
fusermount -u /mnt/agfs
```

## Usage

```
agfs-fuse [options]

Options:
  -agfs-server-url string
        AGFS server URL (required)
  -mount string
        Mount point directory (required)
  -cache-ttl duration
        Cache TTL duration (default 5s)
  -debug
        Enable debug output
  -allow-other
        Allow other users to access the mount
  -version
        Show version information
```

## License

See LICENSE file for details.
