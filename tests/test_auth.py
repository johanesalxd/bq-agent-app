"""
Tests for the bridge_oauth_token before_tool_callback.

Verifies that the callback correctly bridges the Gemini Enterprise OAuth token
from tool_context.state[AUTH_ID] to the ADK toolset token cache keys, and
handles all edge cases without making external API calls.
"""

import asyncio
import importlib
import json
from unittest.mock import MagicMock


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_tool_context(state: dict) -> MagicMock:
    """Create a minimal ToolContext mock backed by the given state dict."""
    ctx = MagicMock()
    ctx.state = state
    return ctx


def _make_tool() -> MagicMock:
    tool = MagicMock()
    tool.name = "list_dataset_ids"
    return tool


def _run(coro):
    """Run a coroutine synchronously."""
    return asyncio.run(coro)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_bridge_writes_to_bq_cache_when_token_present():
    """Token from Gemini Enterprise is written to bigquery_token_cache."""
    state = {"bq-oauth": "ya29.test-access-token"}
    ctx = _make_tool_context(state)

    from bq_multi_agent_app.auth import bridge_oauth_token

    result = _run(bridge_oauth_token(tool=_make_tool(), args={}, tool_context=ctx))

    assert result is None
    assert "bigquery_token_cache" in state
    token_data = json.loads(state["bigquery_token_cache"])
    assert token_data["token"] == "ya29.test-access-token"
    assert token_data["scopes"] == ["https://www.googleapis.com/auth/cloud-platform"]


def test_bridge_writes_to_data_agent_cache_when_token_present():
    """Token from Gemini Enterprise is written to data_agent_token_cache."""
    state = {"bq-oauth": "ya29.test-access-token"}
    ctx = _make_tool_context(state)

    from bq_multi_agent_app.auth import bridge_oauth_token

    _run(bridge_oauth_token(tool=_make_tool(), args={}, tool_context=ctx))

    assert "data_agent_token_cache" in state
    token_data = json.loads(state["data_agent_token_cache"])
    assert token_data["token"] == "ya29.test-access-token"


def test_bridge_returns_none_always():
    """Callback never short-circuits tool execution (always returns None)."""
    from bq_multi_agent_app.auth import bridge_oauth_token

    # With token
    state = {"bq-oauth": "ya29.token"}
    result = _run(
        bridge_oauth_token(
            tool=_make_tool(), args={}, tool_context=_make_tool_context(state)
        )
    )
    assert result is None

    # Without token
    result = _run(
        bridge_oauth_token(
            tool=_make_tool(), args={}, tool_context=_make_tool_context({})
        )
    )
    assert result is None


def test_bridge_skips_when_no_token():
    """No state keys are written when AUTH_ID token is absent."""
    state = {}
    ctx = _make_tool_context(state)

    from bq_multi_agent_app.auth import bridge_oauth_token

    _run(bridge_oauth_token(tool=_make_tool(), args={}, tool_context=ctx))

    assert "bigquery_token_cache" not in state
    assert "data_agent_token_cache" not in state


def test_bridge_overwrites_existing_cache():
    """Existing token caches are always overwritten with the latest token.

    This ensures that if Gemini Enterprise issues a new token mid-session
    (e.g. after the user re-authorizes with a wider scope), the toolsets
    pick it up immediately rather than continuing to use a stale cached token.
    """
    existing = json.dumps({"token": "old-token", "refresh_token": "rt123"})
    state = {
        "bq-oauth": "ya29.new-token",
        "bigquery_token_cache": existing,
        "data_agent_token_cache": existing,
    }
    ctx = _make_tool_context(state)

    from bq_multi_agent_app.auth import bridge_oauth_token

    _run(bridge_oauth_token(tool=_make_tool(), args={}, tool_context=ctx))

    assert json.loads(state["bigquery_token_cache"])["token"] == "ya29.new-token"
    assert json.loads(state["data_agent_token_cache"])["token"] == "ya29.new-token"


def test_bridge_token_json_is_valid_credentials_format():
    """The JSON written to caches is parseable by from_authorized_user_info."""
    import google.oauth2.credentials

    state = {"bq-oauth": "ya29.test-token"}
    ctx = _make_tool_context(state)

    from bq_multi_agent_app.auth import bridge_oauth_token

    _run(bridge_oauth_token(tool=_make_tool(), args={}, tool_context=ctx))

    token_data = json.loads(state["bigquery_token_cache"])
    creds = google.oauth2.credentials.Credentials.from_authorized_user_info(
        token_data, scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    assert creds.token == "ya29.test-token"


def test_bridge_respects_auth_id_env_var(monkeypatch):
    """AUTH_ID env var controls which state key is read."""
    monkeypatch.setenv("AUTH_ID", "custom-auth-id")

    import bq_multi_agent_app.auth as auth_module

    importlib.reload(auth_module)

    state = {"custom-auth-id": "ya29.custom-token"}
    ctx = _make_tool_context(state)

    _run(auth_module.bridge_oauth_token(tool=_make_tool(), args={}, tool_context=ctx))

    assert "bigquery_token_cache" in state
    assert json.loads(state["bigquery_token_cache"])["token"] == "ya29.custom-token"

    # Restore module state.
    monkeypatch.delenv("AUTH_ID", raising=False)
    importlib.reload(auth_module)
