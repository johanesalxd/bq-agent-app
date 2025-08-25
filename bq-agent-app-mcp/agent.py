"""BigQuery Agent module for data science queries and analysis.

This module defines a BigQuery agent that can answer questions about BigQuery
data and models, and execute SQL queries using the Google ADK framework.
"""

from google.adk.agents.llm_agent import Agent
from toolbox_core import ToolboxSyncClient

bigquery_toolbox = ToolboxSyncClient("http://127.0.0.1:5000")
bigquery_toolset = bigquery_toolbox.load_toolset()

# The variable name `root_agent` determines what your root agent is for the
# debug CLI
root_agent = Agent(
    model='gemini-2.5-flash',
    name="bigquery_agent",
    description=(
        "Agent to answer questions about BigQuery data and models and execute"
        " SQL queries."
    ),
    instruction="""\
        You are a data science agent with access to several BigQuery tools.
        Make use of those tools to answer the user's questions.
    """,
    tools=bigquery_toolset,
)
