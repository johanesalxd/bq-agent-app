"""
Create and manage the BQML RAG corpus for BigQuery ML documentation.

This script creates a Vertex AI RAG corpus containing BQML documentation
and reference guides for use by the BQML agent.

Usage:
    uv run python setup/rag_corpus/create_bqml_corpus.py

On first run, creates the corpus and writes BQML_RAG_CORPUS_NAME to .env.
On subsequent runs, skips creation and only re-imports files into the
existing corpus.

Note: Vertex AI RAG defaults to us-west4 when GOOGLE_CLOUD_LOCATION is
not set. This is intentional -- us-west4 has higher RAG quota than
us-central1. The rest of the infrastructure runs in us-central1.
If you need the corpus in the same region, set GOOGLE_CLOUD_LOCATION
to a region that supports both Vertex AI RAG and Agent Engine.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from dotenv import set_key
import vertexai
from vertexai import rag

# Path to repo root .env file.
_ENV_FILE = Path(__file__).parent.parent.parent / ".env"

# Public GCS bucket with BQML documentation files.
_BQML_DOCS_PATH = "gs://cloud-samples-data/adk-samples/data-science/bqml"


def create_rag_corpus(
    project_id: str,
    location: str,
    display_name: str = "bqml_referenceguide_corpus",
) -> str:
    """Create a RAG corpus with the text-embedding-005 embedding model.

    Args:
        project_id: GCP project ID.
        location: GCP region for the corpus.
        display_name: Human-readable corpus name.

    Returns:
        The fully-qualified corpus resource name.
    """
    embedding_model_config = rag.RagEmbeddingModelConfig(
        vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
            publisher_model="publishers/google/models/text-embedding-005"
        )
    )

    backend_config = rag.RagVectorDbConfig(
        rag_embedding_model_config=embedding_model_config
    )

    corpus = rag.create_corpus(
        display_name=display_name,
        backend_config=backend_config,
    )

    _write_corpus_name_to_env(corpus.name)
    return corpus.name


def ingest_files(corpus_name: str) -> None:
    """Ingest BQML documentation files into the RAG corpus.

    Args:
        corpus_name: Fully-qualified corpus resource name.
    """
    transformation_config = rag.TransformationConfig(
        chunking_config=rag.ChunkingConfig(
            chunk_size=512,
            chunk_overlap=100,
        ),
    )

    rag.import_files(
        corpus_name,
        [_BQML_DOCS_PATH],
        transformation_config=transformation_config,
        max_embedding_requests_per_min=1000,
    )

    rag.list_files(corpus_name)


def _write_corpus_name_to_env(corpus_name: str) -> None:
    """Write the corpus resource name to the .env file.

    Args:
        corpus_name: Fully-qualified corpus resource name.
    """
    load_dotenv(_ENV_FILE)
    set_key(_ENV_FILE, "BQML_RAG_CORPUS_NAME", corpus_name)
    print(f"BQML_RAG_CORPUS_NAME written to {_ENV_FILE}")


if __name__ == "__main__":
    load_dotenv(dotenv_path=_ENV_FILE)

    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        raise RuntimeError("GOOGLE_CLOUD_PROJECT must be set in .env or environment.")

    # Default to us-west4 (higher Vertex AI RAG quota than us-central1).
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-west4")

    vertexai.init(project=project_id, location=location)

    corpus_name = os.getenv("BQML_RAG_CORPUS_NAME")

    if not corpus_name:
        print("Creating new BQML RAG corpus...")
        corpus_name = create_rag_corpus(project_id, location)
        print(f"Corpus created: {corpus_name}")
    else:
        print(f"Using existing corpus: {corpus_name}")

    print(f"Importing files to corpus: {corpus_name}")
    ingest_files(corpus_name)
    print(f"Files imported to corpus: {corpus_name}")
