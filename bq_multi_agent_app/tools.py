"""
Tools for BigQuery Multi-Agent Application

This module provides:
1. ca_toolset      — CA API + discovery tools for the root agent (read-only, per-user OAuth)
2. ds_toolset      — Advanced analysis tools for the DS sub-agent (read-only, per-user OAuth)
3. data_agent_toolset — Pre-configured BQ Data Agents via Conversational Analytics API
"""

import os

from google.adk.tools.bigquery import BigQueryCredentialsConfig, BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode
from google.adk.tools.data_agent.config import DataAgentToolConfig
from google.adk.tools.data_agent.credentials import DataAgentCredentialsConfig
from google.adk.tools.data_agent.data_agent_toolset import DataAgentToolset

# Shared OAuth credentials for all BigQuery toolsets.
# Each user authenticates via the Google OAuth consent screen on the first BQ
# call; the token is cached in session state under "bigquery_token_cache" and
# reused (with automatic refresh) within the same session.  All toolsets share
# the same cache key so the user authenticates only once regardless of which
# agent/toolset handles the request.
_bq_credentials = BigQueryCredentialsConfig(
    client_id=os.environ["GOOGLE_OAUTH_CLIENT_ID"],
    client_secret=os.environ["GOOGLE_OAUTH_CLIENT_SECRET"],
)

# Root agent: CA API + discovery tools (read-only).
# ask_data_insights is the Conversational Analytics API — it translates natural
# language questions into SQL and returns results with Vega-Lite chart specs.
# This handles 80-90% of user queries without needing raw SQL execution.
ca_toolset = BigQueryToolset(
    credentials_config=_bq_credentials,
    tool_filter=[
        "ask_data_insights",
        "list_dataset_ids",
        "get_dataset_info",
        "list_table_ids",
        "get_table_info",
        "search_catalog",
    ],
    bigquery_tool_config=BigQueryToolConfig(write_mode=WriteMode.BLOCKED),
)

# DS sub-agent: advanced analysis tools (read-only).
# Used for statistical testing, complex transformations, forecasting, anomaly
# detection, and multi-step analysis that require direct SQL execution or ML
# tools beyond what the CA API provides.
ds_toolset = BigQueryToolset(
    credentials_config=_bq_credentials,
    tool_filter=[
        "execute_sql",
        "forecast",
        "analyze_contribution",
        "detect_anomalies",
        "list_dataset_ids",
        "get_dataset_info",
        "list_table_ids",
        "get_table_info",
        "get_job_info",
    ],
    bigquery_tool_config=BigQueryToolConfig(write_mode=WriteMode.BLOCKED),
)

# Pre-configured BQ Data Agents via Conversational Analytics API (per-user OAuth).
# Provides access to Data Agents that users have created in BigQuery Studio.
# Shares the same OAuth client credentials; uses "data_agent_token_cache" as
# the session state key (separate from the BQ toolset token cache).
data_agent_toolset = DataAgentToolset(
    credentials_config=DataAgentCredentialsConfig(
        client_id=os.environ["GOOGLE_OAUTH_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_OAUTH_CLIENT_SECRET"],
    ),
    data_agent_tool_config=DataAgentToolConfig(max_query_result_rows=100),
)
