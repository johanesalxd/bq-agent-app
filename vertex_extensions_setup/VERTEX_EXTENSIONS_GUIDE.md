# Vertex AI Code Interpreter Extensions Management Guide

This guide explains how to manage Vertex AI Code Interpreter extensions to prevent duplicate extensions and properly configure your BigQuery Multi-Agent application.

## Problem

The `VertexAiCodeExecutor` creates a new Code Interpreter extension every time it runs without a specified `resource_name`. This leads to multiple duplicate extensions and unnecessary resource usage.

## Solution

Use environment variables to specify which extension to use and scripts to manage extensions.

## Quick Start

### 1. Create a New Extension

```bash
python setup_vertex_extensions.py
```

This will:
- Create a new Code Interpreter extension
- Print the extension resource name in the format: `projects/PROJECT_NUMBER/locations/REGION/extensions/EXTENSION_ID`
- Tell you to copy this line to your `.env` file

### 2. Clean Up Duplicate Extensions

Preview what will be deleted:

```bash
python cleanup_vertex_extensions.py --dry-run --keep-id YOUR_EXTENSION_ID
```

Delete duplicates (keeping the specified extension):

```bash
python cleanup_vertex_extensions.py --keep-id YOUR_EXTENSION_ID
```

## Environment Configuration

Add the extension resource name to your `.env` file:

```bash
# Vertex AI Code Interpreter Extension
CODE_INTERPRETER_EXTENSION_NAME=projects/605626490127/locations/us-central1/extensions/2132199061984378880
```

## Script Usage

### setup_vertex_extensions.py

**Command**: `python setup_vertex_extensions.py`

**What it does**:
- Creates a new Code Interpreter extension
- Gets your project number automatically
- Prints the complete resource name for copying to `.env`

**Based on**: [Google Cloud Code Interpreter Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/extensions/code-interpreter)

### cleanup_vertex_extensions.py

**Commands**:
- `python cleanup_vertex_extensions.py --dry-run --keep-id EXTENSION_ID` - Preview cleanup
- `python cleanup_vertex_extensions.py --keep-id EXTENSION_ID` - Delete duplicates

**What it does**:
- Lists all Code Interpreter extensions
- Keeps the specified extension ID
- Deletes all other Code Interpreter extensions

## How It Works

### DS Agent Configuration

The DS agent automatically uses the extension specified in the environment variable:

```python
ds_agent = Agent(
    model='gemini-2.5-flash',
    name="ds_agent",
    instruction=return_instructions_ds(),
    code_executor=VertexAiCodeExecutor(
        optimize_data_file=False,
        stateful=False,
    ),
)
```

The Google ADK SDK automatically checks for the `CODE_INTERPRETER_EXTENSION_NAME` environment variable.

### Tool vs Sub-Agent Pattern

The DS agent is wrapped as a tool to prevent `MALFORMED_FUNCTION_CALL` errors:

```python
# In tools.py
def call_data_science_agent(query: str) -> str:
    """Call the data science agent for data analysis and visualization."""
    try:
        response = ds_agent.send_message(query)
        return response.text
    except Exception as e:
        return f"Error calling data science agent: {str(e)}"

# In agent.py
root_agent = Agent(
    model='gemini-2.5-flash',
    name="bigquery_ds_agent",
    instruction=return_instructions_root(),
    tools=[bigquery_toolset, call_data_science_agent],  # As tool, not sub_agent
)
```

## Best Practices

1. **Always use dry-run first**: Preview changes before executing cleanup
2. **Keep the most recent extension**: Usually the one with the latest creation date
3. **Set up environment variables**: Prevents creation of new extensions
4. **Regular cleanup**: Periodically clean up unused extensions

## Troubleshooting

### Permission Errors
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### Extension Not Found
1. Run `python setup_vertex_extensions.py` to create a new one
2. Check if you're using the correct extension ID
3. Verify the extension exists in your project

### Import Errors
```bash
pip install google-adk
```

## Summary

This solution provides:
- ✅ Simple extension creation with `python setup_vertex_extensions.py`
- ✅ Easy cleanup with `python cleanup_vertex_extensions.py --keep-id EXTENSION_ID`
- ✅ Prevents duplicate extensions via environment variables
- ✅ Safe dry-run options
- ✅ Tool-based architecture for error prevention

Your DS agent will consistently use the specified extension without creating new ones.
