package fusefs

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	agfs "github.com/c4pt0r/agfs/agfs-sdk/go"
)

func TestHandleManagerBasicOperations(t *testing.T) {
	// Note: This is a unit test that doesn't require a running server
	// We're testing the handle manager's mapping logic

	client := agfs.NewClient("http://localhost:8080")
	hm := NewHandleManager(client)

	// Test initial state
	if count := hm.Count(); count != 0 {
		t.Errorf("Expected 0 handles, got %d", count)
	}

	// Note: We can't actually test Open/Close without a running server
	// Those would be integration tests
}

func TestHandleManagerConcurrency(t *testing.T) {
	client := agfs.NewClient("http://localhost:8080")
	hm := NewHandleManager(client)

	// Test concurrent access to handle map (shouldn't panic)
	done := make(chan bool, 2)

	go func() {
		for i := 0; i < 100; i++ {
			hm.Count()
		}
		done <- true
	}()

	go func() {
		for i := 0; i < 100; i++ {
			hm.Count()
		}
		done <- true
	}()

	<-done
	<-done

	// If we got here without panic, concurrency is safe
}

func TestHandleManager_OpenHandleNotSupportedFallback(t *testing.T) {
	// Create a test HTTP server that returns 501 for OpenHandle
	testServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/api/v1/handles/open" {
			w.WriteHeader(http.StatusNotImplemented)
			// Optionally, write an error JSON (agfs.Client expects it but will map 501 first)
			json.NewEncoder(w).Encode(agfs.ErrorResponse{Error: "handlefs not supported"})
			return
		}
		// For other paths, return 200 OK (or mock as needed)
		w.WriteHeader(http.StatusOK)
	}))
	defer testServer.Close()

	// Create an agfs.Client configured to talk to our test server
	client := agfs.NewClient(testServer.URL)
	hm := NewHandleManager(client)

	// Attempt to open a handle
	fuseHandle, err := hm.Open("/test/path", 0, 0)
	if err != nil {
		t.Fatalf("Expected nil error during Open, but got: %v", err)
	}

	// Verify that a local handle was created
	if count := hm.Count(); count != 1 {
		t.Errorf("Expected 1 handle after fallback, got %d", count)
	}

	info, ok := hm.handles[fuseHandle]
	if !ok {
		t.Fatalf("Handle %d not found in manager", fuseHandle)
	}
	if info.htype != handleTypeLocal {
		t.Errorf("Expected handle type to be local (%v), got %v", handleTypeLocal, info.htype)
	}

	// Test closing the local handle
	err = hm.Close(fuseHandle)
	if err != nil {
		t.Errorf("Error closing local handle: %v", err)
	}
	if count := hm.Count(); count != 0 {
		t.Errorf("Expected 0 handles after close, got %d", count)
	}
}
