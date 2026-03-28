# pyagfs - AGFS Python SDK

Python SDK for interacting with AGFS (Plugin-based File System) Server API.

See more details at [c4pt0r/agfs](https://github.com/c4pt0r/agfs)

## Installation

```bash
pip install pyagfs
```

For local development:

```bash
pip install -e .
```

## Quick Start

```python
from pyagfs import AGFSClient

# Initialize client
client = AGFSClient("http://localhost:8080")

# Check server health
health = client.health()
print(f"Server version: {health.get('version', 'unknown')}")

# List directory contents
files = client.ls("/")
for file in files:
    print(f"{file['name']} - {'dir' if file['isDir'] else 'file'}")

# Create a new directory
client.mkdir("/test_dir")

# Write to a file
client.write("/test_dir/hello.txt", b"Hello, AGFS!")

# Read file content
content = client.cat("/test_dir/hello.txt")
print(content.decode())

# Get file info
info = client.stat("/test_dir/hello.txt")
print(f"Size: {info['size']} bytes")

# Remove file and directory
client.rm("/test_dir", recursive=True)
```

## High-Level File Operations

The SDK provides helper functions for common operations like copying files within AGFS or transferring files between the local filesystem and AGFS.

```python
from pyagfs import AGFSClient, cp, upload, download

client = AGFSClient("http://localhost:8080")

# Upload local file or directory to AGFS
upload(client, "./local_data", "/remote_data", recursive=True)

# Download file or directory from AGFS to local
download(client, "/remote_data/config.json", "./local_config.json")

# Copy files within AGFS
cp(client, "/remote_data/original.txt", "/remote_data/backup.txt")
```

## Advanced Usage

### Streaming Operations

Useful for handling large files or long-running search results.

```python
# Stream file content
response = client.cat("/large/file.log", stream=True)
for chunk in response.iter_content(chunk_size=8192):
    process(chunk)

# Stream grep results
for match in client.grep("/logs", "error", recursive=True, stream=True):
    if match.get('type') == 'summary':
        print(f"Total matches: {match['count']}")
    else:
        print(f"{match['file']}:{match['line']}: {match['content']}")
```

### Mount Management

Dynamically mount different filesystem backends.

```python
# List mounted plugins
mounts = client.mounts()

# Mount a memory filesystem
client.mount("memfs", "/test/mem", {})

# Mount a SQL filesystem
client.mount("sqlfs", "/test/db", {
    "backend": "sqlite",
    "db_path": "/tmp/test.db"
})

# Unmount a path
client.unmount("/test/mem")
```

### Plugin Management

Load and unload external plugins (shared libraries).

```python
# Load external plugin
result = client.load_plugin("./plugins/myplugin.so")

# List loaded plugins
plugins = client.list_plugins()

# Get detailed plugin info
plugin_infos = client.get_plugins_info()

# Unload plugin
client.unload_plugin("./plugins/myplugin.so")
```

### Search and Integrity

```python
# Recursive case-insensitive search
result = client.grep("/local", "warning|error", recursive=True, case_insensitive=True)
print(f"Found {result['count']} matches")

# Calculate file digest (hash)
# Supported algorithms: "xxh3" (default), "md5"
result = client.digest("/path/to/file.txt", algorithm="xxh3")
print(f"Hash: {result['digest']}")
```

## API Reference

### AGFSClient

#### Constructor
- `AGFSClient(api_base_url, timeout=10)` - Initialize client with API base URL

#### File Operations
- `ls(path="/")` - List directory contents
- `cat(path, offset=0, size=-1, stream=False)` - Read file content (alias: `read`)
- `write(path, data, max_retries=3)` - Write data to file with retry logic
- `create(path)` - Create new empty file
- `rm(path, recursive=False)` - Remove file or directory
- `stat(path)` - Get file/directory information
- `mv(old_path, new_path)` - Move/rename file or directory
- `chmod(path, mode)` - Change file permissions
- `touch(path)` - Update file timestamp
- `digest(path, algorithm="xxh3")` - Calculate file hash

#### Directory Operations
- `mkdir(path, mode="755")` - Create directory

#### Search Operations
- `grep(path, pattern, recursive=False, case_insensitive=False, stream=False)` - Search for pattern in files

#### Mount Operations
- `mounts()` - List all mounted plugins
- `mount(fstype, path, config)` - Mount a plugin dynamically
- `unmount(path)` - Unmount a plugin

#### Plugin Operations
- `list_plugins()` - List all loaded external plugins
- `get_plugins_info()` - Get detailed info about loaded plugins
- `load_plugin(library_path)` - Load an external plugin
- `unload_plugin(library_path)` - Unload an external plugin

#### Health Check
- `health()` - Check server health

### Helper Functions

- `cp(client, src, dst, recursive=False, stream=False)` - Copy files/directories within AGFS
- `upload(client, local_path, remote_path, recursive=False, stream=False)` - Upload from local to AGFS
- `download(client, remote_path, local_path, recursive=False, stream=False)` - Download from AGFS to local

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

### Code Formatting

```bash
black pyagfs/
ruff check pyagfs/
```

## License

See LICENSE file for details.