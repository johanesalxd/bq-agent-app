#!/usr/bin/env python3
"""
Shared utilities for Vertex AI Code Interpreter extension management.
"""

import json
import subprocess
import sys
from typing import Any


def get_access_token() -> str:
    """Get access token using gcloud auth.

    Returns:
        The current access token string.
    """
    try:
        result = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting access token: {e.stderr}")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("Error: gcloud auth print-access-token timed out after 30s")
        sys.exit(1)


def get_project_id() -> str:
    """Get the current project ID from gcloud config.

    Returns:
        The active GCP project ID.
    """
    try:
        result = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        project_id = result.stdout.strip()
        if not project_id:
            print(
                "No project ID found. Set it with: gcloud config set project PROJECT_ID"
            )
            sys.exit(1)
        return project_id
    except subprocess.CalledProcessError as e:
        print(f"Error getting project ID: {e.stderr}")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("Error: gcloud config get-value timed out after 30s")
        sys.exit(1)


def get_project_number(project_id: str) -> str:
    """Get the project number from project ID.

    Args:
        project_id: The GCP project ID.

    Returns:
        The numeric project number string.
    """
    try:
        result = subprocess.run(
            [
                "gcloud",
                "projects",
                "describe",
                project_id,
                "--format=value(projectNumber)",
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting project number: {e.stderr}")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("Error: gcloud projects describe timed out after 30s")
        sys.exit(1)


def make_api_request(
    method: str,
    url: str,
    headers: dict[str, str],
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Make an API request using curl.

    Args:
        method: HTTP method (GET, POST, DELETE).
        url: Target URL.
        headers: HTTP headers dict (must include Authorization).
        data: Optional JSON body for POST requests.

    Returns:
        Parsed JSON response dict, or {"error": ...} on failure.
    """
    curl_command = [
        "curl",
        "-s",
        "-X",
        method,
        "-H",
        f"Authorization: {headers['Authorization']}",
        "-H",
        "Content-Type: application/json",
    ]

    if data:
        curl_command.extend(["-d", json.dumps(data)])

    curl_command.append(url)

    try:
        result = subprocess.run(
            curl_command,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )

        if result.stdout.strip():
            return json.loads(result.stdout)
        return {}
    except subprocess.CalledProcessError as e:
        print(f"Error making API request: {e.stderr}")
        return {"error": e.stderr}
    except subprocess.TimeoutExpired:
        print(f"Error: curl request to {url} timed out after 30s")
        return {"error": "request timed out"}
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return {"error": "invalid JSON response"}
