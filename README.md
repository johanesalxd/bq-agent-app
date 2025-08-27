# BigQuery Agent with Google ADK

A powerful AI-powered data analysis agent that combines Google BigQuery with the Google Agent Development Kit (ADK) to enable natural language interactions with your data warehouse. Choose from three implementations based on your needs.

## Quick Start

1. **Clone and Setup**
```bash
git clone https://github.com/johanesalxd/bq-agent-app.git
cd bq-agent-app
./setup.sh
source .venv/bin/activate
```

2. **Authentication**
```bash
gcloud auth application-default login
```

3. **Choose Your Implementation** (see comparison below)

## Available Implementations

| Feature | Direct Agent | MCP Agent | Multi-Agent System |
|---------|-------------|-----------|-------------------|
| **Directory** | `bq_agent_app/` | `bq_agent_app_mcp/` | `bq_multi_agent_app/` |
| **Setup Complexity** | Simple | Moderate | Simple |
| **BigQuery Operations** | ✅ | ✅ | ✅ |
| **MCP Protocol Support** | ❌ | ✅ | ❌ |
| **Python Data Science** | ❌ | ❌ | ✅ |
| **Statistical Analysis** | ❌ | ❌ | ✅ |
| **Data Visualization** | ❌ | ❌ | ✅ |
| **Multi-Agent Orchestration** | ❌ | ❌ | ✅ |
| **Additional Dependencies** | None | MCP Toolbox | None |

### When to Use Which

- **Direct Agent**: Basic BigQuery queries and exploration, simple setup
- **MCP Agent**: Tool interoperability, integration with other MCP-compatible systems
- **Multi-Agent System**: Advanced analytics, data science workflows, comprehensive analysis with visualizations

## Core Features (All Implementations)

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

## Usage

### Running Any Implementation

1. **Configure Environment**:
```bash
# For [agent]/.env
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```

2. **Start MCP Server** (MCP Agent only):
```bash
./bq_agent_app_mcp/mcp-toolbox/toolbox --prebuilt bigquery
```

3. **Run the Agent**:
```bash
adk web # or adk run
```

### Example Interactions

**Basic Operations (All Implementations)**
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
All implementations use:
- **Google Agent Development Kit (ADK)**: Framework for building AI agents
- **BigQuery Toolset**: Direct access to BigQuery operations
- **Gemini 2.5 Flash**: Large language model for natural language understanding
- **Vertex AI**: Google Cloud's AI platform integration

### Multi-Agent System Architecture
```
Root Agent (bigquery_ds_agent)
├── BigQuery Tools (direct access)
│   ├── list_dataset_ids
│   ├── get_dataset_info
│   ├── list_table_ids
│   ├── get_table_info
│   └── execute_sql
└── DS Sub-Agent (ds_agent)
    ├── Python Code Execution
    ├── Data Visualization
    └── Statistical Analysis
```

## Project Structure

```
bq-agent-app/
├── bq_agent_app/                    # Direct BigQuery Agent
├── bq_agent_app_mcp/                # MCP BigQuery Agent
│   └── mcp-toolbox/                 # MCP server installation
├── bq_multi_agent_app/              # Multi-Agent System
│   ├── agent.py                     # Root agent with orchestration
│   ├── subagents.py                 # Data science sub-agent
│   ├── prompts.py                   # Agent instructions
│   ├── tools.py                     # BigQuery toolset
│   └── credentials.py               # Authentication config
├── setup.sh                         # Quick setup script
└── README.md
```

## Prerequisites

- Python 3.8 or higher
- Google Cloud Project with BigQuery enabled
- Google Cloud credentials

## Authentication Options

<details>
<summary>Click to expand authentication details</summary>

### 1. Application Default Credentials (Recommended)
```bash
gcloud auth application-default login
```

### 2. OAuth2 Authentication
```env
# In .env file
OAUTH_CLIENT_ID=your_client_id
OAUTH_CLIENT_SECRET=your_client_secret
```

### 3. Service Account
1. Download service account key as `service_account_key.json`
2. Update `CREDENTIALS_TYPE` in `credentials.py`

</details>

## Configuration

### Write Modes
Control BigQuery write access in `credentials.py`:
- **ALLOWED**: Full write capabilities
- **BLOCKED**: Read-only mode (recommended for production)
- **PROTECTED**: Temporary data writes only

## Security Considerations

- Use minimum required permissions
- Store credentials securely
- Review SQL queries executed by agents
- Consider read-only mode for production

## Related Resources

- [Google Agent Development Kit Documentation](https://cloud.google.com/adk)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [Blog Post: BigQuery meets Google ADK and MCP](https://cloud.google.com/blog/products/ai-machine-learning/bigquery-meets-google-adk-and-mcp)

---

*Built with ❤️ using Google Agent Development Kit and BigQuery*
