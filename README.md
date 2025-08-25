# BigQuery Agent with Google ADK

A powerful AI-powered data analysis agent that combines Google BigQuery with the Google Agent Development Kit (ADK) to enable natural language interactions with your data warehouse. Now available in two implementations: direct BigQuery integration and Model Context Protocol (MCP) support.

## Overview

This project demonstrates the integration of BigQuery with Google's Agent Development Kit, creating intelligent agents that can understand natural language queries and execute SQL operations on BigQuery datasets. The project includes two agent implementations:

1. **Direct BigQuery Agent** (`bq-agent-app/`): Direct integration with BigQuery APIs
2. **MCP BigQuery Agent** (`bq-agent-app-mcp/`): Uses Model Context Protocol for enhanced tool interoperability

Both agents leverage Google's Gemini models to provide conversational data analysis capabilities.

## Features

### Current Capabilities
- 🔍 **Dataset Discovery**: List and explore BigQuery datasets
- 📊 **Table Analysis**: Get detailed information about tables and their schemas
- 🔎 **SQL Execution**: Execute complex SQL queries through natural language
- 🤖 **AI-Powered**: Uses Gemini 2.5 Flash for intelligent query understanding
- 🔐 **Flexible Authentication**: Multiple authentication methods supported
- 🔗 **MCP Integration**: Model Context Protocol support for enhanced tool interoperability
- 🛠️ **Dual Implementation**: Choose between direct BigQuery integration or MCP-based approach

### Coming Soon
- 📈 **Advanced Analytics**: Extended data visualization and analysis capabilities

## Architecture

The project provides two agent implementations:

### Direct BigQuery Agent (`bq-agent-app/`)
- **Google Agent Development Kit (ADK)**: Framework for building AI agents
- **BigQuery Toolset**: Specialized tools for BigQuery operations
- **Gemini 2.5 Flash**: Large language model for natural language understanding
- **Python**: Core implementation language
- **Vertex AI**: Google Cloud's AI platform integration

### MCP BigQuery Agent (`bq-agent-app-mcp/`)
- **Google Agent Development Kit (ADK)**: Framework for building AI agents
- **MCP Toolbox**: Model Context Protocol for tool interoperability
- **Gemini 2.5 Flash**: Large language model for natural language understanding
- **Python**: Core implementation language
- **Vertex AI**: Google Cloud's AI platform integration

## Prerequisites

- Python 3.8 or higher
- Google Cloud Project with BigQuery enabled
- Google Cloud credentials (one of the authentication methods below)

## Installation

### Common Setup

1. Clone the repository:
```bash
git clone https://github.com/johanesalxd/bq-agent-app.git
cd bq-agent-app
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

### For Direct BigQuery Agent (`bq-agent-app/`)

3. Install dependencies:
```bash
pip install google-adk
```

### For MCP BigQuery Agent (`bq-agent-app-mcp/`)

3. Install dependencies:
```bash
pip install google-adk toolbox-core
```

4. Install MCP Toolbox:
```bash
cd bq-agent-app-mcp/mcp-toolbox
chmod +x install-mcp-toolbox.sh
./install-mcp-toolbox.sh
```

## Authentication Setup

The agent supports three authentication methods:

### 1. Application Default Credentials (Recommended)
```bash
gcloud auth application-default login
```

### 2. OAuth2 Authentication
Set up OAuth2 credentials in your `.env` file:
```env
OAUTH_CLIENT_ID=your_client_id
OAUTH_CLIENT_SECRET=your_client_secret
```

Update `credentials.py`:
```python
CREDENTIALS_TYPE = AuthCredentialTypes.OAUTH2
```

### 3. Service Account
1. Download your service account key as `service_account_key.json`
2. Update `credentials.py`:
```python
CREDENTIALS_TYPE = AuthCredentialTypes.SERVICE_ACCOUNT
```

## Configuration

### Write Modes
The agent supports different write access levels:

- **ALLOWED**: Full write capabilities (current setting)
- **BLOCKED**: Read-only mode (default safety setting)
- **PROTECTED**: Temporary data writes only

To change the write mode, modify the `tool_config` in `credentials.py`:
```python
tool_config = BigQueryToolConfig(write_mode=WriteMode.BLOCKED)  # For read-only
```

## Usage

### Running the Direct BigQuery Agent

1. Configure your authentication method in `credentials.py`
2. Run the agent:
```bash
adk web # or adk run
```

### Running the MCP BigQuery Agent

1. Start the MCP Toolbox server:
```bash
./bq-agent-app-mcp/mcp-toolbox/toolbox --prebuilt bigquery
```

1. Run the agent:
```bash
adk web # or adk run
```

### Example Interactions

```
User: "What datasets are available in my project?"
Agent: Lists all BigQuery datasets with descriptions

User: "Show me the schema of the sales_data table"
Agent: Displays table schema, column types, and metadata

User: "Find the top 10 customers by revenue this year"
Agent: Executes appropriate SQL query and returns results
```

## Available BigQuery Tools

The agent has access to the following BigQuery operations:

- `list_dataset_ids`: List all datasets in the project
- `get_dataset_info`: Get detailed information about a specific dataset
- `list_table_ids`: List all tables in a dataset
- `get_table_info`: Get schema and metadata for a specific table
- `execute_sql`: Execute SQL queries on BigQuery

## Project Structure

```
bq-agent-app/
├── bq-agent-app/                    # Direct BigQuery Agent
│   ├── __init__.py
│   ├── agent.py                     # Main agent definition and BigQuery toolset setup
│   ├── credentials.py               # BigQuery credentials configuration
│   └── .env                         # Environment variables (create this)
├── bq-agent-app-mcp/                # MCP BigQuery Agent
│   ├── __init__.py
│   ├── agent.py                     # MCP-based agent definition
│   ├── .env                         # Vertex AI configuration
│   └── mcp-toolbox/                 # MCP Toolbox installation
│       └── install-mcp-toolbox.sh   # Installation script
├── .gitignore
└── README.md                        # This file
```

## Choosing Between Implementations

### Use Direct BigQuery Agent when:
- You need direct control over BigQuery API calls
- You want to customize authentication methods extensively
- You prefer a simpler setup without additional server components

### Use MCP BigQuery Agent when:
- You want enhanced tool interoperability through MCP
- You're building a system that integrates with other MCP-compatible tools
- You prefer the standardized MCP protocol for tool communication
- You want to leverage Vertex AI's enhanced capabilities

## Security Considerations

- Always use the minimum required permissions for your use case
- Consider using `WriteMode.BLOCKED` or `WriteMode.PROTECTED` in production
- Store credentials securely and never commit them to version control
- Review and audit SQL queries executed by the agent

## Related Resources

- [Google Agent Development Kit Documentation](https://cloud.google.com/adk)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [Blog Post: BigQuery meets Google ADK and MCP](https://cloud.google.com/blog/products/ai-machine-learning/bigquery-meets-google-adk-and-mcp)

---

*Built with ❤️ using Google Agent Development Kit and BigQuery*
