#!/bin/bash

# BigQuery Agent Setup Script
# Simple setup for BigQuery Agent with Google ADK

set -e

echo "Setting up BigQuery Agent..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Create requirements.txt
echo "Creating requirements.txt..."
cat > requirements.txt << EOF
google-adk
toolbox-core
EOF

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download MCP Toolbox for MCP agent
echo "Setting up MCP Toolbox..."
cd bq-agent-app-mcp/mcp-toolbox
chmod +x install-mcp-toolbox.sh
./install-mcp-toolbox.sh
cd ../..

echo ""
echo "Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source .venv/bin/activate"
echo "2. Configure authentication: gcloud auth application-default login"
echo "3. Run the agent: adk web"
echo ""
echo "For MCP agent, start the toolbox server first:"
echo "./bq-agent-app-mcp/mcp-toolbox/toolbox --prebuilt bigquery"
