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


# ---------------------------------------------------------------------------
# external_access_token_key — no client_id/client_secret on toolsets
# ---------------------------------------------------------------------------


def test_bq_credentials_uses_external_access_token_key():
    from bq_multi_agent_app.tools import _bq_credentials

    assert _bq_credentials.external_access_token_key == "bq-oauth", (
        "_bq_credentials must use external_access_token_key, not client_id/client_secret"
    )


def test_bq_credentials_has_no_client_id():
    from bq_multi_agent_app.tools import _bq_credentials

    assert not getattr(_bq_credentials, "client_id", None), (
        "_bq_credentials must not have client_id set"
    )


def test_data_agent_toolset_uses_external_access_token_key():
    from bq_multi_agent_app.tools import data_agent_toolset

    creds = data_agent_toolset._credentials_config
    assert creds.external_access_token_key == "bq-oauth", (
        "data_agent_toolset must use external_access_token_key"
    )


def test_bqml_toolset_uses_external_access_token_key():
    from bq_multi_agent_app.sub_agents.bqml_agents.tools import bqml_toolset

    creds = bqml_toolset._credentials_config
    assert creds.external_access_token_key == "bq-oauth", (
        "bqml_toolset must use external_access_token_key"
    )
