"""
Tests for root-level tools in tools.py.

Focuses on the pure-function logic that can be verified without external
API calls: the DS request builder and the module-level structure of
call_data_science_agent.
"""

import inspect

import pytest


# ---------------------------------------------------------------------------
# _build_ds_request – pure function, no external deps
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def build_ds_request():
    from bq_multi_agent_app.tools import _build_ds_request

    return _build_ds_request


def test_build_ds_request_includes_question(build_ds_request):
    result = build_ds_request(
        question="What is the average revenue?", data="col_a,col_b\n1,2"
    )
    assert "What is the average revenue?" in result


def test_build_ds_request_includes_data(build_ds_request):
    data_payload = "col_a,col_b\n1,2\n3,4"
    result = build_ds_request(question="Any question", data=data_payload)
    assert data_payload in result


def test_build_ds_request_contains_analysis_instructions(build_ds_request):
    result = build_ds_request(question="q", data="d")
    lowered = result.lower()
    assert "pandas" in lowered or "analysis" in lowered
    assert "visualiz" in lowered or "matplotlib" in lowered


def test_build_ds_request_returns_string(build_ds_request):
    result = build_ds_request(question="q", data="d")
    assert isinstance(result, str)
    assert len(result) > 0


def test_build_ds_request_question_and_data_are_independent(build_ds_request):
    q1 = build_ds_request(question="question_alpha", data="data_beta")
    q2 = build_ds_request(question="question_gamma", data="data_delta")
    assert "question_alpha" in q1
    assert "data_beta" in q1
    assert "question_gamma" in q2
    assert "data_delta" in q2
    assert "question_alpha" not in q2
    assert "question_gamma" not in q1


# ---------------------------------------------------------------------------
# call_data_science_agent – signature and async contract
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def call_ds_agent_fn():
    from bq_multi_agent_app.tools import call_data_science_agent

    return call_data_science_agent


def test_call_data_science_agent_is_coroutine(call_ds_agent_fn):
    assert inspect.iscoroutinefunction(call_ds_agent_fn)


def test_call_data_science_agent_accepts_question_data_tool_context(call_ds_agent_fn):
    sig = inspect.signature(call_ds_agent_fn)
    params = list(sig.parameters.keys())
    assert "question" in params
    assert "data" in params
    assert "tool_context" in params


# ---------------------------------------------------------------------------
# Module-level toolset objects
# ---------------------------------------------------------------------------


def test_bigquery_toolset_is_instantiated():
    from bq_multi_agent_app.tools import bigquery_toolset

    assert bigquery_toolset is not None


def test_data_agent_toolset_is_instantiated():
    from bq_multi_agent_app.tools import data_agent_toolset

    assert data_agent_toolset is not None


def test_ds_agent_tool_is_instantiated():
    from bq_multi_agent_app.tools import _ds_agent_tool

    assert _ds_agent_tool is not None


def test_ds_agent_tool_wraps_ds_agent():
    from bq_multi_agent_app.tools import _ds_agent_tool
    from bq_multi_agent_app.sub_agents import ds_agent

    # AgentTool exposes the wrapped agent via .agent attribute.
    assert _ds_agent_tool.agent is ds_agent
