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

# Session state key where Gemini Enterprise deposits the user's OAuth access token.
# All toolsets read from this key on every tool call — no caching, no refresh attempt.
# This bypasses the broken refresh flow (Gemini Enterprise issues access tokens only,
# no refresh tokens) and ensures every call uses the latest token from the session.
_AUTH_ID = os.getenv("AUTH_ID", "bq-oauth")

# Shared credentials config for all BigQuery toolsets.
# Uses external_access_token_key so the toolset reads the token directly from
# tool_context.state[_AUTH_ID] on every invocation instead of managing OAuth
# credentials (client_id/client_secret) and attempting token refresh.
_bq_credentials = BigQueryCredentialsConfig(
    external_access_token_key=_AUTH_ID,
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
# Uses external_access_token_key so the token is read fresh from session state
# on every call — consistent with the BigQuery toolsets above.
data_agent_toolset = DataAgentToolset(
    credentials_config=DataAgentCredentialsConfig(
        external_access_token_key=_AUTH_ID,
    ),
    data_agent_tool_config=DataAgentToolConfig(max_query_result_rows=100),
)
