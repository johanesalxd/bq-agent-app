"""
Tools for BigQuery Multi-Agent Application

This module provides:
1. BigQuery toolset via ADK built-in BigQueryToolset (ADC) for database operations
2. Data science agent wrapper for analysis with code execution
"""

import google.auth
from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.bigquery import BigQueryCredentialsConfig, BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode

from .sub_agents import ds_agent

# Use Application Default Credentials
_credentials, _ = google.auth.default()

# Read-only BigQuery toolset (blocks write operations)
# Replaces the three MCP toolsets: conversational, data_retrieval, ml_analysis
bigquery_toolset = BigQueryToolset(
    credentials_config=BigQueryCredentialsConfig(credentials=_credentials),
    bigquery_tool_config=BigQueryToolConfig(write_mode=WriteMode.BLOCKED),
)


async def call_data_science_agent(
    question: str,
    data: str,
    tool_context: ToolContext,
) -> str:
    """
    Call DS agent to analyze data using Python code execution.

    This function wraps the DS agent as a tool to prevent code execution errors
    that would occur if used as a sub-agent.

    Args:
        question: The analytical question to answer
        data: The data to analyze (CSV, JSON, query results, etc.)
        tool_context: Context for sharing state between tools

    Returns:
        Analysis result with insights, visualizations, and conclusions
    """
    full_request = f"""
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

    # Wrap DS agent to handle code execution properly
    agent_tool = AgentTool(agent=ds_agent)

    try:
        result = await agent_tool.run_async(
            args={"request": full_request}, tool_context=tool_context
        )
        # Store result for potential use by other tools
        tool_context.state["ds_analysis_result"] = result
        return result

    except Exception as e:
        error_message = f"Error in data science analysis: {str(e)}"
        tool_context.state["ds_analysis_error"] = error_message
        return error_message
