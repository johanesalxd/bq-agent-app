from google.adk.agents.llm_agent import Agent
from google.adk.code_executors.vertex_ai_code_executor import \
    VertexAiCodeExecutor

from bq_multi_agent_app.sub_agents.ds_agents.prompts import \
    return_instructions_ds

ds_agent = Agent(
    model='gemini-2.5-flash',
    name="ds_agent",
    instruction=return_instructions_ds(),
    code_executor=VertexAiCodeExecutor(
        optimize_data_file=False,
        stateful=False,
    ),
)
