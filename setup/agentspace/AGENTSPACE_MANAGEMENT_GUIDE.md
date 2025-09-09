# AgentSpace Management

This directory contains tools for managing Google Cloud AgentSpace agents and ReasoningEngines.

## Files

- `manage_agentspace.sh` - Comprehensive script for AgentSpace and ReasoningEngine management
- `test_agent_engine.py` - Testing script for Agent Engine SDK

## Quick Start

The `manage_agentspace.sh` script is your one-stop solution for managing both AgentSpace agents and ReasoningEngines.

### Configuration

Before using the script, update the configuration variables at the top of `manage_agentspace.sh`:

```bash
export PROJECT_ID="your-project-id"
export PROJECT_NUMBER="your-project-number"
export REASONING_ENGINE_ID="your-reasoning-engine-id"
export AS_APP="your-agentspace-id"
export AGENT_DISPLAY_NAME="your-agent-name"
```

### Usage

```bash
# Make the script executable
chmod +x manage_agentspace.sh

# Show help
./manage_agentspace.sh help

# AgentSpace operations
./manage_agentspace.sh list           # List all agents
./manage_agentspace.sh deploy         # Deploy new agent
./manage_agentspace.sh delete         # Delete agent by display name
./manage_agentspace.sh replace        # Replace existing agent (default)

# ReasoningEngine operations
./manage_agentspace.sh delete-reasoning-engine           # Delete with sessions cleanup
./manage_agentspace.sh delete-reasoning-engine --force   # Force delete everything
./manage_agentspace.sh delete-reasoning-engine --dry-run # Preview what would be deleted
./manage_agentspace.sh list-sessions                     # List ReasoningEngine sessions
./manage_agentspace.sh delete-sessions                   # Delete all sessions
```

## Features

### AgentSpace Management
- **List agents**: View all agents in your AgentSpace
- **Deploy agent**: Create a new agent with your ReasoningEngine
- **Delete agent**: Remove an agent by display name
- **Replace agent**: Delete existing and deploy new (recommended for updates)

### ReasoningEngine Management
- **Session management**: List and delete ReasoningEngine sessions
- **Safe deletion**: Delete sessions first, then ReasoningEngine
- **Force deletion**: Delete ReasoningEngine and all child resources at once
- **Dry run mode**: Preview deletions without executing them

### Error Handling
The script handles the common ReasoningEngine deletion error:
> "The ReasoningEngine contains child resources: sessions. Please delete the child resources before deleting the ReasoningEngine, or set force to true to delete child resources."

Two approaches are available:
1. **Step-by-step** (default): Delete sessions first, then ReasoningEngine
2. **Force deletion**: Use `--force` flag to delete everything at once

## Prerequisites

- Google Cloud CLI (`gcloud`) installed and authenticated
- `curl` command available
- `jq` (optional, for better JSON formatting)
- Appropriate Google Cloud permissions for:
  - Discovery Engine API
  - Vertex AI Platform API
  - Agent Engine operations

## Examples

### Replace an existing agent
```bash
./manage_agentspace.sh replace
```

### Fix ReasoningEngine deletion error
```bash
# Preview what would be deleted
./manage_agentspace.sh delete-reasoning-engine --dry-run

# Delete sessions first, then ReasoningEngine
./manage_agentspace.sh delete-reasoning-engine

# Or force delete everything at once
./manage_agentspace.sh delete-reasoning-engine --force
```

### Manage sessions only
```bash
# List all sessions
./manage_agentspace.sh list-sessions

# Delete all sessions (but keep ReasoningEngine)
./manage_agentspace.sh delete-sessions
```

## Troubleshooting

1. **Authentication errors**: Ensure you're logged in with `gcloud auth login`
2. **Permission errors**: Verify your account has the necessary API permissions
3. **Configuration errors**: Double-check all configuration variables in the script
4. **API errors**: Check the raw JSON response for detailed error messages

For more detailed error information, the script outputs the full API response when operations fail.
