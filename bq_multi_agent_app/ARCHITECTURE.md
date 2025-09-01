# BigQuery Multi-Agent Application Architecture

## Overview

Multi-agent system for BigQuery data analysis and data science operations.

## Architecture Patterns

### Tool-Wrapped Agents (For Code Executors)

**When to Use:**
- Agents with `VertexAiCodeExecutor`
- Agents that generate raw Python code

**Implementation:**
```python
# In tools.py
async def call_data_science_agent(question: str, data: str, tool_context: ToolContext):
    agent_tool = AgentTool(agent=ds_agent)
    result = await agent_tool.run_async(args={"request": full_request}, tool_context=tool_context)
    return result

# In agent.py
root_agent = Agent(
    tools=[call_data_science_agent],
)
```

### Sub-Agents (For Tool-Based Agents)

**When to Use:**
- Agents that only use tools (no code executors)
- Agents that return structured text responses

## Current Implementation

### File Structure
```
bq_multi_agent_app/
├── agent.py                    # Root agent (uses tools, not sub-agents)
├── tools.py                   # All tools: BigQuery + DS agent wrappers
├── sub_agents/
│   └── ds_agents/
│       ├── agent.py           # DS agent with VertexAiCodeExecutor
│       └── prompts.py         # DS agent instructions
└── ARCHITECTURE.md            # This file
```

### Components

- **Root Agent (`agent.py`)**: Main orchestrator using tools
- **DS Agent (`sub_agents/ds_agents/agent.py`)**: Data analysis with VertexAiCodeExecutor
- **Tools (`tools.py`)**: BigQuery tools + DS agent wrapper

## Key Rule

| Agent Type | Has Code Executor? | Use As |
|------------|-------------------|---------|
| DS Agent | ✅ Yes | Tool |
| Other Agents | ❌ No | Sub-Agent or Tool |

## Usage

1. User asks: "Show me the monthly order trend"
2. Root agent uses BigQuery tools to get data
3. Root agent calls `call_data_science_agent` to analyze
4. DS agent generates Python code and returns results
