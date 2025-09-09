# BigQuery Agent with Google ADK

A powerful AI-powered data analysis agent that combines Google BigQuery with the Google Agent Development Kit (ADK) to enable natural language interactions with your data warehouse.

## Quick Start

1. **Authentication**
```bash
gcloud auth application-default login
```

2. **Clone and Setup**
```bash
git clone https://github.com/johanesalxd/bq-agent-app.git
cd bq-agent-app

# Install uv (if not already installed)
# Visit: https://docs.astral.sh/uv/getting-started/installation/

# Install dependencies with uv
uv sync

# Activate environment
source .venv/bin/activate

# Setup MCP Toolbox (for Multi-Agent System)
cd setup/mcp_toolbox

# Update the script parameters for your OS before running
# Edit install-mcp-toolbox.sh and update:
# - MCP_VERSION: choose the version from https://github.com/googleapis/genai-toolbox/releases
# - MCP_OS: "linux" for Linux, "darwin" for macOS
# - MCP_ARCH: "amd64" for Intel/x64, "arm64" for Apple Silicon
# Example for macOS Apple Silicon: MCP_OS="darwin" MCP_ARCH="arm64"

chmod +x install-mcp-toolbox.sh
./install-mcp-toolbox.sh
cd ../..

# Configure the environment
cp .env.example .env
export $(cat .env | grep -v '^#' | xargs)

# Run the MCP server with custom configuration
cd setup/mcp_toolbox
./toolbox --tools-file=tools.yaml --port=5000
cd ../..

# Run ADK
uv run adk web
```

## Additional Guides

- [Agentspace Management Guide](setup/agentspace/AGENTSPACE_MANAGEMENT_GUIDE.md) - Comprehensive guide for managing Google Cloud Agentspace agents and ReasoningEngines
- [Vertex Extensions Setup Guide](setup/vertex_extensions/VERTEX_EXTENSIONS_GUIDE.md) - Complete guide for setting up Vertex AI Extensions for code interpretation
- [MCP Toolbox Deployment Guide](setup/mcp_toolbox/MCP_TOOLBOX_GUIDE.md) - Deploy MCP toolbox to Google Cloud Run for production use

## Implementation

This project provides a comprehensive **Multi-Agent System** for BigQuery analytics with advanced data science capabilities.

| Feature | Multi-Agent System |
|---------|-------------------|
| **Directory** | `bq_multi_agent_app/` |
| **Setup Complexity** | Moderate |
| **BigQuery Operations** | ✅ |
| **MCP Protocol Support** | ✅ |
| **Python Data Science** | ✅ |
| **Statistical Analysis** | ✅ |
| **Data Visualization** | ✅ |
| **Multi-Agent Orchestration** | ✅ |
| **Additional Dependencies** | MCP Toolbox |

### Key Benefits

- **Advanced Analytics**: Complete data science workflows with comprehensive analysis and visualizations
- **Multi-Agent Architecture**: Root agent orchestrates specialized sub-agents for different tasks
- **MCP Integration**: Uses Model Context Protocol for standardized BigQuery operations

## Core Features

- 🔍 **Dataset Discovery**: List and explore BigQuery datasets
- 📊 **Table Analysis**: Get detailed schema and metadata information
- 🔎 **SQL Execution**: Execute complex SQL queries through natural language
- 🤖 **AI-Powered**: Uses Gemini 2.5 Flash for intelligent query understanding
- 🔐 **Flexible Authentication**: Multiple authentication methods supported

## Advanced Features

- 🎯 **Multi-Agent Orchestration**: Root agent delegates tasks to specialized sub-agents
- 🐍 **Python Analytics**: Stateful code execution for advanced data science workflows
- 📈 **Data Visualization**: Automated chart generation with matplotlib
- 🧠 **Statistical Analysis**: Comprehensive statistical testing and modeling
- 🔗 **MCP Integration**: Uses Model Context Protocol for BigQuery operations
- 💬 **Conversational Analytics**: Interactive BigQuery exploration via MCP
- 📊 **Time Series Forecasting**: Built-in forecasting capabilities for temporal data
- 📝 **Pre-defined SQL Templates**: Execute common SQL patterns efficiently

## Usage

### Example Interactions

**Basic Operations**
```
"What datasets are available in my project?"
"Show me the schema of the sales_data table"
"Find the top 10 customers by revenue this year"
```

**Advanced Analytics**
```
"Analyze sales trends over the last 12 months and create a visualization"
→ Root agent retrieves data, DS agent creates trend analysis with charts

"Build a predictive model for customer churn"
→ Root agent extracts features, DS agent trains and evaluates model

"Compare revenue across product categories with statistical testing"
→ Root agent queries data, DS agent performs statistical analysis
```

