"""Research AIDA sub-agent for BigQuery, data analytics, and AI topics.

Uses Google Search grounding to provide current, authoritative answers
about data platforms, features, comparisons, and best practices.

Note: google_search is an ADK built-in tool that must be used alone within
an agent — it cannot be combined with other tools in the same agent instance.
"""

from google.adk.agents import Agent
from google.adk.tools import google_search

from ...constants import MODEL_NAME

from .prompts import return_instructions_research

research_aida_agent = Agent(
    model=MODEL_NAME,
    name="research_aida_agent",
    description=(
        "Research agent for BigQuery, data analytics, and AI/ML topics. "
        "Uses Google Search to answer questions about platform features, "
        "comparisons with Snowflake/Databricks/Redshift, best practices, "
        "and documentation lookups. Scoped to data analytics topics only."
    ),
    instruction=return_instructions_research(),
    tools=[google_search],
)
