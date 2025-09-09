#!/usr/bin/env python3
"""
Detailed test to get the full error message from the conversational analytics tool.
"""

import os
import json
import requests
from dotenv import load_dotenv
import google.auth
from google.auth.transport.requests import Request

# Load environment variables
load_dotenv()

TOOLBOX_URL = os.getenv("TOOLBOX_URL")
BIGQUERY_PROJECT = os.getenv("BIGQUERY_PROJECT")

def get_detailed_error():
    """Get the detailed error from conversational analytics tool"""

    # Get cloud-platform scoped token
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    request = Request()
    credentials.refresh(request)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {credentials.token}"
    }

    # Test conversational analytics with a simple query
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "bigquery-conversational-analytics",
            "arguments": {
                "user_query_with_context": "What is the structure of this table?",
                "table_references": json.dumps([{
                    "projectId": BIGQUERY_PROJECT,
                    "datasetId": "samples",
                    "tableId": "shakespeare"
                }])
            }
        }
    }

    try:
        response = requests.post(
            f"{TOOLBOX_URL}/mcp",
            headers=headers,
            json=payload,
            timeout=60
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("Full response:")
            print(json.dumps(result, indent=2))
        else:
            print(f"Error response:")
            print(response.text)

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    get_detailed_error()
