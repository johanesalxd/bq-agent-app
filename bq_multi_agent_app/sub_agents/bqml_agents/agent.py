"""
BQML Agent for BigQuery ML operations.

This agent specializes in BigQuery ML tasks including model creation, training,
and inspection. It uses RAG for BQML documentation and integrates with BigQuery
through MCP toolsets.
"""

from google.adk.agents import Agent

from .prompts import return_instructions_bqml
from .tools import bqml_toolset
from .tools import check_bq_models
from .tools import rag_response

root_agent = Agent(
    model='gemini-2.5-flash',
    name="bqml_agent",
    instruction=return_instructions_bqml(),
    tools=[
        bqml_toolset,      # MCP toolset for BigQuery SQL/BQML execution
        check_bq_models,   # List existing BQML models
        rag_response,      # Query BQML documentation
    ],
)
