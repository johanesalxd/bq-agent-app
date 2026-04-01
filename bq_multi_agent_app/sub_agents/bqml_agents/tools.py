"""
Tools for BQML Agent

This module provides BQML-specific tools including:
1. rag_response: Query BQML documentation from RAG corpus
2. bqml_toolset: ADK built-in BigQueryToolset for executing SQL/BQML statements

Note: Listing BigQuery ML models is handled via the bqml_toolset using
INFORMATION_SCHEMA.MODELS, which ensures per-user OAuth is enforced consistently.
"""

import os

from google.adk.tools.bigquery import BigQueryCredentialsConfig, BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode
from vertexai import rag


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


# BQML toolset using per-user OAuth.
# Shares the "bigquery_token_cache" session state key with the root BigQueryToolset,
# so the user authenticates only once for all BQ operations across both agents.
# Write mode is allowed for BQML model creation and training.
bqml_toolset = BigQueryToolset(
    credentials_config=BigQueryCredentialsConfig(
        client_id=os.environ["GOOGLE_OAUTH_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_OAUTH_CLIENT_SECRET"],
    ),
    bigquery_tool_config=BigQueryToolConfig(write_mode=WriteMode.ALLOWED),
)
