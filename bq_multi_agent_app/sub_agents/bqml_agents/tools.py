"""
Tools for BQML Agent

This module provides BQML-specific tools including:
1. check_bq_models: List BigQuery ML models in a dataset
2. rag_response: Query BQML documentation from RAG corpus
3. bqml_toolset: MCP toolset for executing SQL/BQML statements
"""

import os

from google.adk.tools.mcp_tool.mcp_session_manager import \
    StreamableHTTPConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.cloud import bigquery
from vertexai import rag


def check_bq_models(dataset_id: str) -> str:
    """Lists models in a BigQuery dataset and returns them as a string.

    Args:
        dataset_id: The ID of the BigQuery dataset (e.g., "project.dataset").

    Returns:
        A string representation of a list of dictionaries, where each dictionary
        contains the 'name' and 'type' of a model in the specified dataset.
        Returns an empty string "[]" if no models are found.
    """
    try:
        client = bigquery.Client()

        models = client.list_models(dataset_id)
        model_list = []  # Initialize as a list

        print(f"Models contained in '{dataset_id}':")
        for model in models:
            model_id = model.model_id
            model_type = model.model_type
            model_list.append({"name": model_id, "type": model_type})

        return str(model_list)

    except Exception as e:
        return f"An error occurred: {str(e)}"


def rag_response(query: str) -> str:
    """Retrieves contextually relevant information from a RAG corpus.

    Args:
        query (str): The query string to search within the corpus.

    Returns:
        str: The response containing retrieved information from the corpus.
    """
    corpus_name = os.getenv("BQML_RAG_CORPUS_NAME")

    if not corpus_name:
        return "BQML RAG corpus not configured. Please set BQML_RAG_CORPUS_NAME environment variable."

    try:
        rag_retrieval_config = rag.RagRetrievalConfig(
            top_k=3,  # Optional
            filter=rag.Filter(vector_distance_threshold=0.5),  # Optional
        )
        response = rag.retrieval_query(
            rag_resources=[
                rag.RagResource(
                    rag_corpus=corpus_name,
                )
            ],
            text=query,
            rag_retrieval_config=rag_retrieval_config,
        )
        return str(response)
    except Exception as e:
        return f"Error querying RAG corpus: {str(e)}"


# Get toolbox URL from environment, default to local development
TOOLBOX_URL = os.getenv("TOOLBOX_URL", "http://127.0.0.1:5000")

# BQML toolset for executing SQL/BQML statements
bqml_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        # MCP endpoint with BQML toolset filter
        url=f"{TOOLBOX_URL}/mcp/bqml_toolset",
        headers={}  # Add auth headers if needed
    )
)
