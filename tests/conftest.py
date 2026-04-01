"""
Shared fixtures and hooks for the bq-multi-agent-app test suite.

The application modules instantiate BigQueryToolset, DataAgentToolset, and
VertexAiCodeExecutor at import time, reading env vars via os.environ[]. These
must be set before any module is imported.

VertexAiCodeExecutor makes a live gRPC call at init time to validate the Code
Interpreter extension resource name. The call must succeed, which requires real
project credentials and a real extension ID. We load the project .env file
before any module is imported so the real values are available. pytest_configure
runs at collection time before any test module is imported, making it the
correct place to inject these env vars.

GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET are set as fallbacks for
CI environments that do not have a .env file present.
"""

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv


def pytest_configure(config):
    """Load real credentials and set required env vars before modules import."""
    load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

    # CI fallbacks for OAuth vars not needed in production .env.
    os.environ.setdefault("GOOGLE_OAUTH_CLIENT_ID", "test-client-id")
    os.environ.setdefault("GOOGLE_OAUTH_CLIENT_SECRET", "test-client-secret")


@pytest.fixture()
def unset_rag_corpus(monkeypatch):
    """Remove BQML_RAG_CORPUS_NAME so rag_response returns its guard message."""
    monkeypatch.delenv("BQML_RAG_CORPUS_NAME", raising=False)
