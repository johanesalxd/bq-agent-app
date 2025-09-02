#!/usr/bin/env python3
"""
Shared utilities for Vertex AI Code Interpreter extension management.
"""

import json
import subprocess
import sys
from typing import Any, Dict, Optional


def get_access_token() -> str:
    """Get access token using gcloud auth."""
    try:
        result = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting access token: {e.stderr}")
        sys.exit(1)


def get_project_id() -> str:
    """Get the current project ID from gcloud config."""
    try:
        result = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True,
            text=True,
            check=True
        )
        project_id = result.stdout.strip()
        if not project_id:
            print(
                "No project ID found. Please set your project with: gcloud config set project PROJECT_ID")
            sys.exit(1)
        return project_id
    except subprocess.CalledProcessError as e:
        print(f"Error getting project ID: {e.stderr}")
        sys.exit(1)


def get_project_number(project_id: str) -> str:
    """Get the project number from project ID."""
    try:
        result = subprocess.run(
            ["gcloud", "projects", "describe", project_id,
                "--format=value(projectNumber)"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting project number: {e.stderr}")
        sys.exit(1)


def make_api_request(method: str, url: str, headers: Dict[str, str], data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Make an API request using curl."""
    curl_command = [
        "curl", "-s", "-X", method,
        "-H", f"Authorization: {headers['Authorization']}",
        "-H", "Content-Type: application/json"
    ]

    if data:
        curl_command.extend(["-d", json.dumps(data)])

    curl_command.append(url)

    try:
        result = subprocess.run(
            curl_command,
            capture_output=True,
            text=True,
            check=True
        )

        if result.stdout.strip():
            return json.loads(result.stdout)
        return {}
    except subprocess.CalledProcessError as e:
        print(f"Error making API request: {e.stderr}")
        return {"error": e.stderr}
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return {"error": "Invalid JSON response"}
