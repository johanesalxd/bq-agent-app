"""
BigQuery Multi-Agent Application - Root Agent

This is the main agent that orchestrates BigQuery data retrieval, data science analysis,
and conversational analytics via BQ Data Agents. All BigQuery and Data Agent operations
use per-user OAuth so that each user's IAM permissions are enforced transparently.
"""

from datetime import date

from google.adk.agents import Agent
from google.adk.tools import load_artifacts

from .prompts import return_instructions_root
from .sub_agents import bqml_agent
from .tools import bigquery_toolset
from .tools import call_data_science_agent
from .tools import data_agent_toolset

date_today = date.today()

root_agent = Agent(
    model="gemini-3-flash-preview",
    name="bigquery_ds_agent",
    global_instruction=(
        f"""
        You are a Data Science and BigQuery Analytics Multi Agent System.
        Today's date: {date_today}

        Follow the detailed instructions provided to discover schema and execute analysis.
        """
    ),
    instruction=return_instructions_root(),
    sub_agents=[bqml_agent],
    tools=[
        bigquery_toolset,  # BigQuery analytics (read-only, per-user OAuth)
        call_data_science_agent,  # Data science analysis with code execution
        load_artifacts,  # Load local files for analysis
        data_agent_toolset,  # Conversational Analytics API via BQ Data Agents (per-user OAuth)
    ],
)
