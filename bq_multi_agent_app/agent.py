"""
BigQuery Multi-Agent Application - Root Agent

CA API-first orchestration of BigQuery analytics, advanced data science,
BigQuery ML, and conversational analytics via BQ Data Agents.

All BigQuery and Data Agent operations use per-user OAuth so each user's
IAM permissions are enforced transparently.

Memory Bank (Vertex AI) provides cross-session conversation persistence when
deployed to Agent Engine. Run locally with:
    uv run adk web --memory_service_uri=agentengine://$AGENT_ENGINE_ID
"""

from datetime import date

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.adk.tools.load_memory_tool import LoadMemoryTool

from .prompts import return_instructions_root
from .sub_agents import bqml_agent, ds_agent
from .tools import ca_toolset, data_agent_toolset

# Number of recent events to process for memory generation per turn.
_MEMORY_EVENT_WINDOW = 5


async def _generate_memories_callback(callback_context: CallbackContext) -> None:
    """Generate memories from the most recent conversation events.

    Called after each agent turn. Uses add_events_to_memory (incremental
    processing) to avoid reprocessing events from prior turns.
    """
    await callback_context.add_events_to_memory(
        events=callback_context.session.events[-_MEMORY_EVENT_WINDOW:-1]
    )


def _global_instruction() -> str:
    """Build global instruction with current date (evaluated per-request)."""
    return f"""
    You are a Data Science and BigQuery Analytics Multi Agent System.
    Today's date: {date.today()}

    Follow the detailed instructions provided to discover schema and execute analysis.
    """


root_agent = Agent(
    model="gemini-3-flash-preview",
    name="bigquery_ds_agent",
    description=(
        "Orchestrates BigQuery analytics, data science analysis, BigQuery ML operations, "
        "and conversational analytics via BQ Data Agents. Routes requests to the "
        "appropriate tool or sub-agent based on the type of analysis required."
    ),
    global_instruction=_global_instruction,
    instruction=return_instructions_root(),
    sub_agents=[ds_agent, bqml_agent],
    tools=[
        ca_toolset,  # CA API + discovery tools (ask_data_insights, list/get dataset/table)
        data_agent_toolset,  # Pre-configured BQ Data Agents via Conversational Analytics API
        PreloadMemoryTool(),  # Auto-retrieves relevant memories at the start of each turn
        LoadMemoryTool(),  # Model calls this explicitly to search memories mid-conversation
    ],
    after_agent_callback=_generate_memories_callback,
)
