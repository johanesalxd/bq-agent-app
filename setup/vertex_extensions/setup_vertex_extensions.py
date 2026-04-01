#!/usr/bin/env python3
"""
Create a Vertex AI Code Interpreter extension.

Based on the official Google Cloud documentation:
https://cloud.google.com/vertex-ai/generative-ai/docs/extensions/code-interpreter

Usage:
    uv run python setup/vertex_extensions/setup_vertex_extensions.py
"""

import os
import sys
from typing import Any

# Allow running from project root: add this script's directory to sys.path so
# that "from utils import ..." resolves correctly regardless of working directory.
sys.path.insert(0, os.path.dirname(__file__))

from utils import get_access_token  # noqa: E402
from utils import get_project_id  # noqa: E402
from utils import get_project_number  # noqa: E402
from utils import make_api_request  # noqa: E402


def create_code_interpreter_extension(
    project_id: str, region: str = "us-central1"
) -> dict[str, Any]:
    """Create a new Code Interpreter extension.

    Args:
        project_id: GCP project ID.
        region: GCP region (default: us-central1).

    Returns:
        The API response dict for the created extension.
    """
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    url = (
        f"https://{region}-aiplatform.googleapis.com/v1beta1"
        f"/projects/{project_id}/locations/{region}/extensions:import"
    )

    extension_data = {
        "displayName": "Code Interpreter Extension",
        "description": "Code Interpreter for data analysis",
        "manifest": {
            "name": "code_interpreter_tool",
            "description": "A Google Code Interpreter tool",
            "apiSpec": {
                "openApiGcsUri": "gs://vertex-extension-public/code_interpreter.yaml"
            },
            "authConfig": {
                "authType": "GOOGLE_SERVICE_ACCOUNT_AUTH",
                "googleServiceAccountConfig": {},
            },
        },
        "runtimeConfig": {"codeInterpreterRuntimeConfig": {}},
    }

    print(f"Creating Code Interpreter extension in project {project_id}...")
    response = make_api_request("POST", url, headers, extension_data)

    if "error" in response:
        print(f"Error creating extension: {response['error']}")
        sys.exit(1)

    return response


def main() -> None:
    """Create a Code Interpreter extension and print the resource name."""
    print("Vertex AI Code Interpreter Extension Setup")
    print("=" * 50)

    project_id = get_project_id()
    project_number = get_project_number(project_id)
    region = "us-central1"

    print(f"Project ID    : {project_id}")
    print(f"Project Number: {project_number}")
    print(f"Region        : {region}")
    print()

    extension = create_code_interpreter_extension(project_id, region)

    extension_name = extension.get("name", "")
    extension_id = extension_name.split("/")[-1] if extension_name else "Unknown"

    print("\nExtension created successfully.")
    print("\n" + "=" * 50)
    print("Add this line to your .env file:")
    print("=" * 50)
    print(
        f"CODE_INTERPRETER_EXTENSION_NAME="
        f"projects/{project_number}/locations/{region}/extensions/{extension_id}"
    )
    print("=" * 50)


if __name__ == "__main__":
    main()
