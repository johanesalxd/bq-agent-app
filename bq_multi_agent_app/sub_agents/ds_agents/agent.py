"""
Data Science Agent with Python code execution capabilities.

This agent uses VertexAiCodeExecutor to run pandas, matplotlib, and other
data science libraries for analysis and visualization.

Note: This agent must be wrapped as a tool (not used as sub-agent) to prevent
function call interpretation errors.
"""

from google.adk.agents import Agent
from google.adk.code_executors.vertex_ai_code_executor import \
    VertexAiCodeExecutor

from .prompts import return_instructions_ds

root_agent = Agent(
    model='gemini-2.5-flash',
    name="ds_agent",
    instruction=return_instructions_ds(),
    code_executor=VertexAiCodeExecutor(
        optimize_data_file=False,  # Don't optimize data files for simpler behavior
        # Each execution starts fresh (no variable persistence)
        stateful=False,
    ),
)
