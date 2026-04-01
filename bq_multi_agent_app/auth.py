"""Bridge OAuth token from Gemini Enterprise to ADK toolset token caches.

When an ADK agent is registered with Gemini Enterprise and the user completes
the OAuth consent flow, Gemini Enterprise stores the access token in
tool_context.state[AUTH_RESOURCE_ID] (keyed by the authorization resource ID,
e.g. "bq-oauth").

ADK's BigQueryToolset and DataAgentToolset look for cached credentials at
different keys ("bigquery_token_cache" and "data_agent_token_cache"
respectively). Without bridging, every tool call returns:
    "User authorization is required to access Google services for <tool>."

The bridge_oauth_token before_tool_callback copies the token from the Gemini
Enterprise key to both ADK toolset cache keys on every tool call. Always
overwriting ensures that if Gemini Enterprise issues a new token mid-session
(e.g. after the user re-authorizes with a wider scope), the toolsets pick it
up immediately rather than continuing to use a stale cached token.

This callback must be set on every agent (root and sub-agents) because ADK
does not inherit before_tool_callback from parent to sub-agents.
"""

import json
import logging
import os
from datetime import UTC, datetime, timedelta
from typing import Any

from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext

logger = logging.getLogger(__name__)

# Must match the AUTH_ID used in deployment/register_gemini_enterprise.sh and
# the authorization resource name registered with Gemini Enterprise.
_AUTH_RESOURCE_ID = os.getenv("AUTH_ID", "bq-oauth")

# ADK toolset token cache keys.
_BQ_TOKEN_CACHE_KEY = "bigquery_token_cache"
_DA_TOKEN_CACHE_KEY = "data_agent_token_cache"

# Use cloud-platform scope to cover BigQuery, Dataplex, and any other GCP
# APIs the toolsets may call. The narrower bigquery-only scope would cause
# failures if any tool calls a Dataplex API internally (BigQueryCredentialsConfig
# defaults include dataplex.read-write).
_BQ_SCOPE = "https://www.googleapis.com/auth/cloud-platform"


async def bridge_oauth_token(
    tool: BaseTool,
    args: dict[str, Any],
    tool_context: ToolContext,
) -> dict | None:
    """Copy the Gemini Enterprise OAuth token to ADK toolset token caches.

    Reads the access token placed by Gemini Enterprise at
    tool_context.state[AUTH_RESOURCE_ID] and writes a
    google.oauth2.credentials.Credentials-compatible JSON entry to both ADK
    toolset cache keys on every tool call. Always overwriting ensures a new
    token issued by Gemini Enterprise (e.g. after re-authorization with a
    wider scope) is picked up immediately.

    Returns None in all cases so tool execution always proceeds normally.

    Args:
        tool: The tool about to be invoked (unused, required by callback API).
        args: The tool call arguments (unused, required by callback API).
        tool_context: The tool context providing access to session state.

    Returns:
        None — the tool is never short-circuited by this callback.
    """
    access_token = tool_context.state.get(_AUTH_RESOURCE_ID)
    if not access_token:
        # No token from Gemini Enterprise yet — the ADK toolset will trigger
        # the OAuth flow itself via request_credential().
        logger.debug(
            "bridge_oauth_token: no token at state key '%s', skipping",
            _AUTH_RESOURCE_ID,
        )
        return None

    client_id = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "")
    client_secret = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", "")
    expiry = (datetime.now(UTC) + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    token_json = json.dumps(
        {
            "token": access_token,
            # Gemini Enterprise server-side OAuth does not return a refresh token.
            # The access token is valid for ~1 hour; the user will re-authorize on
            # the next session.
            "refresh_token": "",
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": client_id,
            "client_secret": client_secret,
            "scopes": [_BQ_SCOPE],
            "expiry": expiry,
        }
    )

    for cache_key in (_BQ_TOKEN_CACHE_KEY, _DA_TOKEN_CACHE_KEY):
        tool_context.state[cache_key] = token_json
        logger.debug(
            "bridge_oauth_token: token written from '%s' to '%s'",
            _AUTH_RESOURCE_ID,
            cache_key,
        )

    return None
