"""
Smoke test for a deployed Agent Engine instance.

Connects to an existing Agent Engine deployment, creates a session,
sends a simple query, and verifies a response is received.

Usage:
    uv run python deployment/test_deployment.py

Required environment variables (.env or shell):
    GOOGLE_CLOUD_PROJECT          - GCP project ID
    GOOGLE_CLOUD_LOCATION         - GCP region
    AGENT_ENGINE_RESOURCE_NAME    - Fully-qualified resource name, e.g.:
                                    projects/.../reasoningEngines/...
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env", override=True)

import vertexai  # noqa: E402
from vertexai import agent_engines  # noqa: E402

_REQUIRED_VARS = [
    "GOOGLE_CLOUD_PROJECT",
    "GOOGLE_CLOUD_LOCATION",
    "AGENT_ENGINE_RESOURCE_NAME",
]

_TEST_USER_ID = "deployment-smoke-test"
_TEST_QUERY = "What BigQuery datasets are available?"


def _check_env() -> dict[str, str]:
    """Validate required environment variables and return them."""
    missing = [v for v in _REQUIRED_VARS if not os.getenv(v)]
    if missing:
        print(f"Error: missing required environment variables: {', '.join(missing)}")
        sys.exit(1)
    return {v: os.environ[v] for v in _REQUIRED_VARS}


def main() -> None:
    """Run a smoke test against the deployed Agent Engine."""
    env = _check_env()

    vertexai.init(
        project=env["GOOGLE_CLOUD_PROJECT"],
        location=env["GOOGLE_CLOUD_LOCATION"],
    )

    resource_name = env["AGENT_ENGINE_RESOURCE_NAME"]
    print(f"Connecting to: {resource_name}")
    adk_app = agent_engines.get(resource_name)
    print(f"  Display name : {adk_app.display_name}")
    print(f"  Resource name: {adk_app.resource_name}")

    # Create a session.
    print("\n--- Creating session ---")
    session = adk_app.create_session(user_id=_TEST_USER_ID)
    session_id = session["id"]
    print(f"Session ID: {session_id}")

    # Send a simple query and collect events.
    print(f"\n--- Querying: '{_TEST_QUERY}' ---")
    events = list(
        adk_app.stream_query(
            user_id=_TEST_USER_ID,
            session_id=session_id,
            message=_TEST_QUERY,
        )
    )
    print(f"Received {len(events)} event(s)")

    response_text = None
    for event in reversed(events):
        parts = event.get("content", {}).get("parts", [])
        for part in parts:
            if part.get("text"):
                response_text = part["text"]
                break
        if response_text:
            break

    if response_text:
        print(f"Agent response (first 300 chars): {response_text[:300]}")
    else:
        print("Warning: no text response found in events")

    # Clean up the test session.
    print("\n--- Deleting session ---")
    try:
        adk_app.delete_session(user_id=_TEST_USER_ID, session_id=session_id)
        print("Session deleted.")
    except Exception as exc:  # noqa: BLE001
        print(f"Warning: could not delete session: {exc}")

    if not events:
        print("\nSmoke test FAILED: no events received from agent.")
        sys.exit(1)

    print("\nSmoke test PASSED.")


if __name__ == "__main__":
    main()
