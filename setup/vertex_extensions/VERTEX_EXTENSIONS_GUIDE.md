# Vertex AI Code Interpreter Extensions Management Guide

This guide explains how to manage Vertex AI Code Interpreter extensions to prevent
duplicate extensions and properly configure the BigQuery Multi-Agent application.

## Problem

`VertexAiCodeExecutor` creates a new Code Interpreter extension every time it runs
without a specified `resource_name`. This leads to duplicate extensions and
unnecessary resource usage.

## Solution

Set `CODE_INTERPRETER_EXTENSION_NAME` in `.env` to reuse a single pre-provisioned
extension. Use the scripts below to create and clean up extensions.

## Quick Start

### 1. Create a new extension

```bash
uv run python setup/vertex_extensions/setup_vertex_extensions.py
```

This creates a Code Interpreter extension and prints the resource name to copy
into `.env` as `CODE_INTERPRETER_EXTENSION_NAME`.

### 2. Clean up duplicate extensions

Preview what will be deleted (safe — no changes made):

```bash
uv run python setup/vertex_extensions/cleanup_vertex_extensions.py \
    --dry-run --keep-id YOUR_EXTENSION_ID
```

Delete duplicates, keeping the specified extension:

```bash
uv run python setup/vertex_extensions/cleanup_vertex_extensions.py \
    --keep-id YOUR_EXTENSION_ID
```

## Environment Configuration

```bash
# .env
CODE_INTERPRETER_EXTENSION_NAME=projects/YOUR_PROJECT_NUMBER/locations/us-central1/extensions/YOUR_EXTENSION_ID
```

## Script Reference

### setup_vertex_extensions.py

Creates a new Code Interpreter extension and prints the fully-qualified resource
name for copying to `.env`.

Reference: [Google Cloud Code Interpreter Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/extensions/code-interpreter)

### cleanup_vertex_extensions.py

| Flag | Required | Description |
|------|----------|-------------|
| `--keep-id ID` | Yes | Numeric extension ID to preserve |
| `--dry-run` | No | Preview changes without deleting |

Lists all Code Interpreter extensions (up to 100 per page), keeps the specified ID,
and deletes all others. Prompts for confirmation before deletion.

## Best Practices

1. Always use `--dry-run` first to preview changes before executing cleanup.
2. Set `CODE_INTERPRETER_EXTENSION_NAME` in `.env` to prevent new extensions from
   being created on every agent start.
3. Run cleanup periodically if multiple developers or runs have created extras.
