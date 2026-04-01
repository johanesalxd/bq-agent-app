"""
Tests for prompt functions.

Verifies that each prompt function returns a non-empty string and that
critical routing sections, workflow steps, and security constraints are
present. These act as regression guards against accidental deletion of
key prompt sections.
"""

import os

import pytest


# ---------------------------------------------------------------------------
# Root agent prompt
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def root_instructions():
    from bq_multi_agent_app.prompts import return_instructions_root

    return return_instructions_root()


def test_root_instructions_returns_string(root_instructions):
    assert isinstance(root_instructions, str)
    assert len(root_instructions) > 0


def test_root_instructions_contain_all_routing_paths(root_instructions):
    for path in ("DEFAULT PATH", "ADVANCED PATH", "BQML PATH", "DATA AGENT PATH"):
        assert path in root_instructions, f"Missing '{path}' in root instructions"


def test_root_instructions_contain_schema_first_approach(root_instructions):
    assert "SCHEMA-FIRST" in root_instructions or "schema" in root_instructions.lower()


def test_root_instructions_contain_bqml_routing(root_instructions):
    assert "bqml" in root_instructions.lower()
    assert (
        "sub-agent" in root_instructions.lower()
        or "sub_agent" in root_instructions.lower()
    )


def test_root_instructions_contain_data_agent_routing(root_instructions):
    assert "data agent" in root_instructions.lower()


def test_root_instructions_reference_ask_data_insights(root_instructions):
    # Root agent uses ask_data_insights (CA API) — not bigquery-execute-sql.
    assert "ask_data_insights" in root_instructions


def test_root_instructions_do_not_reference_execute_sql_directly(root_instructions):
    # execute_sql belongs to the DS sub-agent; root prompt should not call it.
    assert "bigquery-execute-sql" not in root_instructions


def test_root_instructions_no_check_bq_models_reference(root_instructions):
    assert "check_bq_models" not in root_instructions


def test_root_instructions_contain_data_presentation_standards(root_instructions):
    lowered = root_instructions.lower()
    assert "first 3" in lowered or "truncat" in lowered or "presentation" in lowered


def test_root_instructions_describe_advanced_path_delegation(root_instructions):
    lowered = root_instructions.lower()
    assert "ds sub-agent" in lowered or "advanced" in lowered


# ---------------------------------------------------------------------------
# BQML agent prompt
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def bqml_instructions():
    from bq_multi_agent_app.sub_agents.bqml_agents.prompts import (
        return_instructions_bqml,
    )

    return return_instructions_bqml()


def test_bqml_instructions_returns_string(bqml_instructions):
    assert isinstance(bqml_instructions, str)
    assert len(bqml_instructions) > 0


def test_bqml_instructions_contain_rag_workflow(bqml_instructions):
    assert "rag_response" in bqml_instructions


def test_bqml_instructions_contain_user_verification_requirement(bqml_instructions):
    lowered = bqml_instructions.lower()
    assert "verification" in lowered or "approval" in lowered or "approve" in lowered


def test_bqml_instructions_contain_information_schema_for_model_listing(
    bqml_instructions,
):
    assert "INFORMATION_SCHEMA" in bqml_instructions
    assert "MODELS" in bqml_instructions


def test_bqml_instructions_no_check_bq_models_reference(bqml_instructions):
    assert "check_bq_models" not in bqml_instructions


def test_bqml_instructions_contain_compute_project(bqml_instructions):
    assert (
        "your-project-id" not in bqml_instructions
        or os.getenv("GOOGLE_CLOUD_PROJECT", "") in bqml_instructions
    )


def test_bqml_instructions_reference_rag_for_syntax(bqml_instructions):
    # SQL model type examples have been removed; the prompt instructs the agent
    # to always query rag_response for authoritative, up-to-date BQML syntax.
    assert "rag_response" in bqml_instructions, (
        "BQML prompt must reference rag_response as the authoritative syntax source"
    )


def test_bqml_instructions_warn_about_long_run_times(bqml_instructions):
    lowered = bqml_instructions.lower()
    assert "time" in lowered and (
        "long" in lowered or "significant" in lowered or "hours" in lowered
    )


# ---------------------------------------------------------------------------
# DS agent prompt
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def ds_instructions():
    from bq_multi_agent_app.sub_agents.ds_agents.prompts import return_instructions_ds

    return return_instructions_ds()


def test_ds_instructions_returns_string(ds_instructions):
    assert isinstance(ds_instructions, str)
    assert len(ds_instructions) > 0


def test_ds_instructions_mention_core_libraries(ds_instructions):
    for lib in ("pandas", "numpy", "matplotlib"):
        assert lib in ds_instructions.lower(), f"Missing library reference: {lib}"


def test_ds_instructions_contain_response_format_section(ds_instructions):
    assert "Analysis Summary" in ds_instructions or "Response Format" in ds_instructions


def test_ds_instructions_contain_pip_install_constraint(ds_instructions):
    assert "pip install" in ds_instructions.lower()
    assert "forbidden" in ds_instructions.lower() or "never" in ds_instructions.lower()


def test_ds_instructions_contain_visualization_guidance(ds_instructions):
    lowered = ds_instructions.lower()
    assert "visualization" in lowered or "chart" in lowered or "plot" in lowered


def test_ds_instructions_contain_data_presentation_standards(ds_instructions):
    lowered = ds_instructions.lower()
    assert "first 3" in lowered or "truncat" in lowered or "sample" in lowered


def test_ds_instructions_reference_own_bigquery_tools(ds_instructions):
    # DS agent now has its own BigQuery toolset — prompt must reference the tools.
    assert "bigquery-execute-sql" in ds_instructions or "execute_sql" in ds_instructions


def test_ds_instructions_reference_schema_discovery(ds_instructions):
    lowered = ds_instructions.lower()
    assert "schema" in lowered or "discover" in lowered


def test_ds_instructions_do_not_reference_parent_agent_data(ds_instructions):
    # Old prompt referenced receiving data from "parent agent"; new prompt does
    # not since DS agent queries BQ directly.
    assert "parent agent" not in ds_instructions.lower()
