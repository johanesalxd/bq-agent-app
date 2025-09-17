"""
Tools for BigQuery Multi-Agent Application

This module provides:
1. BigQuery toolset via MCP for database operations
2. Data science agent wrapper for analysis with code execution
"""

import os

from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.mcp_tool.mcp_session_manager import \
    StreamableHTTPConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset

from .sub_agents.bqml_agents.agent import bqml_agent
from .sub_agents.ds_agents.agent import ds_agent

# Get toolbox URL from environment, default to local development
TOOLBOX_URL = os.getenv("TOOLBOX_URL", "http://127.0.0.1:5000")

# BigQuery tools via MCP toolbox
# Use McpToolset with StreamableHTTPConnectionParams for proper MCP integration

# Conversational toolset for quick insights and answers
conversational_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        # MCP endpoint with toolset filter
        url=f"{TOOLBOX_URL}/mcp/conversational_toolset",
        headers={}  # Add auth headers if needed
    )
)

# Data retrieval toolset for raw data extraction and analysis
data_retrieval_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        # MCP endpoint with toolset filter
        url=f"{TOOLBOX_URL}/mcp/data_retrieval_toolset",
        headers={}  # Add auth headers if needed
    )
)

# ML analysis toolset for forecasting and contribution analysis
ml_analysis_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        # MCP endpoint with toolset filter
        url=f"{TOOLBOX_URL}/mcp/ml_analysis_toolset",
        headers={}  # Add auth headers if needed
    )
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


async def call_bqml_agent(
    question: str,
    tool_context: ToolContext,
) -> str:
    """
    Call BQML agent for BigQuery ML operations.

    This function wraps the BQML agent as a tool to handle BQML model creation,
    training, and inspection tasks.

    Args:
        question: The BQML-related question or task
        tool_context: Context for sharing state between tools

    Returns:
        BQML operation result with model information and insights
    """
    full_request = f"""
    Please help with the following BigQuery ML task:

    TASK: {question}

    Please:
    1. Use rag_response to get relevant BQML documentation if needed
    2. Check for existing models if applicable using check_bq_models
    3. Generate appropriate BQML code and get user approval before execution
    4. Execute the BQML operations using the available tools
    5. Provide clear explanations and results
    """

    # Wrap BQML agent to handle BQML operations properly
    agent_tool = AgentTool(agent=bqml_agent)

    try:
        result = await agent_tool.run_async(
            args={"request": full_request},
            tool_context=tool_context
        )
        # Store result for potential use by other tools
        tool_context.state["bqml_result"] = result
        return result

    except Exception as e:
        error_message = f"Error in BQML operations: {str(e)}"
        tool_context.state["bqml_error"] = error_message
        return error_message
