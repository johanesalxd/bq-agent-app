"""
Data Science Agent with Python code execution and BigQuery access.

This agent uses VertexAiCodeExecutor to run pandas, matplotlib, and other
data science libraries. It also has its own filtered BigQueryToolset for
direct SQL execution, forecasting, and anomaly detection — so it can query
data independently without relying on the root agent to pass data in.
"""

import os

from google.adk.agents import Agent
from google.adk.code_executors.vertex_ai_code_executor import VertexAiCodeExecutor
from google.adk.tools import load_artifacts

from .prompts import return_instructions_ds
from ...auth import bridge_oauth_token
from ...constants import MODEL_NAME
from ...tools import ds_toolset

ds_agent = Agent(
    model=MODEL_NAME,
    name="ds_agent",
    description=(
        "Performs advanced data science analysis with Python code execution and direct "
        "BigQuery access. Uses pandas, matplotlib, numpy, scipy, and seaborn for "
        "statistical analysis and visualization. Can run SQL queries, time-series "
        "forecasting, contribution analysis, and anomaly detection directly on BQ tables."
    ),
    instruction=return_instructions_ds(),
    tools=[
        ds_toolset,  # Advanced BQ tools: execute_sql, forecast, analyze_contribution, etc.
        load_artifacts,  # Load local files for analysis
    ],
    before_tool_callback=bridge_oauth_token,
    code_executor=VertexAiCodeExecutor(
        optimize_data_file=False,
        stateful=False,
        # Reuse a pre-provisioned Code Interpreter extension to prevent
        # VertexAiCodeExecutor from creating a new one on every run.
        # See setup/vertex_extensions/ for provisioning instructions.
        resource_name=os.getenv("CODE_INTERPRETER_EXTENSION_NAME"),
    ),
)