## Architecture

### Foundation
The system is built on:
- **Google Agent Development Kit (ADK)**: Framework for building AI agents
- **Gemini 2.5 Flash**: Large language model for natural language understanding
- **Vertex AI**: Google Cloud's AI platform integration

### Multi-Agent System Architecture
```
Root Agent (bigquery_ds_agent)
├── Conversational Toolset (MCP Toolbox)
│   └── bigquery-conversational-analytics    # Quick insights & answers
├── Data Retrieval Toolset (MCP Toolbox)
│   ├── bigquery-execute-sql                 # Raw data extraction
│   ├── bigquery-forecast                    # Time series forecasting
│   ├── bigquery-list-dataset-ids           # Dataset discovery
│   ├── bigquery-get-dataset-info           # Dataset metadata
│   ├── bigquery-list-table-ids             # Table discovery
│   └── bigquery-get-table-info             # Table schema
└── DS Sub-Agent (ds_agent)
    ├── Python Code Execution
    ├── Data Visualization
    └── Statistical Analysis
```

#### Two-Path Workflow
The agent intelligently chooses between two approaches:

**PATH 1: Quick Insights (Conversational Analytics)**
- For simple questions and quick answers
- Uses `bigquery-conversational-analytics` directly
- Returns natural language insights

**PATH 2: In-Depth Analysis (Data Retrieval + Data Science)**
- For complex analysis and visualizations
- Uses `bigquery-execute-sql` → `call_data_science_agent`
- Provides full control over data and analysis

## Project Structure

```
bq-agent-app/
├── pyproject.toml                   # uv package configuration
├── uv.lock                          # Dependency lock file
├── bq_multi_agent_app/              # Multi-Agent System
│   ├── agent.py                     # Root agent with MCP integration
│   ├── tools.py                     # MCP BigQuery tools + DS agent wrapper
│   ├── prompts.py                   # Agent instructions
│   └── sub_agents/
│       └── ds_agents/
│           ├── agent.py             # Data science agent
│           └── prompts.py           # DS agent instructions
├── setup/                           # Setup and deployment tools
│   ├── mcp_toolbox/                 # MCP Toolbox setup
│   │   ├── install-mcp-toolbox.sh   # Local installation script
│   │   ├── deploy.sh                # Cloud Run deployment
│   │   ├── Dockerfile               # Container definition
│   │   └── MCP_TOOLBOX_GUIDE.md     # Deployment guide
│   ├── vertex_extensions/           # Vertex AI Extensions Management
│   │   ├── setup_vertex_extensions.py   # Create extensions
│   │   ├── cleanup_vertex_extensions.py # Clean up extensions
│   │   ├── utils.py                 # Shared utilities
│   │   └── VERTEX_EXTENSIONS_GUIDE.md   # Setup guide
│   └── agentspace/                  # Agentspace Management
│       ├── manage_agentspace.sh     # Agentspace and ReasoningEngine management
│       ├── test_agent_engine.py     # Testing utilities
│       └── AGENTSPACE_MANAGEMENT_GUIDE.md  # Comprehensive guide
└── README.md
```

## Prerequisites

