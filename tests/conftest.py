"""
Shared fixtures and hooks for the bq-multi-agent-app test suite.

The application modules instantiate BigQueryToolset and DataAgentToolset at
import time, reading GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET via
os.environ[]. These must be set before any module is imported, which means
pytest's monkeypatch fixture (function-scoped) is too late for module-scoped
fixtures. pytest_configure runs at collection time before any test module is
imported, making it the correct place to inject test-only env vars.
"""

import os

import pytest


def pytest_configure(config):
    """Set required env vars before application modules are imported."""
    _test_env = {
        "GOOGLE_OAUTH_CLIENT_ID": "test-client-id",
        "GOOGLE_OAUTH_CLIENT_SECRET": "test-client-secret",
        "GOOGLE_CLOUD_PROJECT": "test-project",
        "GOOGLE_CLOUD_LOCATION": "us-central1",
        # Prevent accidental real Vertex AI calls during tests.
        "GOOGLE_GENAI_USE_VERTEXAI": "0",
    }
    for key, value in _test_env.items():
        os.environ.setdefault(key, value)


@pytest.fixture()
def unset_rag_corpus(monkeypatch):
    """Remove BQML_RAG_CORPUS_NAME so rag_response returns its guard message."""
    monkeypatch.delenv("BQML_RAG_CORPUS_NAME", raising=False)
