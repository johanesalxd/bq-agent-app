"""
Tests for BQML agent tools.

Covers the rag_response guard clause (no external calls needed) and the
structural absence of the removed check_bq_models function.
"""

import pytest


# ---------------------------------------------------------------------------
# rag_response – guard clause when corpus name is not configured
# ---------------------------------------------------------------------------


def test_rag_response_returns_error_when_corpus_not_configured(unset_rag_corpus):
    """rag_response must return a clear error string when BQML_RAG_CORPUS_NAME
    is not set, instead of raising an exception."""
    from bq_multi_agent_app.sub_agents.bqml_agents.tools import rag_response

    result = rag_response("any query")

    assert isinstance(result, str)
    assert len(result) > 0


def test_rag_response_error_message_is_actionable(unset_rag_corpus):
    """The error message should guide the user toward fixing the configuration."""
    from bq_multi_agent_app.sub_agents.bqml_agents.tools import rag_response

    result = rag_response("any query")

    lowered = result.lower()
    # Should mention the env var or 'not configured' so users know what to fix.
    assert (
        "bqml_rag_corpus_name" in lowered
        or "not configured" in lowered
        or "corpus" in lowered
    )


def test_rag_response_accepts_query_string(unset_rag_corpus):
    """rag_response must accept any string query without raising."""
    from bq_multi_agent_app.sub_agents.bqml_agents.tools import rag_response

    # Should not raise regardless of query content when corpus is unset.
    result = rag_response("")
    assert isinstance(result, str)

    result = rag_response("CREATE MODEL logistic regression")
    assert isinstance(result, str)


# ---------------------------------------------------------------------------
# check_bq_models – confirm removal
# ---------------------------------------------------------------------------


def test_check_bq_models_no_longer_exported():
    """check_bq_models was removed in favour of INFORMATION_SCHEMA queries
    via bqml_toolset. Importing it must fail."""
    with pytest.raises(ImportError):
        from bq_multi_agent_app.sub_agents.bqml_agents.tools import check_bq_models  # noqa: F401


# ---------------------------------------------------------------------------
# bqml_toolset – basic instantiation
# ---------------------------------------------------------------------------


def test_bqml_toolset_is_instantiated():
    from bq_multi_agent_app.sub_agents.bqml_agents.tools import bqml_toolset

    assert bqml_toolset is not None


def test_google_cloud_bigquery_not_imported_in_bqml_tools():
    """Direct use of google.cloud.bigquery (ADC-based) must not appear in
    bqml tools after removing check_bq_models."""
    import importlib
    import sys

    # Re-import the module fresh to inspect its globals.
    mod_name = "bq_multi_agent_app.sub_agents.bqml_agents.tools"
    if mod_name in sys.modules:
        mod = sys.modules[mod_name]
    else:
        mod = importlib.import_module(mod_name)

    assert "bigquery" not in [
        name
        for name, obj in vars(mod).items()
        if hasattr(obj, "__module__")
        and "google.cloud.bigquery" in getattr(obj, "__module__", "")
    ]
