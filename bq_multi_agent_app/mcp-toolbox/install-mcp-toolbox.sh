#!/bin/bash

# Install MCP Toolbox for BigQuery
# Based on: https://cloud.google.com/bigquery/docs/pre-built-tools-with-mcp-toolbox#install

set -e

echo "Installing MCP Toolbox for BigQuery..."

# Set the version (you can update this to the latest version)
MCP_VERSION="v0.13.0"
MCP_OS="linux"
MCP_ARCH="amd64"

# Download the appropriate binary
DOWNLOAD_URL="https://storage.googleapis.com/genai-toolbox/${MCP_VERSION}/${MCP_OS}/${MCP_ARCH}/toolbox"
echo "Downloading MCP Toolbox from: $DOWNLOAD_URL"

if command -v curl >/dev/null 2>&1; then
    curl -O "$DOWNLOAD_URL"
elif command -v wget >/dev/null 2>&1; then
    wget "$DOWNLOAD_URL"
else
    echo "Error: Neither curl nor wget is available. Please install one of them."
    exit 1
fi

# Make the binary executable
chmod +x toolbox

# Verify the installation
echo "Verifying installation..."
./toolbox --version

echo ""
echo "MCP Toolbox installation completed successfully!"
echo "The toolbox binary is now available at: $(pwd)/toolbox"
echo ""
echo "Next steps:"
echo "- Configure your IDE with the MCP server using the path: $(pwd)/toolbox"
echo "- Set the BIGQUERY_PROJECT environment variable to your Google Cloud project ID"
