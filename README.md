# BigQuery Multi-Agent App

A multi-agent system for BigQuery analytics and data science, built with the
[Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/). Users
interact in natural language; the system handles schema discovery, analytics via
the Conversational Analytics (CA) API, advanced Python analysis, BigQuery ML
operations, and access to pre-configured BQ Data Agents.

## Quick Start

```bash
# 1. Authenticate
gcloud auth application-default login

# 2. Clone and install
git clone https://github.com/johanesalxd/bq-agent-app.git
cd bq-agent-app
uv sync

# 3. Configure
cp .env.example .env
# Edit .env: set GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION,
#            GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET

# 4. Run
uv run adk web
```

> **ADC note:** Do not set `GOOGLE_APPLICATION_CREDENTIALS`. The app uses
> Application Default Credentials (ADC) via `gcloud auth application-default login`.
> Setting `GOOGLE_APPLICATION_CREDENTIALS` to a service account key overrides ADC
> and will cause auth failures for the per-user OAuth flows.

> **Shell environment note:** If your shell exports `GOOGLE_CLOUD_LOCATION` (e.g.
> from `.zshrc`), it overrides `.env`. The app and all setup scripts call
> `load_dotenv(..., override=True)` to handle this correctly. Avoid exporting
> region vars globally, or ensure your `.env` values are consistent with your shell.

---

## How It Works

The root agent uses **intent-based routing** — it infers what the user needs from
context, not keyword matching, and sends the request to the right tool or sub-agent.

```
User: "Show me sales by region last month"
  -> Root agent: standard data question
  -> Calls ask_data_insights with discovered table references
  -> Returns data table + Vega-Lite chart (rendered natively in Gemini Enterprise)

User: "Run a significance test comparing region revenue"
  -> Root agent: statistical analysis, needs Python
  -> Delegates to DS sub-agent
  -> DS agent: execute_sql (retrieve data) -> Code Interpreter (scipy, statsmodels)
  -> Returns statistical report + matplotlib charts

User: "Create a churn prediction model"
  -> Root agent: BQML task
  -> Delegates to BQML sub-agent
  -> BQML agent: RAG lookup -> generate SQL -> user approval -> execute

User: "Ask my sales data agent about Q4"
  -> Root agent: pre-configured Data Agent reference
  -> Calls DataAgentToolset -> ask_data_agent
  -> Returns CA API response from the user's pre-configured agent
```

### Routing logic

| Priority | Path | Trigger (inferred from intent) | Handler |
|----------|------|-------------------------------|---------|
| 1 | **Data Agent** | User explicitly references a named BQ Data Agent | `DataAgentToolset` |
| 2 | **BQML** | ML model creation, training, evaluation, predictions | BQML sub-agent |
| 3 | **Advanced** | Statistical testing, custom Python, forecasting, anomaly detection | DS sub-agent |
| 4 | **Default** | Everything else — counts, aggregations, trends, comparisons, charts | `ask_data_insights` (CA API) |

The **Default path** handles the vast majority of queries. `ask_data_insights` is
the same backend that powers BQ Agents and Looker Conversational Analytics — it
translates natural-language questions into SQL and returns Vega-Lite chart specs
that render natively in Gemini Enterprise.

---

## Architecture

```
Root Agent  bigquery_ds_agent
│
├── BigQueryToolset  [ca_toolset — read-only, per-user OAuth]
│   ask_data_insights  list_dataset_ids  get_dataset_info
│   list_table_ids  get_table_info  search_catalog
│
├── DataAgentToolset  [per-user OAuth]
│   list_accessible_data_agents  get_data_agent_info  ask_data_agent
│
├── Memory Tools  [Vertex AI Memory Bank]
│   PreloadMemoryTool  LoadMemoryTool
│
└── Sub-agents
    │
    ├── DS Sub-Agent  ds_agent
    │   ├── BigQueryToolset  [ds_toolset — read-only, per-user OAuth]
    │   │   execute_sql  forecast  analyze_contribution  detect_anomalies
    │   │   list_dataset_ids  get_dataset_info  list_table_ids
    │   │   get_table_info  get_job_info
    │   ├── Code Interpreter  [VertexAiCodeExecutor]
    │   │   numpy 1.26.4  pandas 2.2.1  matplotlib 3.8.3  scipy 1.12.0
    │   │   seaborn 0.13.2  scikit-learn 1.4.0  statsmodels 0.14.1  Pillow 10.2.0
    │   └── load_artifacts
    │
    └── BQML Sub-Agent  bqml_agent
        ├── BigQueryToolset  [bqml_toolset — write-enabled, per-user OAuth]
        │   execute_sql  list_dataset_ids  get_dataset_info
        │   list_table_ids  get_table_info
        └── rag_response  [BQML documentation corpus]
```

### Technology stack

