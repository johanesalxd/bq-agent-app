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
- Lists all Code Interpreter extensions (max. 100)
- Keeps the specified extension ID
- Deletes all other Code Interpreter extensions

## Best Practices

1. **Always use dry-run first**: Preview changes before executing cleanup
2. **Keep the most recent extension**: Usually the one with the latest creation date
3. **Set up environment variables**: Prevents creation of new extensions
4. **Regular cleanup**: Periodically clean up unused extensions

## Summary

This solution provides:
- ✅ Simple extension creation with `python setup_vertex_extensions.py`
- ✅ Easy cleanup with `python cleanup_vertex_extensions.py --keep-id EXTENSION_ID`
- ✅ Prevents duplicate extensions via environment variables
- ✅ Safe dry-run options
- ✅ Tool-based architecture for error prevention