- **Python 3.11+**
- **uv** package manager ([installation guide](https://docs.astral.sh/uv/getting-started/installation/))
- **Google Cloud Project** with BigQuery enabled
- **Google Cloud credentials**

## Deployment

The Multi-Agent System requires both the MCP Toolbox and the Agent to be deployed. You can choose to run each component locally or deploy to Cloud Run based on your needs.

### Step 1: Deploy the MCP Toolbox

The MCP Toolbox provides BigQuery connectivity for the agent.

#### Option A: Run MCP Toolbox Locally
```bash
# Set environment variables
cp .env.example .env
export $(cat .env | grep -v '^#' | xargs)

# Start the MCP server with custom configuration
cd setup/mcp_toolbox
BIGQUERY_PROJECT=$BIGQUERY_PROJECT ./toolbox --tools-file=tools.yaml --port=5000
```

#### Option B: Deploy MCP Toolbox to Cloud Run
```bash
# Set environment variables
cp .env.example .env
export $(cat .env | grep -v '^#' | xargs)

# Setup and deploy
cd setup/mcp_toolbox
chmod +x deploy.sh
./deploy.sh
```

The script will:
- Enable required Google Cloud APIs
- Create a service account with BigQuery permissions
- Build and push the Docker image
- Deploy to Cloud Run with `--allow-unauthenticated`
- Provide the service URL for access

### Step 2: Deploy the Agent

The agent connects to the MCP Toolbox (local or cloud) to provide BigQuery functionality.

#### Option A: Run Agent Locally
```bash
# Set environment variables
cp .env.example .env
export $(cat .env | grep -v '^#' | xargs)

uv run adk web  # or uv run adk run
```

#### Option B: Deploy Agent to Cloud Run
```bash
# Set environment variables
cp .env.example bq_multi_agent_app/.env
export $(cat .env | grep -v '^#' | xargs)

uv run adk deploy cloud_run \
  --project=your-project-id \
  --region=us-central1 \
  --service_name=bq-agent-app \
  --trace_to_cloud \
  --with_ui \
  ./bq_multi_agent_app
```

After deployment:
- Access your agent at the provided Cloud Run service URL
- The web UI will be available for interactive testing
- Cloud tracing is enabled for monitoring and debugging

#### Option C: Deploy Agent to Agent Engine
```bash
# Set environment variables
export $(cat .env | grep -v '^#' | xargs)

uv run adk deploy agent_engine \
  --project=your-project-id \
  --region=us-central1 \
  --staging_bucket="gs://your-project-id-adk-staging" \
  --display_name="BigQuery Multi-Agent App" \
  --trace_to_cloud \
  --env_file=.env \
  ./bq_multi_agent_app
```

After deployment:
- Agent is deployed to Vertex AI Agent Engine with managed sessions
- Provides programmatic access via the Agent Engine API
- Integrated with Vertex AI ecosystem for enterprise use
- Supports both synchronous and asynchronous operations

### Deployment Combinations

| MCP Toolbox | Agent | Use Case |
|-------------|-------|----------|
| Local | Local | Development and testing |
| Cloud Run | Local | Development with shared toolbox |
| Cloud Run | Cloud Run | Full production deployment |
| Cloud Run | Agent Engine | Enterprise deployment with managed sessions |

**Note**: Ensure your service account has the necessary BigQuery permissions for your project. For advanced MCP configurations, refer to the [official documentation](https://googleapis.github.io/genai-toolbox/how-to/deploy_toolbox/).

## Agentspace Management

Once your agent is deployed to Agent Engine, you can manage it through Google Cloud Agentspace. The project includes comprehensive tools for Agentspace operations:

### Features
- **Agent Management**: List, deploy, delete, and replace agents in Agentspace
- **ReasoningEngine Operations**: Manage ReasoningEngine sessions and handle deletion errors
- **Error Resolution**: Automatically handle the common "child resources" deletion error
- **Dry Run Mode**: Preview operations before execution

### Quick Usage
```bash
cd setup/agentspace

# Make script executable
chmod +x manage_agentspace.sh

# Configure your project details in the script
# Edit manage_agentspace.sh and update:
# - PROJECT_ID, PROJECT_NUMBER
# - REASONING_ENGINE_ID, AS_APP
# - AGENT_DISPLAY_NAME

# Common operations
./manage_agentspace.sh list                    # List all agents
./manage_agentspace.sh deploy                  # Deploy new agent
./manage_agentspace.sh delete                  # Delete existing agent
./manage_agentspace.sh delete-reasoning-engine # Fix deletion errors
./manage_agentspace.sh help                    # Show all commands
```

### Solving ReasoningEngine Deletion Errors
If you encounter the error: *"The ReasoningEngine contains child resources: sessions"*, use:

```bash
# Preview what would be deleted
./manage_agentspace.sh delete-reasoning-engine --dry-run

# Delete sessions first, then ReasoningEngine (recommended)
./manage_agentspace.sh delete-reasoning-engine

# Or force delete everything at once
./manage_agentspace.sh delete-reasoning-engine --force
```

For detailed instructions, see the [Agentspace Management Guide](setup/agentspace/AGENTSPACE_MANAGEMENT_GUIDE.md).

## Security Considerations

- Use minimum required permissions
- Store credentials securely
- Review SQL queries executed by agents
- Consider read-only mode for production

## Related Resources

- [Google Agent Development Kit Documentation](https://cloud.google.com/adk)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Toolbox Cloud Run Deployment Guide](https://googleapis.github.io/genai-toolbox/how-to/deploy_toolbox/)
- [Blog Post: BigQuery meets Google ADK and MCP](https://cloud.google.com/blog/products/ai-machine-learning/bigquery-meets-google-adk-and-mcp)

---

*Built with ❤️ using Google Agent Development Kit, BigQuery, and MCP*
