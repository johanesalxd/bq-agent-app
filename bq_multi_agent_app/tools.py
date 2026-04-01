"""
Tools for BigQuery Multi-Agent Application

This module provides:
1. BigQuery toolset via ADK built-in BigQueryToolset (user OAuth) for database operations
2. Data Agent toolset via ADK DataAgentToolset (user OAuth) for conversational analytics
3. Data science agent wrapper for analysis with code execution
"""

import os

from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.bigquery import BigQueryCredentialsConfig, BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode
from google.adk.tools.data_agent.config import DataAgentToolConfig
from google.adk.tools.data_agent.credentials import DataAgentCredentialsConfig
from google.adk.tools.data_agent.data_agent_toolset import DataAgentToolset

from .sub_agents import ds_agent

# Read-only BigQuery toolset using per-user OAuth.
# Each user authenticates via Google OAuth consent screen on first BQ call;
# the token is cached in session state under "bigquery_token_cache" and
# reused (with automatic refresh) for subsequent calls within the same session.
# This ensures BQ IAM permissions are enforced at the individual user level.
bigquery_toolset = BigQueryToolset(
    credentials_config=BigQueryCredentialsConfig(
        client_id=os.environ["GOOGLE_OAUTH_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_OAUTH_CLIENT_SECRET"],
    ),
    bigquery_tool_config=BigQueryToolConfig(write_mode=WriteMode.BLOCKED),
)

# Data Agent toolset backed by the Conversational Analytics API.
# Uses per-user OAuth (same client credentials, separate token cache key
# "data_agent_token_cache"). Provides access to pre-configured BQ Data Agents
# for natural-language analytics without writing SQL.
data_agent_toolset = DataAgentToolset(
    credentials_config=DataAgentCredentialsConfig(
        client_id=os.environ["GOOGLE_OAUTH_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_OAUTH_CLIENT_SECRET"],
    ),
    data_agent_tool_config=DataAgentToolConfig(max_query_result_rows=100),
)

# AgentTool wrapping the DS agent. Instantiated once at module level to avoid
# creating a new object on every call_data_science_agent invocation.
_ds_agent_tool = AgentTool(agent=ds_agent)


def _build_ds_request(question: str, data: str) -> str:
    """Builds the formatted request prompt for the data science agent.

    Args:
        question: The analytical question to answer.
        data: The data to analyze (CSV, JSON, query results, etc.).

    Returns:
        Formatted prompt string combining the question and data with
        analysis instructions.
    """
    return f"""
    Please analyze the provided data to answer the following question:

    QUESTION: {question}

    DATA TO ANALYZE:
    {data}

    Please provide:
    1. Data exploration and cleaning if needed
    2. Relevant analysis using pandas, numpy, etc.
    3. Visualizations using matplotlib/seaborn if appropriate
    4. Clear insights and conclusions
    """


async def call_data_science_agent(
    question: str,
    data: str,
    tool_context: ToolContext,
) -> str:
    """Calls the DS agent to analyze data using Python code execution.

    This function wraps the DS agent as a tool to prevent code execution errors
    that would occur if used as a sub-agent.

    Args:
        question: The analytical question to answer.
        data: The data to analyze (CSV, JSON, query results, etc.).
        tool_context: Context for sharing state between tools.

    Returns:
        Analysis result with insights, visualizations, and conclusions.
    """
    full_request = _build_ds_request(question, data)

    try:
        result = await _ds_agent_tool.run_async(
            args={"request": full_request}, tool_context=tool_context
        )
        # Store result for potential use by other tools
        tool_context.state["ds_analysis_result"] = result
        return result

    except Exception as e:
        error_message = f"Error in data science analysis: {str(e)}"
        tool_context.state["ds_analysis_error"] = error_message
        return error_message
