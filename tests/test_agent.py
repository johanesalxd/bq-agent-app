"""
Tests for agent configurations.

Verifies that all agents have the correct names, models, descriptions,
tool registrations, and sub-agent wiring required by ADK. These tests
catch structural regressions without executing any external API calls.
"""

import pytest


# ---------------------------------------------------------------------------
# Root agent
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def root_agent():
    from bq_multi_agent_app.agent import root_agent as _root_agent

    return _root_agent


def test_root_agent_name(root_agent):
    assert root_agent.name == "bigquery_ds_agent"


def test_root_agent_has_description(root_agent):
    assert root_agent.description
    assert len(root_agent.description) > 0


def test_root_agent_description_mentions_bigquery(root_agent):
    assert "BigQuery" in root_agent.description


def test_root_agent_model_is_set(root_agent):
    assert root_agent.model


def test_root_agent_has_bqml_sub_agent(root_agent):
    sub_agent_names = [a.name for a in root_agent.sub_agents]
    assert "bqml_agent" in sub_agent_names


def test_root_agent_ds_agent_is_not_a_sub_agent(root_agent):
    # DS agent must be tool-wrapped, not a sub-agent, to avoid code
    # execution interpretation errors.
    sub_agent_names = [a.name for a in root_agent.sub_agents]
    assert "ds_agent" not in sub_agent_names


def test_root_agent_has_exactly_one_sub_agent(root_agent):
    assert len(root_agent.sub_agents) == 1


def test_root_agent_tools_include_load_artifacts(root_agent):
    # load_artifacts is the ADK built-in; confirm it is registered.
    tool_names = _tool_names(root_agent)
    assert any("load_artifacts" in n for n in tool_names)


def test_root_agent_has_global_instruction(root_agent):
    assert root_agent.global_instruction
    assert "Data Science" in root_agent.global_instruction


def test_root_agent_has_instruction(root_agent):
    assert root_agent.instruction
    assert len(root_agent.instruction) > 0


# ---------------------------------------------------------------------------
# BQML agent
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def bqml_agent():
    from bq_multi_agent_app.sub_agents.bqml_agents.agent import (
        bqml_agent as _bqml_agent,
    )

    return _bqml_agent


def test_bqml_agent_name(bqml_agent):
    assert bqml_agent.name == "bqml_agent"


def test_bqml_agent_has_description(bqml_agent):
    assert bqml_agent.description
    assert len(bqml_agent.description) > 0


def test_bqml_agent_description_mentions_bqml(bqml_agent):
    assert "BQML" in bqml_agent.description or "BigQuery ML" in bqml_agent.description


def test_bqml_agent_model_is_set(bqml_agent):
    assert bqml_agent.model


def test_bqml_agent_has_no_sub_agents(bqml_agent):
    assert len(bqml_agent.sub_agents) == 0


def test_bqml_agent_has_rag_response_tool(bqml_agent):
    tool_names = _tool_names(bqml_agent)
    assert any("rag_response" in n for n in tool_names)


def test_bqml_agent_does_not_have_check_bq_models(bqml_agent):
    # check_bq_models was removed; model listing now goes through
    # INFORMATION_SCHEMA via bqml_toolset.
    tool_names = _tool_names(bqml_agent)
    assert not any("check_bq_models" in n for n in tool_names)


def test_bqml_agent_has_instruction(bqml_agent):
    assert bqml_agent.instruction
    assert len(bqml_agent.instruction) > 0


# ---------------------------------------------------------------------------
# DS agent
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def ds_agent():
    from bq_multi_agent_app.sub_agents.ds_agents.agent import ds_agent as _ds_agent

    return _ds_agent


def test_ds_agent_name(ds_agent):
    assert ds_agent.name == "ds_agent"


def test_ds_agent_has_description(ds_agent):
    assert ds_agent.description
    assert len(ds_agent.description) > 0


def test_ds_agent_description_mentions_code_execution(ds_agent):
    desc = ds_agent.description.lower()
    assert "python" in desc or "code" in desc or "pandas" in desc


def test_ds_agent_model_is_set(ds_agent):
    assert ds_agent.model


def test_ds_agent_has_code_executor(ds_agent):
    assert ds_agent.code_executor is not None


def test_ds_agent_has_no_sub_agents(ds_agent):
    assert len(ds_agent.sub_agents) == 0


def test_ds_agent_has_no_tools(ds_agent):
    # DS agent relies entirely on code execution; tools list should be empty.
    assert len(ds_agent.tools) == 0


def test_ds_agent_has_instruction(ds_agent):
    assert ds_agent.instruction
    assert len(ds_agent.instruction) > 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _tool_names(agent) -> list[str]:
    """Return a flat list of string identifiers for all tools on an agent.

    ADK tools may be plain functions, FunctionTool wrappers, or Toolset
    objects. We use str() as a reliable way to get a searchable identifier
    without depending on private ADK internals.
    """
    names = []
    for tool in agent.tools:
        names.append(str(tool))
        # Also capture __name__ when available (plain functions)
        if hasattr(tool, "__name__"):
            names.append(tool.__name__)
        if hasattr(tool, "name"):
            names.append(tool.name)
    return names
