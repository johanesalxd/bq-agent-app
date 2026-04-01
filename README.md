# BigQuery Agent with Google ADK

A multi-agent system for BigQuery analytics and data science, built with the
Google Agent Development Kit (ADK). Users interact in natural language; the
agent handles dataset discovery, analytics via the Conversational Analytics API,
advanced Python analysis, BigQuery ML operations, and conversational analytics
via pre-configured BQ Data Agents.

## Quick Start

**1. Authenticate**
```bash
gcloud auth application-default login
```

**2. Clone and install**
```bash
git clone https://github.com/johanesalxd/bq-agent-app.git
cd bq-agent-app
uv sync
```

**3. Configure**
```bash
cp .env.example .env
# Required: set GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION,
#           GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET
```

**4. Run**
```bash
uv run adk web
```

## How It Works

The root agent uses intent-based routing to send each request to the right tool
or sub-agent. The vast majority of queries go through the **default path** using
the Conversational Analytics (CA) API, which is the same backend powering
BQ Agents and Looker Conversational Analytics.

```
User: "Show me sales by region last month"
→ Root agent infers: standard data question
→ Calls ask_data_insights with table references
→ Returns: data table + Vega-Lite chart (rendered natively in Gemini Enterprise)

User: "Run a significance test comparing region performance"
→ Root agent infers: statistical analysis, needs Python
→ Delegates to DS sub-agent
→ DS agent: execute_sql (get data) → Code Interpreter (scipy, statsmodels)
→ Returns: statistical report + matplotlib charts

User: "Create a churn prediction model"
→ Root agent infers: BQML task
→ Delegates to BQML sub-agent
→ BQML agent: RAG lookup → generate SQL → user approval → execute

User: "Ask my sales data agent about Q4 performance"
→ Root agent infers: pre-configured Data Agent
→ Uses DataAgentToolset → ask_data_agent
→ Returns: CA API response from pre-configured agent
```

### Routing Logic (intent-based, not keyword-based)

| Path | When | Tool/Agent |
|------|------|-----------|
| **Default** | Counts, aggregations, trends, comparisons, simple charts | `ask_data_insights` (CA API) |
| **Advanced** | Statistical testing, custom Python, multi-step analysis | DS sub-agent |
| **BQML** | ML model creation, training, evaluation, predictions | BQML sub-agent |
| **Data Agent** | User references a pre-configured BQ Data Agent | `DataAgentToolset` |

## Architecture

```
Root Agent (bigquery_ds_agent)
├── BigQueryToolset [ca_toolset — CA API + discovery, read-only]
│   Tools: ask_data_insights, list_dataset_ids, get_dataset_info,
│          list_table_ids, get_table_info, search_catalog
│
├── DataAgentToolset [pre-configured BQ Data Agents, per-user OAuth]
│   Tools: list_accessible_data_agents, get_data_agent_info, ask_data_agent
│
├── Memory Tools [Vertex AI Memory Bank]
│   Tools: PreloadMemoryTool, LoadMemoryTool
│
└── Sub-agents:
    ├── DS Sub-Agent (advanced analysis)
    │   ├── BigQueryToolset [ds_toolset — advanced tools, read-only]
    │   │   Tools: execute_sql, forecast, analyze_contribution,
    │   │          detect_anomalies, list_dataset_ids, get_dataset_info,
    │   │          list_table_ids, get_table_info, get_job_info
    │   ├── Code Interpreter [VertexAiCodeExecutor]
    │   │   Libs: matplotlib, numpy, pandas, scipy, seaborn, sklearn, statsmodels
    │   └── load_artifacts
    │
    └── BQML Sub-Agent
        ├── BigQueryToolset [bqml_toolset — SQL + discovery, write-enabled]
        │   Tools: execute_sql, list_dataset_ids, get_dataset_info,
        │          list_table_ids, get_table_info
        └── RAG Response [BQML documentation corpus]
```

### Technology

| Component | Details |
|-----------|---------|
| Framework | Google ADK 1.28+ |
| Model | Gemini 3 Flash Preview |
| CA API | `ask_data_insights` from `BigQueryToolset` — same backend as BQ Agents |
| Auth | Per-user OAuth passthrough (BigQuery + Data Agents) |
| Code execution | `VertexAiCodeExecutor` + Code Interpreter Extension |
| BQML docs | Vertex AI RAG corpus (`text-embedding-005`) |
| Memory | Vertex AI Memory Bank via `PreloadMemoryTool` / `LoadMemoryTool` |

## Prerequisites

