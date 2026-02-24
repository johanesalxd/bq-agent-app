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

# Install dependencies
uv sync

# Activate environment
source .venv/bin/activate
```

3. **Configure Environment**
```bash
cp .env.example .env
# Edit .env and set your project details:
# GOOGLE_CLOUD_PROJECT=your-project-id
# GOOGLE_CLOUD_LOCATION=us-central1
```

4. **Run**
```bash
uv run adk web
```

BigQuery access uses Application Default Credentials (ADC) automatically — no additional server or toolbox setup required.

## BQML Agent Setup

This section covers setting up the BQML agent with RAG corpus integration for enhanced BigQuery ML capabilities.

### Prerequisites for BQML Agent

In addition to the basic prerequisites, the BQML agent requires:

1. **Additional APIs enabled**:
   - Vertex AI API
   - BigQuery API (already required)
   - Cloud Resource Manager API

2. **Additional permissions** for your account:
   - Vertex AI User
   - BigQuery User
   - BigQuery Data Viewer

3. **Enable required APIs**:
   ```bash
   gcloud services enable aiplatform.googleapis.com
   gcloud services enable bigquery.googleapis.com
   gcloud services enable cloudresourcemanager.googleapis.com
   ```

### BQML Environment Configuration

```bash
# BQML Agent configuration (leave empty initially)
BQML_RAG_CORPUS_NAME=
```

### RAG Corpus Setup

The BQML agent uses a RAG corpus for enhanced BQML documentation access:

```bash
uv run python setup/rag_corpus/create_bqml_corpus.py
```

This script creates a Vertex AI RAG corpus with text-embedding-005, ingests BQML documentation, and writes the corpus name to your `.env` file automatically.

### Region Selection for BQML

**Important**: The BQML setup uses `us-west4` as the default region for Vertex AI RAG due to capacity availability.

## Additional Guides

- [Agentspace Management Guide](setup/agentspace/AGENTSPACE_MANAGEMENT_GUIDE.md) - Manage Google Cloud Agentspace agents and ReasoningEngines
- [Vertex Extensions Setup Guide](setup/vertex_extensions/VERTEX_EXTENSIONS_GUIDE.md) - Set up Vertex AI Extensions for code interpretation

## Implementation

This project provides a **Multi-Agent System** for BigQuery analytics with advanced data science capabilities.

| Feature | Multi-Agent System |
|---------|-------------------|
| **Directory** | `bq_multi_agent_app/` |
| **BigQuery Operations** | ✅ Built-in ADK BigQueryToolset |
| **Python Data Science** | ✅ |
| **Statistical Analysis** | ✅ |
| **Data Visualization** | ✅ |
| **Multi-Agent Orchestration** | ✅ |
| **BQML Integration** | ✅ |

### Key Benefits

- **Zero Infrastructure**: BigQuery tools use ADC directly — no external server required
- **Advanced Analytics**: Complete data science workflows with analysis and visualizations
- **Multi-Agent Architecture**: Root agent orchestrates specialized sub-agents for different tasks

## Core Features

- 🔍 **Dataset Discovery**: List and explore BigQuery datasets
- 📊 **Table Analysis**: Get detailed schema and metadata information
- 🔎 **SQL Execution**: Execute complex SQL queries through natural language
- 🤖 **AI-Powered**: Uses Gemini 3 Flash Preview for intelligent query understanding
- 🔐 **ADC Authentication**: Application Default Credentials for seamless auth

## Advanced Features

- 🎯 **Multi-Agent Orchestration**: Root agent delegates tasks to specialized sub-agents
- 🐍 **Python Analytics**: Stateful code execution for advanced data science workflows
- 📈 **Data Visualization**: Automated chart generation with matplotlib
- 🧠 **Statistical Analysis**: Comprehensive statistical testing and modeling
- 📊 **Time Series Forecasting**: Built-in forecasting capabilities via `AI.FORECAST`
- 💬 **Natural Language Queries**: `ask_data_insights` for NL-to-BQ analysis

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

**BQML Operations**
```
"Create a logistic regression model for customer churn prediction"
→ BQML agent queries RAG corpus, generates CREATE MODEL statement

"What BQML model types are available for forecasting?"
→ BQML agent retrieves ARIMA_PLUS and time series model documentation