| Component | Details |
|-----------|---------|
| Framework | Google ADK 1.28+ |
| Model | Gemini 2.5 Flash Preview |
| CA API | `ask_data_insights` — same backend as BQ Agents and Looker CA |
| Auth | Per-user OAuth passthrough (BigQuery + Data Agents) |
| Code execution | `VertexAiCodeExecutor` + pre-provisioned Code Interpreter Extension |
| BQML docs | Vertex AI RAG corpus (`text-embedding-005`, `us-west4`) |
| Memory | Vertex AI Memory Bank via `PreloadMemoryTool` / `LoadMemoryTool` |

---

## Prerequisites

- Python 3.12
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) package manager
- Google Cloud project with BigQuery enabled
- `gcloud` CLI authenticated: `gcloud auth application-default login`

### Required GCP APIs

```bash
gcloud services enable aiplatform.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
gcloud services enable discoveryengine.googleapis.com  # Gemini Enterprise only
```

### Required IAM roles

| Role | Purpose |
|------|---------|
| Vertex AI User | Agent Engine, Code Interpreter, RAG |
| BigQuery User | Query execution |
| BigQuery Data Viewer | Table / schema access |

---

## Setup

Complete these steps once before running the app for the first time.

### 1. OAuth 2.0 client (required)

BigQuery and Data Agent toolsets authenticate each user via OAuth. You need an
OAuth 2.0 client registered in Google Cloud Console.

1. Cloud Console → APIs & Services → Credentials → **Create OAuth 2.0 Client ID**
2. Application type: **Web application**
3. Add authorised redirect URIs:
   - Local ADK web UI: `http://localhost:8000/oauth2callback`
   - Gemini Enterprise: `https://vertexaisearch.cloud.google.com/oauth-redirect`
   - Gemini Enterprise: `https://vertexaisearch.cloud.google.com/static/oauth/oauth.html`
4. Copy **Client ID** and **Client Secret** to `.env`:
   ```
   GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
   ```

### 2. Code Interpreter Extension (required for DS agent)

`VertexAiCodeExecutor` requires a pre-provisioned Code Interpreter Extension.
Create one once and pin it in `.env` to prevent new extensions being created on
every agent start.

```bash
uv run python setup/vertex_extensions/setup_vertex_extensions.py
# Copy the printed resource name to CODE_INTERPRETER_EXTENSION_NAME in .env
```

To clean up duplicate extensions:

```bash
# Preview first
uv run python setup/vertex_extensions/cleanup_vertex_extensions.py \
    --dry-run --keep-id YOUR_EXTENSION_ID

# Then delete
uv run python setup/vertex_extensions/cleanup_vertex_extensions.py \
    --keep-id YOUR_EXTENSION_ID
```

See [`setup/vertex_extensions/VERTEX_EXTENSIONS_GUIDE.md`](setup/vertex_extensions/VERTEX_EXTENSIONS_GUIDE.md)
for full details.

### 3. BQML RAG corpus (required for BQML agent)

The BQML agent uses a Vertex AI RAG corpus for documentation lookup. The script
deploys the corpus and writes `BQML_RAG_CORPUS_NAME` to `.env` automatically.

```bash
uv run python setup/rag_corpus/create_bqml_corpus.py
```

> **Region note:** The script defaults to `us-west4` (`RAG_LOCATION` env var).
> New GCP projects typically have higher Vertex AI RAG quota there than in
> `us-central1`. Override by setting `RAG_LOCATION` in `.env` before running.

---

## Running Locally

```bash
uv run adk web
```

Open `http://localhost:8000` in your browser. On first tool use, you will be
prompted to complete an OAuth flow for your BigQuery credentials.

### With Memory Bank

