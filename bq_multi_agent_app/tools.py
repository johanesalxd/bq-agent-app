"""
Tools for BigQuery Multi-Agent Application

This module provides:
1. BigQuery toolset for database operations
2. Data science agent wrapper for analysis with code execution
"""

from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.bigquery.bigquery_toolset import BigQueryToolset

from .credentials import credentials_config
from .sub_agents.ds_agents.agent import ds_agent

# BigQuery tools for database operations
bigquery_toolset = BigQueryToolset(credentials_config=credentials_config, tool_filter=[
    'list_dataset_ids',
    'get_dataset_info',
    'list_table_ids',
    'get_table_info',
    'execute_sql',
])


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
            args={"request": full_request},
            tool_context=tool_context
        )
        # Store result for potential use by other tools
        tool_context.state["ds_analysis_result"] = result
        return result

    except Exception as e:
        error_message = f"Error in data science analysis: {str(e)}"
        tool_context.state["ds_analysis_error"] = error_message
        return error_message
