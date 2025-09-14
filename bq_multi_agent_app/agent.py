"""
BigQuery Multi-Agent Application - Root Agent

This is the main agent that orchestrates BigQuery data retrieval and data science analysis.
It uses MCP for BigQuery operations and ADK for data science code execution.
"""

from datetime import date

from google.adk.agents import Agent

from .prompts import return_instructions_root
from .tools import call_data_science_agent, conversational_toolset, data_retrieval_toolset, ml_analysis_toolset

date_today = date.today()

root_agent = Agent(
    model='gemini-2.5-flash',
    name="bigquery_ds_agent",
    global_instruction=(
        f"""
        You are a Data Science and BigQuery Analytics Multi Agent System.
        Today's date: {date_today}

        Your capabilities:
        1. Query BigQuery databases using your available tools.
        2. Perform data science analysis using call_data_science_agent.
        3. Create visualizations and statistical analysis.
        4. Perform advanced analysis such as forecasting and contribution analysis.
        """
    ),
    instruction=return_instructions_root(),
    tools=[
        conversational_toolset,     # BigQuery conversational analytics
        data_retrieval_toolset,     # BigQuery data retrieval and schema tools
        ml_analysis_toolset,        # BigQuery ML analysis tools
        call_data_science_agent,    # Data science analysis with code execution
    ],
)
