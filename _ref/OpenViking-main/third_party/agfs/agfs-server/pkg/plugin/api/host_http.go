package api

import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"strings"
	"time"

	log "github.com/sirupsen/logrus"
	wazeroapi "github.com/tetratelabs/wazero/api"
)

// HTTPRequest represents an HTTP request from WASM
type HTTPRequest struct {
	Method  string            `json:"method"`
	URL     string            `json:"url"`
	Headers map[string]string `json:"headers"`
	Body    []byte            `json:"body"`
	Timeout int               `json:"timeout"` // timeout in seconds
}

// HTTPResponse represents an HTTP response to WASM
type HTTPResponse struct {
	StatusCode int               `json:"status_code"`
	Headers    map[string]string `json:"headers"`
	Body       []byte            `json:"body"`
	Error      string            `json:"error,omitempty"`
}

// HostHTTPRequest performs an HTTP request from the host
// Parameters:
//   - params[0]: pointer to JSON-encoded HTTPRequest
//
// Returns: packed u64 (lower 32 bits = response pointer, upper 32 bits = response size)
func HostHTTPRequest(ctx context.Context, mod wazeroapi.Module, params []uint64) []uint64 {
	requestPtr := uint32(params[0])

	// Read request JSON from memory
	requestJSON, ok := readStringFromMemory(mod, requestPtr)
	if !ok {
		log.Errorf("host_http_request: failed to read request from memory")
		return []uint64{0}
	}

	log.Debugf("host_http_request: requestJSON=%s", requestJSON)

	// Parse request
	var req HTTPRequest
	if err := json.Unmarshal([]byte(requestJSON), &req); err != nil {
		log.Errorf("host_http_request: failed to parse request JSON: %v", err)
		resp := HTTPResponse{
			Error: "failed to parse request: " + err.Error(),
		}
		return packHTTPResponse(mod, &resp)
	}

	// Validate method
	if req.Method == "" {
		req.Method = "GET"
	}

	// Create HTTP client with timeout
	timeout := time.Duration(req.Timeout) * time.Second
	if timeout == 0 {
		timeout = 30 * time.Second // default 30s timeout
	}
	client := &http.Client{
		Timeout: timeout,
	}

	// Create HTTP request
	var bodyReader io.Reader
	if len(req.Body) > 0 {
		bodyReader = strings.NewReader(string(req.Body))
	}

	httpReq, err := http.NewRequestWithContext(ctx, req.Method, req.URL, bodyReader)
	if err != nil {
		log.Errorf("host_http_request: failed to create request: %v", err)
		resp := HTTPResponse{
			Error: "failed to create request: " + err.Error(),
		}
		return packHTTPResponse(mod, &resp)
	}

	// Set headers
	for key, value := range req.Headers {
		httpReq.Header.Set(key, value)
	}

	// Perform request
	httpResp, err := client.Do(httpReq)
	if err != nil {
		log.Errorf("host_http_request: request failed: %v", err)
		resp := HTTPResponse{
			Error: "request failed: " + err.Error(),
		}
		return packHTTPResponse(mod, &resp)
	}
	defer httpResp.Body.Close()

	// Read response body
	respBody, err := io.ReadAll(httpResp.Body)
	if err != nil {
		log.Errorf("host_http_request: failed to read response body: %v", err)
		resp := HTTPResponse{
			StatusCode: httpResp.StatusCode,
			Error:      "failed to read response body: " + err.Error(),
		}
		return packHTTPResponse(mod, &resp)
	}

	// Build response headers map
	respHeaders := make(map[string]string)
	for key, values := range httpResp.Header {
		if len(values) > 0 {
			respHeaders[key] = values[0] // Take first value
		}
	}

	// Create response
	resp := HTTPResponse{
		StatusCode: httpResp.StatusCode,
		Headers:    respHeaders,
		Body:       respBody,
	}

	log.Debugf("host_http_request: status=%d, bodyLen=%d", resp.StatusCode, len(resp.Body))
	return packHTTPResponse(mod, &resp)
}

// packHTTPResponse serializes and writes HTTPResponse to WASM memory
func packHTTPResponse(mod wazeroapi.Module, resp *HTTPResponse) []uint64 {
	respJSON, err := json.Marshal(resp)
	if err != nil {
		log.Errorf("packHTTPResponse: failed to marshal response: %v", err)
		return []uint64{0}
	}

	respPtr, _, err := writeBytesToMemory(mod, respJSON)
	if err != nil {
		log.Errorf("packHTTPResponse: failed to write response to memory: %v", err)
		return []uint64{0}
	}

	// Pack pointer and size
	packed := uint64(respPtr) | (uint64(len(respJSON)) << 32)
	return []uint64{packed}
}
