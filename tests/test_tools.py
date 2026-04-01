"""
Tests for root-level tools in tools.py.

Verifies module-level structure of the toolsets: ca_toolset, ds_toolset,
and data_agent_toolset. No external API calls are made.
"""


# ---------------------------------------------------------------------------
# ca_toolset
# ---------------------------------------------------------------------------


def test_ca_toolset_is_instantiated():
    from bq_multi_agent_app.tools import ca_toolset

    assert ca_toolset is not None


def test_ds_toolset_is_instantiated():
    from bq_multi_agent_app.tools import ds_toolset

    assert ds_toolset is not None


def test_data_agent_toolset_is_instantiated():
    from bq_multi_agent_app.tools import data_agent_toolset

    assert data_agent_toolset is not None


def test_ca_toolset_and_ds_toolset_are_different_objects():
    from bq_multi_agent_app.tools import ca_toolset, ds_toolset

    assert ca_toolset is not ds_toolset


# ---------------------------------------------------------------------------
# Removed symbols — ensure clean removal of old AgentTool wrapper
# ---------------------------------------------------------------------------


def test_call_data_science_agent_is_removed():
    import bq_multi_agent_app.tools as tools_module

    assert not hasattr(tools_module, "call_data_science_agent"), (
        "call_data_science_agent should have been removed from tools.py"
    )


def test_build_ds_request_is_removed():
    import bq_multi_agent_app.tools as tools_module

    assert not hasattr(tools_module, "_build_ds_request"), (
        "_build_ds_request should have been removed from tools.py"
    )


def test_ds_agent_tool_is_removed():
    import bq_multi_agent_app.tools as tools_module

    assert not hasattr(tools_module, "_ds_agent_tool"), (
        "_ds_agent_tool should have been removed from tools.py"
    )


def test_bigquery_toolset_alias_is_removed():
    import bq_multi_agent_app.tools as tools_module

    assert not hasattr(tools_module, "bigquery_toolset"), (
        "bigquery_toolset was renamed to ca_toolset; old name should be gone"
    )
