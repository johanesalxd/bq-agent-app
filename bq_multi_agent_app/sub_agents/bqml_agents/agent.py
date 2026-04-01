"""
BQML Agent for BigQuery ML operations.

This agent specializes in BigQuery ML tasks including model creation, training,
and inspection. It uses RAG for BQML documentation and integrates with BigQuery
through the bqml_toolset. Existing models are discovered via INFORMATION_SCHEMA
queries through bqml_toolset, ensuring per-user OAuth is enforced consistently.
"""

from google.adk.agents import Agent

from .prompts import return_instructions_bqml
from .tools import bqml_toolset
from .tools import rag_response
from ...constants import MODEL_NAME

bqml_agent = Agent(
    model=MODEL_NAME,
    name="bqml_agent",
    description=(
        "Specializes in BigQuery ML tasks including model creation, training, "
        "evaluation, and predictions using BQML syntax. Also lists and inspects "
        "existing BQML models in datasets."
    ),
    instruction=return_instructions_bqml(),
    tools=[
        bqml_toolset,  # BigQueryToolset for SQL/BQML execution with per-user OAuth
        rag_response,  # Query BQML documentation from RAG corpus
    ],
)