Memory Bank persists conversation context across sessions. It requires a deployed
Agent Engine instance as the backing store (see [Deployment](#deployment)).

```bash
# After deploying, set AGENT_ENGINE_ID in .env (numeric suffix of the resource name),
# then run:
uv run adk web --memory_service_uri=agentengine://$AGENT_ENGINE_ID
```

---

## Deployment

### Agent Engine

The app deploys to Vertex AI Agent Engine using the ADK CLI. Deploying from source
avoids serialization issues with `VertexAiCodeExecutor`.

**Prerequisites:** Complete all Setup steps above and ensure `.env` has
`GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `GOOGLE_OAUTH_CLIENT_ID`,
`GOOGLE_OAUTH_CLIENT_SECRET`, `CODE_INTERPRETER_EXTENSION_NAME`, and
`BQML_RAG_CORPUS_NAME` set.

```bash
chmod +x deployment/deploy.sh
./deployment/deploy.sh
```

After deployment completes, copy the resource name from the output to `.env`:

```
AGENT_ENGINE_RESOURCE_NAME=projects/PROJECT_NUMBER/locations/REGION/reasoningEngines/ENGINE_ID
AGENT_ENGINE_ID=ENGINE_ID
```

`deploy.sh` configures Memory Bank automatically with 5 topics:

| Topic | What is stored |
|-------|---------------|
| `USER_PERSONAL_INFO` | Team, role, organisational context |
| `USER_PREFERENCES` | Chart style, analysis preferences, currency |
| `KEY_CONVERSATION_DETAILS` | Milestones and conclusions from past sessions |
| `EXPLICIT_INSTRUCTIONS` | Persistent user instructions |
| `data_analysis_context` (custom) | Frequently used datasets, tables, domain context |

**To update an existing deployment:**

```bash
./deployment/deploy.sh --agent_engine_id=ENGINE_ID
```

**Smoke test:**

```bash
uv run python deployment/test_deployment.py
```

**Session management via REST:**

```bash
ACCESS_TOKEN=$(gcloud auth print-access-token)

# List sessions
curl -s -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  "https://us-central1-aiplatform.googleapis.com/v1beta1/${AGENT_ENGINE_RESOURCE_NAME}/sessions"

# Delete a session
curl -s -X DELETE -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  "https://us-central1-aiplatform.googleapis.com/v1beta1/${AGENT_ENGINE_RESOURCE_NAME}/sessions/SESSION_ID"
```

### Gemini Enterprise

After deploying to Agent Engine, register the agent to surface it in the Gemini
Enterprise console. Gemini Enterprise renders Vega-Lite charts from
`ask_data_insights` natively.

**Prerequisites:** `AGENT_ENGINE_RESOURCE_NAME` and `GEMINI_ENTERPRISE_APP_ID`
must be set in `.env`. Find your app ID in the Gemini Enterprise console under
your app settings.

```bash
chmod +x deployment/register_gemini_enterprise.sh
./deployment/register_gemini_enterprise.sh
```

The script:
1. Extracts the region from `AGENT_ENGINE_RESOURCE_NAME` automatically.
2. Calls the Discovery Engine API to register the agent.
3. Prints the agent ID and a link to the console on success.

> **Endpoint location:** The Discovery Engine endpoint defaults to `global`
> (most Gemini Enterprise apps). Override with `GEMINI_ENTERPRISE_ENDPOINT_LOCATION=us`
> or `=eu` in `.env` if your app is region-scoped.

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

---

## Example Interactions

**Default path — CA API**
```
"What datasets are available in my project?"
"Show me the schema of the sales table"
"Top 10 customers by revenue this year"
"Monthly sales trend as a bar chart"
```

**Advanced path — DS sub-agent**
```
"Compare revenue across regions with statistical significance testing"
"Detect anomalies in daily order counts"
"Forecast sales for the next 30 days with confidence intervals"
"What drove the revenue change between Q3 and Q4?"
```

**BQML path**
```
"Create a logistic regression model for churn prediction"
"List existing BQML models in my dataset"
"Evaluate the churn model and show metrics"
"Forecast with ARIMA_PLUS using the sales_data table"
```

**Data Agent path**
```
"Ask my sales data agent about top products last quarter"
"Which data agents do I have available?"
```

---

## Project Structure

```
bq-agent-app/
├── pyproject.toml
├── .env.example
├── bq_multi_agent_app/
│   ├── __init__.py                    # ADK discovery re-export
│   ├── agent.py                       # Root agent: Memory Bank, sub-agents, ca_toolset
│   ├── tools.py                       # ca_toolset, ds_toolset, data_agent_toolset
│   ├── prompts.py                     # Root agent prompt (intent-based routing)
│   ├── .agent_engine_config.json      # Memory Bank config for CLI deploy
│   ├── requirements.txt               # Python deps for Agent Engine container
│   └── sub_agents/
│       ├── __init__.py
│       ├── bqml_agents/
│       │   ├── agent.py               # BQML sub-agent
│       │   ├── prompts.py
│       │   └── tools.py               # bqml_toolset (execute_sql + discovery, write-enabled)
│       └── ds_agents/
│           ├── agent.py               # DS sub-agent: ds_toolset + Code Interpreter
│           └── prompts.py
├── deployment/
│   ├── deploy.sh                      # Agent Engine deployment via ADK CLI
│   ├── register_gemini_enterprise.sh  # Gemini Enterprise registration
│   └── test_deployment.py             # Smoke test for deployed instance
├── setup/
│   ├── probe_code_interpreter.py      # Verify available Code Interpreter libraries
│   ├── rag_corpus/
│   │   └── create_bqml_corpus.py      # Vertex AI RAG corpus provisioning
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

---

## Security

- Root and DS toolsets use `WriteMode.BLOCKED` (read-only)
- BQML toolset uses `WriteMode.ALLOWED` (required for `CREATE MODEL`)
- Per-user OAuth ensures each user's IAM permissions are enforced end-to-end
- Store all credentials in `.env` (git-ignored); never hardcode secrets
- Do not set `GOOGLE_APPLICATION_CREDENTIALS` — use ADC (`gcloud auth application-default login`)

---

## Related Resources

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [ADK BigQuery Tools](https://google.github.io/adk-docs/integrations/bigquery/)
- [BigQuery Conversational Analytics](https://cloud.google.com/bigquery/docs/conversational-analytics-overview)
- [Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
- [Gemini Enterprise](https://cloud.google.com/products/gemini/enterprise)
- [Vertex AI Memory Bank](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank)
