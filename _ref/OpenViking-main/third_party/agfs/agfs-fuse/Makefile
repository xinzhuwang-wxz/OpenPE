.PHONY: build install clean test

# Binary name
BINARY=agfs-fuse

# Build directory
BUILD_DIR=build

# Installation directory
INSTALL_DIR=/usr/local/bin

build:
	@echo "Building $(BINARY)..."
	@mkdir -p $(BUILD_DIR)
	go build -o $(BUILD_DIR)/$(BINARY) ./cmd/agfs-fuse

install: build
	@echo "Installing $(BINARY) to $(INSTALL_DIR)..."
	@sudo cp $(BUILD_DIR)/$(BINARY) $(INSTALL_DIR)/
	@echo "Installation complete"

clean:
	@echo "Cleaning build artifacts..."
	@rm -rf $(BUILD_DIR)
	@echo "Clean complete"

test:
	@echo "Running tests..."
	go test -v ./...
