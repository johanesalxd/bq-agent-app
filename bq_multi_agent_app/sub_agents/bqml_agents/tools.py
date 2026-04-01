"""
Tools for BQML Agent

This module provides BQML-specific tools including:
1. rag_response: Query BQML documentation from RAG corpus
2. bqml_toolset: ADK built-in BigQueryToolset for executing SQL/BQML statements

Note: Listing BigQuery ML models is handled via the bqml_toolset using
INFORMATION_SCHEMA.MODELS, which ensures per-user OAuth is enforced consistently.
"""

import logging
import os

from google.adk.tools.bigquery import BigQueryCredentialsConfig, BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode
from vertexai import rag

logger = logging.getLogger(__name__)


def rag_response(query: str) -> str:
    """Retrieves contextually relevant information from a RAG corpus.

    Args:
        query: The query string to search within the corpus.

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
        logger.exception("rag_response: error querying corpus '%s'", corpus_name)
        return f"Error querying RAG corpus: {str(e)}"


# BQML toolset using per-user OAuth.
# Filtered to SQL execution and discovery tools only — the BQML agent does not
# need ask_data_insights, forecast, analyze_contribution, or detect_anomalies.
# Write mode is ALLOWED for CREATE MODEL, INSERT, and other DDL/DML statements.
# Shares "bigquery_token_cache" with the root and DS toolsets so the user
# authenticates only once for all BQ operations.
bqml_toolset = BigQueryToolset(
    credentials_config=BigQueryCredentialsConfig(
        client_id=os.environ["GOOGLE_OAUTH_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_OAUTH_CLIENT_SECRET"],
    ),
    tool_filter=[
        "execute_sql",
        "list_dataset_ids",
        "get_dataset_info",
        "list_table_ids",
        "get_table_info",
    ],
    bigquery_tool_config=BigQueryToolConfig(write_mode=WriteMode.ALLOWED),
)