"List existing BQML models in my dataset"
→ Root agent queries BigQuery information schema for ML models
```

## Architecture

### Foundation
- **Google Agent Development Kit (ADK) 1.25**: Framework for building AI agents
- **Gemini 3 Flash Preview**: Large language model for natural language understanding
- **ADK BigQueryToolset**: Built-in BigQuery integration via ADC (no external server)
- **Vertex AI**: Google Cloud AI platform integration

### Multi-Agent System Architecture
```
Root Agent (bigquery_ds_agent)
├── BigQueryToolset (ADK built-in, ADC auth)
│   ├── list_dataset_ids        # Dataset discovery
│   ├── get_dataset_info        # Dataset metadata
│   ├── list_table_ids          # Table discovery
│   ├── get_table_info          # Table schema
│   ├── execute_sql             # SQL execution
│   ├── forecast                # AI.FORECAST time series
│   └── ask_data_insights       # Natural language queries
├── DS Sub-Agent (ds_agent)
│   ├── Python Code Execution
│   ├── Data Visualization
│   └── Statistical Analysis
└── BQML Sub-Agent (bqml_agent)
    ├── BigQueryToolset (ADK built-in)
    ├── RAG Response             # BQML documentation queries
    └── Model Listing            # BigQuery ML model discovery
```

## Project Structure

```
bq-agent-app/
├── pyproject.toml                   # uv package configuration
├── uv.lock                          # Dependency lock file
├── .env.example                     # Environment variable template
├── bq_multi_agent_app/              # Multi-Agent System
│   ├── agent.py                     # Root agent
│   ├── tools.py                     # BigQueryToolset + agent wrappers
│   ├── prompts.py                   # Root agent instructions
│   └── sub_agents/
│       ├── ds_agents/               # Data Science Agent
│       │   ├── agent.py
│       │   └── prompts.py
│       └── bqml_agents/             # BigQuery ML Agent
│           ├── agent.py
│           ├── prompts.py
│           └── tools.py
└── setup/                           # Optional setup tools
    ├── rag_corpus/                  # BQML RAG Corpus Setup
    │   ├── create_bqml_corpus.py
    │   └── test_rag.py
    ├── vertex_extensions/           # Vertex AI Extensions
    │   ├── setup_vertex_extensions.py
    │   ├── cleanup_vertex_extensions.py
    │   ├── utils.py
    │   └── VERTEX_EXTENSIONS_GUIDE.md
    └── agentspace/                  # Agentspace Management
        ├── manage_agentspace.sh
        ├── test_agent_engine.py
        └── AGENTSPACE_MANAGEMENT_GUIDE.md
```

## Prerequisites

- **Python 3.12**
- **uv** package manager ([installation guide](https://docs.astral.sh/uv/getting-started/installation/))
- **Google Cloud Project** with BigQuery enabled
- **Application Default Credentials** (`gcloud auth application-default login`)

## Deployment

### Local Development
```bash
cp .env.example .env
# Set GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION in .env
uv run adk web
```

### Cloud Run
```bash
uv run adk deploy cloud_run \
  --project=your-project-id \
  --region=us-central1 \
  --service_name=bq-agent-app \
  --trace_to_cloud \
  --with_ui \
  ./bq_multi_agent_app
```

### Agent Engine
```bash
uv run adk deploy agent_engine \
  --staging_bucket="gs://your-project-id-adk-staging" \
  --display_name="BigQuery Multi-Agent App" \
  --trace_to_cloud \
  --env_file=.env \
  ./bq_multi_agent_app
```

## Agentspace Management

Once deployed to Agent Engine, manage via the included tools:

```bash
cd setup/agentspace
chmod +x manage_agentspace.sh
./manage_agentspace.sh list       # List all agents
./manage_agentspace.sh deploy     # Deploy new agent
./manage_agentspace.sh help       # Show all commands
```

See [Agentspace Management Guide](setup/agentspace/AGENTSPACE_MANAGEMENT_GUIDE.md) for details.

## Security Considerations

- Use minimum required permissions for your GCP service account
- BigQueryToolset is configured with `WriteMode.BLOCKED` by default (read-only)
- Review SQL queries executed by agents before enabling write access
- Store credentials securely using ADC or service account keys

## Related Resources

- [Google Agent Development Kit Documentation](https://google.github.io/adk-docs/)
- [ADK BigQuery Tools](https://google.github.io/adk-docs/integrations/bigquery/)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)

---

*Built with Google Agent Development Kit, BigQuery, and Gemini*
