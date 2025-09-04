"""
BigQuery Multi-Agent Application - Root Agent

This is the main agent that orchestrates BigQuery data retrieval and data science analysis.
It uses MCP for BigQuery operations and ADK for data science code execution.
"""

from datetime import date

from google.adk.agents import Agent

from .prompts import return_instructions_root
from .tools import bigquery_toolset
from .tools import call_data_science_agent

date_today = date.today()

root_agent = Agent(
    model='gemini-2.5-flash',
    name="bigquery_ds_agent",
    global_instruction=(
        f"""
        You are a Data Science and BigQuery Analytics Multi Agent System.
        Today's date: {date_today}

        Your capabilities:
        1. Query BigQuery databases using MCP toolset
        2. Perform data science analysis using call_data_science_agent
        3. Create visualizations and statistical analysis

        Workflow:
        1. Use BigQuery tools to retrieve data based on user questions
        2. Use call_data_science_agent to analyze the retrieved data
        3. Provide insights, visualizations, and conclusions
        """
    ),
    instruction=return_instructions_root(),
    tools=[
        bigquery_toolset,           # BigQuery database operations via MCP
        call_data_science_agent,    # Data science analysis with code execution
    ],
)
