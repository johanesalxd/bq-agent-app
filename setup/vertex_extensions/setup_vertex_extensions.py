#!/usr/bin/env python3
"""
Simple script to create a Vertex AI Code Interpreter extension.

Based on the official Google Cloud documentation:
https://cloud.google.com/vertex-ai/generative-ai/docs/extensions/code-interpreter
"""

import sys
from typing import Any, Dict

from utils import get_access_token
from utils import get_project_id
from utils import get_project_number
from utils import make_api_request


def create_code_interpreter_extension(project_id: str, region: str = "us-central1") -> Dict[str, Any]:
    """Create a new Code Interpreter extension."""
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    url = f"https://{region}-aiplatform.googleapis.com/v1beta1/projects/{project_id}/locations/{region}/extensions:import"

    # Extension configuration
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
                "googleServiceAccountConfig": {}
            }
        },
        "runtimeConfig": {
            "codeInterpreterRuntimeConfig": {}
        }
    }

    print(f"Creating Code Interpreter extension in project {project_id}...")
    response = make_api_request("POST", url, headers, extension_data)

    if "error" in response:
        print(f"Error creating extension: {response['error']}")
        sys.exit(1)

    return response


def main():
    """Main function to create extension and display info."""
    print("Vertex AI Code Interpreter Extension Setup")
    print("=" * 50)

    # Get project ID
    project_id = get_project_id()
    project_number = get_project_number(project_id)
    region = "us-central1"

    print(f"Project ID: {project_id}")
    print(f"Project Number: {project_number}")
    print(f"Region: {region}")
    print()

    # Create the extension
    extension = create_code_interpreter_extension(project_id, region)

    # Extract extension ID from the resource name
    extension_name = extension.get("name", "")
    extension_id = extension_name.split(
        "/")[-1] if extension_name else "Unknown"

    print("\n✓ Extension created successfully!")
    print("\n" + "=" * 50)
    print("Copy this line to your .env file:")
    print("=" * 50)
    print(
        f"projects/{project_number}/locations/{region}/extensions/{extension_id}")
    print("=" * 50)


if __name__ == "__main__":
    main()