- Python 3.12
- `uv` package manager ([install](https://docs.astral.sh/uv/getting-started/installation/))
- Google Cloud project with BigQuery enabled
- Application Default Credentials (`gcloud auth application-default login`)

## BQML Agent Setup

### Required APIs

```bash
gcloud services enable aiplatform.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
```

### Required IAM roles

- Vertex AI User
- BigQuery User
- BigQuery Data Viewer

### RAG Corpus

The BQML agent uses a Vertex AI RAG corpus for documentation lookup. Create it
once and the corpus name is written to your `.env` automatically:

```bash
uv run python setup/rag_corpus/create_bqml_corpus.py
```

Default region: `us-west4` (Vertex AI RAG capacity).

### Code Interpreter Extension

`VertexAiCodeExecutor` requires a pre-provisioned Code Interpreter Extension.
Set it up once and record the resource name in `.env`:

```bash
python setup/vertex_extensions/setup_vertex_extensions.py
# Copy the printed resource name to CODE_INTERPRETER_EXTENSION_NAME in .env
```

See [Vertex Extensions Setup Guide](setup/vertex_extensions/VERTEX_EXTENSIONS_GUIDE.md)
for cleanup and management.

## Deployment

### Local development

```bash
uv run adk web
```

### Local development with Memory Bank

Memory Bank requires an Agent Engine instance for storage. Deploy once to get
the instance, then point your local run at it:

```bash
# 1. Deploy (see Agent Engine section below)
uv run python deployment/deploy.py

# 2. Copy the numeric ID from AGENT_ENGINE_RESOURCE_NAME to AGENT_ENGINE_ID in .env
#    Example: "projects/123/locations/us-central1/reasoningEngines/456789" → 456789

# 3. Run locally with Memory Bank
uv run adk web --memory_service_uri=agentengine://$AGENT_ENGINE_ID
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

### Agent Engine (Python SDK)

The canonical deployment path uses the `AdkApp` Python SDK wrapper.
Memory Bank is configured automatically by `deploy.py`.

```bash
# Set GCS_STAGING_BUCKET in .env, then:
uv run python deployment/deploy.py
```

The script prints the fully-qualified resource name. Copy it to
`AGENT_ENGINE_RESOURCE_NAME` in `.env`.

**Memory Bank topics configured at deployment:**
- `USER_PERSONAL_INFO` — team, role, organizational context
- `USER_PREFERENCES` — chart style, analysis preferences, currency
- `KEY_CONVERSATION_DETAILS` — milestones and conclusions from past sessions
- `EXPLICIT_INSTRUCTIONS` — persistent instructions ("always use sales_data dataset")
- `data_analysis_context` (custom) — frequently used tables, domain context, recurring questions

**Smoke test after deployment:**
```bash
uv run python deployment/test_deployment.py
```

**Manage sessions via REST:**
```bash
ACCESS_TOKEN=$(gcloud auth print-access-token)
# List sessions
curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
  "https://us-central1-aiplatform.googleapis.com/v1beta1/$AGENT_ENGINE_RESOURCE_NAME/sessions"
# Delete a session
curl -s -X DELETE -H "Authorization: Bearer $ACCESS_TOKEN" \
  "https://us-central1-aiplatform.googleapis.com/v1beta1/$AGENT_ENGINE_RESOURCE_NAME/sessions/SESSION_ID"
```

### Gemini Enterprise registration

After deploying to Agent Engine, register the agent with Gemini Enterprise
(formerly Agentspace) to surface it in the Gemini Enterprise console.
Gemini Enterprise renders Vega-Lite chart specs from `ask_data_insights` natively.

**OAuth setup (required first):**

In Google Cloud Console → APIs & Services → Credentials → your OAuth 2.0 Client:
add these authorised redirect URIs:
- `https://vertexaisearch.cloud.google.com/oauth-redirect`
- `https://vertexaisearch.cloud.google.com/static/oauth/oauth.html`

**Register:**
```bash
# Set GEMINI_ENTERPRISE_APP_ID and AGENT_ENGINE_RESOURCE_NAME in .env, then:
chmod +x deployment/register_gemini_enterprise.sh
./deployment/register_gemini_enterprise.sh
```

## Example Interactions

**Standard analytics (default path — CA API)**
```
"What datasets are available in my project?"
"Show me the schema of the sales_data table"
"Find the top 10 customers by revenue this year"
"Show monthly sales trend as a bar chart"
```

**Advanced analysis (DS sub-agent)**
```
"Compare revenue across regions with statistical significance testing"
"Run anomaly detection on daily order counts"
"Forecast sales for the next 30 days and plot confidence intervals"
"Analyze contribution of each product category to revenue change"
```

**BigQuery ML (BQML sub-agent)**
```
"Create a logistic regression model for customer churn prediction"
"What BQML model types are available for forecasting?"
"List existing BQML models in my dataset"
"Evaluate the churn model and show metrics"
```

## Project Structure

```
bq-agent-app/
├── pyproject.toml
├── .env.example
├── bq_multi_agent_app/
│   ├── agent.py                  # Root agent (Memory Bank, sub-agents, CA toolset)
│   ├── tools.py                  # ca_toolset, ds_toolset, data_agent_toolset
│   ├── prompts.py                # Root agent instructions (intent-based routing)
│   └── sub_agents/
│       ├── bqml_agents/          # BigQuery ML sub-agent
│       │   ├── agent.py
│       │   ├── prompts.py
│       │   └── tools.py          # bqml_toolset (execute_sql + discovery, write-enabled)
│       └── ds_agents/            # Data Science sub-agent
│           ├── agent.py          # ds_toolset + Code Interpreter + load_artifacts
│           └── prompts.py
├── deployment/
│   ├── deploy.py                 # Agent Engine deployment with Memory Bank config
│   ├── register_gemini_enterprise.sh
│   └── test_deployment.py
├── setup/
│   ├── rag_corpus/
│   │   └── create_bqml_corpus.py
│   └── vertex_extensions/
│       ├── setup_vertex_extensions.py
│       ├── cleanup_vertex_extensions.py
│       ├── utils.py
│       └── VERTEX_EXTENSIONS_GUIDE.md
└── tests/
    ├── conftest.py
    ├── test_agent.py
    ├── test_bqml_tools.py
    ├── test_prompts.py
    └── test_tools.py
```

## Security

- Root and DS toolsets are read-only (`WriteMode.BLOCKED`)
- BQML toolset is write-enabled only for the BQML sub-agent (required for `CREATE MODEL`)
- Per-user OAuth ensures each user's IAM permissions are enforced
- Store credentials in `.env` (git-ignored); never hardcode secrets
- Minimum required IAM roles only

## Related Resources

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [ADK BigQuery Tools](https://google.github.io/adk-docs/integrations/bigquery/)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
- [Gemini Enterprise](https://cloud.google.com/products/gemini/enterprise)
- [Conversational Analytics API](https://cloud.google.com/bigquery/docs/conversational-analytics-overview)
