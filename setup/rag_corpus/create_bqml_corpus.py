"""
Create and manage BQML RAG Corpus for BigQuery ML documentation.

This script creates a Vertex AI RAG corpus containing BQML documentation
and reference guides for use by the BQML agent.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from dotenv import set_key
import vertexai
from vertexai import rag

# Define the path to the .env file
env_file_path = Path(__file__).parent.parent.parent / ".env"

# Load environment variables from the specified .env file
load_dotenv(dotenv_path=env_file_path)

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
corpus_name = os.getenv("BQML_RAG_CORPUS_NAME")

display_name = "bqml_referenceguide_corpus"

# Use Google's public BQML documentation
paths = [
    "gs://cloud-samples-data/adk-samples/data-science/bqml"
]  # Supports Google Cloud Storage and Google Drive Links

# Initialize Vertex AI API once per session
vertexai.init(project=PROJECT_ID, location="us-central1")


def create_RAG_corpus():
    """Create RagCorpus with embedding model configuration."""
    # Configure embedding model, for example "text-embedding-005".
    embedding_model_config = rag.RagEmbeddingModelConfig(
        vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
            publisher_model="publishers/google/models/text-embedding-005"
        )
    )

    backend_config = rag.RagVectorDbConfig(
        rag_embedding_model_config=embedding_model_config
    )

    bqml_corpus = rag.create_corpus(
        display_name=display_name,
        backend_config=backend_config,
    )

    write_to_env(bqml_corpus.name)

    return bqml_corpus.name


def ingest_files(corpus_name):
    """Ingest BQML documentation files into the RAG corpus."""
    transformation_config = rag.TransformationConfig(
        chunking_config=rag.ChunkingConfig(
            chunk_size=512,
            chunk_overlap=100,
        ),
    )

    rag.import_files(
        corpus_name,
        paths,
        transformation_config=transformation_config,  # Optional
        max_embedding_requests_per_min=1000,  # Optional
    )

    # List the files in the rag corpus
    rag.list_files(corpus_name)


def rag_response(query: str) -> str:
    """Retrieves contextually relevant information from a RAG corpus.

    Args:
        query (str): The query string to search within the corpus.

    Returns:
        str: The response containing retrieved information from the corpus.
    """
    corpus_name = os.getenv("BQML_RAG_CORPUS_NAME")

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


def write_to_env(corpus_name):
    """Writes the corpus name to the specified .env file.

    Args:
        corpus_name: The name of the corpus to write.
    """
    load_dotenv(env_file_path)  # Load existing variables if any

    # Set the key-value pair in the .env file
    set_key(env_file_path, "BQML_RAG_CORPUS_NAME", corpus_name)
    print(f"BQML_RAG_CORPUS_NAME '{corpus_name}' written to {env_file_path}")


if __name__ == "__main__":
    # Check if corpus already exists
    corpus_name = os.getenv("BQML_RAG_CORPUS_NAME")

    if not corpus_name:
        print("Creating new BQML RAG corpus...")
        corpus_name = create_RAG_corpus()
        print(f"Corpus created: {corpus_name}")
    else:
        print(f"Using existing corpus: {corpus_name}")

    print(f"Importing files to corpus: {corpus_name}")
    ingest_files(corpus_name)
    print(f"Files imported to corpus: {corpus_name}")
