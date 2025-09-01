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

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Download MCP Toolbox for MCP agent
echo "Setting up MCP Toolbox..."
cd bq_agent_app_mcp/mcp-toolbox
chmod +x install-mcp-toolbox.sh
./install-mcp-toolbox.sh
cd ../..

# Copy .env example. Update the value accordingly
echo "Setting up Multi Agent environment..."
cd bq_multi_agent_app
cp .env.example .env

echo ""
echo "Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source .venv/bin/activate"
echo "2. Configure authentication: gcloud auth application-default login"
echo "3. Run the agent: adk web"
echo ""
echo "For MCP agent, start the toolbox server first:"
echo "./bq_agent_app_mcp/mcp-toolbox/toolbox --prebuilt bigquery"
