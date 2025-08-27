from datetime import date

from google.adk.agents.llm_agent import Agent

from .prompts import return_instructions_root
from .subagents import ds_agent
from .tools import bigquery_toolset

date_today = date.today()

root_agent = Agent(
    model='gemini-2.5-flash',
    name="bigquery_ds_agent",
    global_instruction=(
        f"""
        You are a Data Science and Data Analytics Multi Agent System.
        Todays date: {date_today}
        """
    ),
    instruction=return_instructions_root(),
    sub_agents=[ds_agent],
    tools=[bigquery_toolset],
)
