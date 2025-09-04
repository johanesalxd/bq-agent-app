# BigQuery Agent with Google ADK

A powerful AI-powered data analysis agent that combines Google BigQuery with the Google Agent Development Kit (ADK) to enable natural language interactions with your data warehouse. Choose from two implementations based on your needs.

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
cd mcp_toolbox_setup

# Update the script parameters for your OS before running
# Edit install-mcp-toolbox.sh and update:
# - MCP_VERSION: choose the version from https://github.com/googleapis/genai-toolbox/releases
# - MCP_OS: "linux" for Linux, "darwin" for macOS
# - MCP_ARCH: "amd64" for Intel/x64, "arm64" for Apple Silicon
# Example for macOS Apple Silicon: MCP_OS="darwin" MCP_ARCH="arm64"

chmod +x install-mcp-toolbox.sh
./install-mcp-toolbox.sh
cd ..

# Configure the environment
cp .env.example .env
export $(cat .env | grep -v '^#' | xargs)

# Run the MCP server
./mcp_toolbox_setup/toolbox --prebuilt bigquery

# Run ADK
uv run adk web
```

## Additional Guides

- [Vertex Extensions Setup Guide](vertex_extensions_setup/VERTEX_EXTENSIONS_GUIDE.md) - Complete guide for setting up Vertex AI Extensions for code interpretation
- [MCP Toolbox Deployment Guide](mcp_toolbox_setup/MCP_TOOLBOX_GUIDE.md) - Deploy MCP toolbox to Google Cloud Run for production use

## Available Implementations

| Feature | ADK Agent | Multi-Agent System |
|---------|-----------|-------------------|
| **Directory** | `bq_agent_adk/` | `bq_multi_agent_app/` |
| **Setup Complexity** | Simple | Moderate |
| **BigQuery Operations** | ✅ | ✅ |
| **MCP Protocol Support** | ❌ | ✅ |
| **Python Data Science** | ❌ | ✅ |
| **Statistical Analysis** | ❌ | ✅ |
| **Data Visualization** | ❌ | ✅ |
| **Multi-Agent Orchestration** | ❌ | ✅ |
| **Additional Dependencies** | None | MCP Toolbox |

### When to Use Which

- **ADK Agent**: Basic BigQuery queries and exploration, simple setup
- **Multi-Agent System**: Advanced analytics, data science workflows, comprehensive analysis with visualizations

## Core Features (Both Implementations)

- 🔍 **Dataset Discovery**: List and explore BigQuery datasets
- 📊 **Table Analysis**: Get detailed schema and metadata information
- 🔎 **SQL Execution**: Execute complex SQL queries through natural language
- 🤖 **AI-Powered**: Uses Gemini 2.5 Flash for intelligent query understanding
- 🔐 **Flexible Authentication**: Multiple authentication methods supported

## Multi-Agent System Exclusive Features

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

**Basic Operations (Both Implementations)**
```
"What datasets are available in my project?"
"Show me the schema of the sales_data table"
"Find the top 10 customers by revenue this year"
```

**Advanced Analytics (Multi-Agent Only)**
```
"Analyze sales trends over the last 12 months and create a visualization"
→ Root agent retrieves data, DS agent creates trend analysis with charts

"Build a predictive model for customer churn"
→ Root agent extracts features, DS agent trains and evaluates model

"Compare revenue across product categories with statistical testing"
→ Root agent queries data, DS agent performs statistical analysis
```

## Architecture

### Common Foundation
Both implementations use:
- **Google Agent Development Kit (ADK)**: Framework for building AI agents
- **Gemini 2.5 Flash**: Large language model for natural language understanding
- **Vertex AI**: Google Cloud's AI platform integration

### ADK Agent Architecture
```
ADK Agent (bigquery_agent)
└── BigQuery Toolset (ADK)
    ├── list_dataset_ids
    ├── get_dataset_info
    ├── list_table_ids
    ├── get_table_info
    └── execute_sql
