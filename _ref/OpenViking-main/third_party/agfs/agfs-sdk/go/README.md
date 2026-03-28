# AGFS Go SDK

Go client SDK for AGFS (Abstract Global File System) HTTP API. This SDK provides a simple and idiomatic Go interface for interacting with AGFS servers.

## Installation

Add the SDK to your project using `go get`:

```bash
go get github.com/c4pt0r/agfs/agfs-sdk/go
```

## Quickstart

Here is a complete example showing how to connect to an AGFS server and perform basic file operations.

```go
package main

import (
	"fmt"
	"log"

	agfs "github.com/c4pt0r/agfs/agfs-sdk/go"
)

func main() {
	// 1. Initialize the client
	// You can point to the base URL (e.g., http://localhost:8080)
	client := agfs.NewClient("http://localhost:8080")

	// 2. Check server health
	if err := client.Health(); err != nil {
		log.Fatalf("Server is not healthy: %v", err)
	}
	fmt.Println("Connected to AGFS server")

	// 3. Write data to a file (creates the file if it doesn't exist)
	filePath := "/hello.txt"
	content := []byte("Hello, AGFS!")
	if _, err := client.Write(filePath, content); err != nil {
		log.Fatalf("Failed to write file: %v", err)
	}
	fmt.Printf("Successfully wrote to %s\n", filePath)

	// 4. Read the file back
	readData, err := client.Read(filePath, 0, -1) // -1 reads the whole file
	if err != nil {
		log.Fatalf("Failed to read file: %v", err)
	}
	fmt.Printf("Read content: %s\n", string(readData))

	// 5. Get file metadata
	info, err := client.Stat(filePath)
	if err != nil {
		log.Fatalf("Failed to stat file: %v", err)
	}
	fmt.Printf("File info: Size=%d, ModTime=%s\n", info.Size, info.ModTime)

	// 6. Clean up
	if err := client.Remove(filePath); err != nil {
		log.Printf("Failed to remove file: %v", err)
	}
	fmt.Println("File removed")
}
```

## Usage Guide

### Client Initialization

You can create a client using `NewClient`. The SDK automatically handles the `/api/v1` path suffix if omitted.

```go
// Connect to localhost
client := agfs.NewClient("http://localhost:8080")
```

For advanced configuration (e.g., custom timeouts, TLS), use `NewClientWithHTTPClient`:

```go
httpClient := &http.Client{
    Timeout: 30 * time.Second,
}
client := agfs.NewClientWithHTTPClient("http://localhost:8080", httpClient)
```

### File Operations

#### Read and Write
The `Write` method includes automatic retries with exponential backoff for network errors.

```go
// Write data
msg, err := client.Write("/logs/app.log", []byte("application started"))

// Read entire file
data, err := client.Read("/logs/app.log", 0, -1)

// Read partial content (e.g., first 100 bytes)
header, err := client.Read("/logs/app.log", 0, 100)
```

#### Manage Files
```go
// Create an empty file
err := client.Create("/newfile.txt")

// Rename or move a file
err := client.Rename("/newfile.txt", "/archive/oldfile.txt")

// Change permissions
err := client.Chmod("/script.sh", 0755)

// Delete a file
err := client.Remove("/archive/oldfile.txt")
```

### Directory Operations

```go
// Create a directory
err := client.Mkdir("/data/images", 0755)

// List directory contents
files, err := client.ReadDir("/data/images")
for _, f := range files {
    fmt.Printf("%s (Dir: %v, Size: %d)\n", f.Name, f.IsDir, f.Size)
}

// Remove a directory recursively
err := client.RemoveAll("/data")
```

### Advanced Features

#### Streaming
For large files, use `ReadStream` to process data without loading it all into memory.

```go
reader, err := client.ReadStream("/large-video.mp4")
if err != nil {
    log.Fatal(err)
}
defer reader.Close()

io.Copy(localFile, reader)
```

#### Server-Side Search (Grep)
Perform regex searches directly on the server.

```go
// Recursive search for "error" in /var/logs, case-insensitive
results, err := client.Grep("/var/logs", "error", true, true)
for _, match := range results.Matches {
    fmt.Printf("%s:%d: %s\n", match.File, match.Line, match.Content)
}
```

#### Checksums
Calculate file digests on the server side.

```go
// Calculate xxHash3 (or "md5")
resp, err := client.Digest("/iso/installer.iso", "xxh3")
fmt.Printf("Digest: %s\n", resp.Digest)
```

## Testing

To run the SDK tests:

```bash
go test -v
```

## License

See the LICENSE file in the root of the repository.