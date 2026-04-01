# BigQuery Agent with Google ADK

A multi-agent system for BigQuery analytics and data science, built with the
Google Agent Development Kit (ADK). Users interact in natural language; the
agent handles dataset discovery, SQL execution, data science workflows, BigQuery
ML operations, and conversational analytics.

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
# Required: set GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION
```

**4. Run**
```bash
uv run adk web
```

BigQuery access uses Application Default Credentials — no additional toolbox or
server setup required.

## Architecture

```
Root Agent (bigquery_ds_agent)
├── BigQueryToolset        — dataset/table discovery, SQL, forecasting (ADC)
├── call_data_science_agent — Python code execution, statistics, visualization
├── data_agent_toolset     — conversational analytics via BQ Data Agents (OAuth)
└── BQML Sub-Agent
    ├── BigQueryToolset    — BigQuery ML queries
    └── RAG Response       — BQML documentation lookup
```

### Technology

| Component | Details |
|-----------|---------|
| Framework | Google ADK 1.28+ |
| Model | Gemini 3 Flash Preview |
| BigQuery | ADK `BigQueryToolset` (read-only, `WriteMode.BLOCKED`) |
| Auth | Per-user OAuth passthrough (BigQuery + Data Agents) |
| Code execution | `VertexAiCodeExecutor` + Code Interpreter Extension |
| BQML docs | Vertex AI RAG corpus (`text-embedding-005`) |

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

The canonical deployment path uses the `AdkApp` Python SDK wrapper:

```bash
# Set GCS_STAGING_BUCKET in .env, then:
uv run python deployment/deploy.py
```

The script prints the fully-qualified resource name. Copy it to
`AGENT_ENGINE_RESOURCE_NAME` in `.env`.

**Smoke test after deployment:**
```bash
uv run python deployment/test_deployment.py
```

**Manage sessions via REST:**
```bash
# List sessions
ACCESS_TOKEN=$(gcloud auth print-access-token)
curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
  "https://us-central1-aiplatform.googleapis.com/v1beta1/$AGENT_ENGINE_RESOURCE_NAME/sessions"

# Delete a session
curl -s -X DELETE -H "Authorization: Bearer $ACCESS_TOKEN" \
  "https://us-central1-aiplatform.googleapis.com/v1beta1/$AGENT_ENGINE_RESOURCE_NAME/sessions/SESSION_ID"
```

### Gemini Enterprise registration

After deploying to Agent Engine, register the agent with Gemini Enterprise
(formerly Agentspace) to surface it in the Gemini Enterprise console:

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

**Basic queries**
```
"What datasets are available in my project?"
"Show me the schema of the sales_data table"
"Find the top 10 customers by revenue this year"
```

**Data science**
```
"Analyze sales trends over the last 12 months and create a visualization"
"Build a predictive model for customer churn"
"Compare revenue across product categories with statistical testing"
```

**BigQuery ML**
```
"Create a logistic regression model for customer churn prediction"
"What BQML model types are available for forecasting?"
"List existing BQML models in my dataset"
```

## Project Structure

```
bq-agent-app/
├── pyproject.toml
├── .env.example
├── bq_multi_agent_app/
│   ├── agent.py                  # Root agent
│   ├── tools.py                  # BigQueryToolset + agent wrappers
│   ├── prompts.py                # Root agent instructions
│   └── sub_agents/
│       ├── bqml_agents/          # BigQuery ML sub-agent
│       │   ├── agent.py
│       │   ├── prompts.py
│       │   └── tools.py
│       └── ds_agents/            # Data Science sub-agent
│           ├── agent.py
│           └── prompts.py
├── deployment/
│   ├── deploy.py                 # Agent Engine deployment (Python SDK AdkApp)
│   ├── register_gemini_enterprise.sh  # Gemini Enterprise registration
│   └── test_deployment.py        # Smoke test for deployed instance
├── setup/
│   ├── rag_corpus/
│   │   └── create_bqml_corpus.py # Vertex AI RAG corpus creation
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

- `BigQueryToolset` is read-only (`WriteMode.BLOCKED`) by default
- Per-user OAuth ensures each user's IAM permissions are enforced
- Store credentials in `.env` (git-ignored); never hardcode secrets
- Minimum required IAM roles only

## Related Resources

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [ADK BigQuery Tools](https://google.github.io/adk-docs/integrations/bigquery/)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
- [Gemini Enterprise](https://cloud.google.com/products/gemini/enterprise)