```

### Multi-Agent System Architecture
```
Root Agent (bigquery_ds_agent)
├── BigQuery Tools (MCP Toolbox)
│   ├── bigquery-list-dataset-ids
│   ├── bigquery-get-dataset-info
│   ├── bigquery-list-table-ids
│   ├── bigquery-get-table-info
│   ├── bigquery-execute-sql
│   ├── bigquery-conversational-analytics
│   ├── bigquery-forecast
│   └── bigquery-sql
└── DS Sub-Agent (ds_agent)
    ├── Python Code Execution
    ├── Data Visualization
    └── Statistical Analysis
```

## Project Structure

```
bq-agent-app/
├── pyproject.toml                   # uv package configuration
├── uv.lock                          # Dependency lock file
├── bq_agent_adk/                    # ADK BigQuery Agent
│   ├── agent.py                     # Main agent with ADK BigQuery tools
│   ├── credentials.py               # Authentication configuration
│   └── .env.example                 # Environment template
├── bq_multi_agent_app/              # Multi-Agent System
│   ├── agent.py                     # Root agent with MCP integration
│   ├── tools.py                     # MCP BigQuery tools + DS agent wrapper
│   ├── prompts.py                   # Agent instructions
│   ├── mcp-toolbox/                 # MCP server installation
│   ├── sub_agents/
│   │   └── ds_agents/
│   │       ├── agent.py             # Data science agent
│   │       └── prompts.py           # DS agent instructions
│   └── .env.example                 # Environment template
├── vertex_extensions_setup/         # Vertex AI Extensions Management
│   ├── utils.py                     # Shared utilities
│   ├── setup_vertex_extensions.py   # Create extensions
│   ├── cleanup_vertex_extensions.py # Clean up extensions
│   └── VERTEX_EXTENSIONS_GUIDE.md   # Detailed guide
└── README.md
```

## Prerequisites

- **Python 3.11+**
- **uv** package manager ([installation guide](https://docs.astral.sh/uv/getting-started/installation/))
- **Google Cloud Project** with BigQuery enabled
- **Google Cloud credentials**

## Authentication Options

<details>
<summary>Click to expand authentication details</summary>

### 1. Application Default Credentials (Recommended)
```bash
gcloud auth application-default login
```

### 2. OAuth2 Authentication (ADK Agent only)
```env
# In .env file
OAUTH_CLIENT_ID=your_client_id
OAUTH_CLIENT_SECRET=your_client_secret
```

### 3. Service Account (ADK Agent only)
1. Download service account key as `service_account_key.json`
2. Update `CREDENTIALS_TYPE` in `credentials.py`

</details>

## Configuration

### Write Modes (ADK Agent only)
Control BigQuery write access in `credentials.py`:
- **ALLOWED**: Full write capabilities
- **BLOCKED**: Read-only mode (recommended for production)
- **PROTECTED**: Temporary data writes only

## Deployment

The Multi-Agent System requires both the MCP Toolbox and the Agent to be deployed. You can choose to run each component locally or deploy to Cloud Run based on your needs.

### Step 1: Deploy the MCP Toolbox

The MCP Toolbox provides BigQuery connectivity for the agent.

#### Option A: Run MCP Toolbox Locally
```bash
# Set environment variables
cp .env.example .env
export $(cat .env | grep -v '^#' | xargs)

# Start the MCP server
./mcp_toolbox_setup/toolbox --prebuilt bigquery
```

#### Option B: Deploy MCP Toolbox to Cloud Run
```bash
# Set environment variables
cp .env.example .env
export $(cat .env | grep -v '^#' | xargs)

# Setup and deploy
cd mcp_toolbox_setup
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
cp .env.example bq_multi_agent_app/.env
export $(cat .env | grep -v '^#' | xargs)

uv run adk deploy agent_engine \
  --project=your-project-id \
  --region=us-central1 \
  --staging_bucket="gs://your-project-id-adk-staging" \
  --display_name="BigQuery Multi-Agent App" \
  --trace_to_cloud \
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
