"""
Deploy the BigQuery Multi-Agent App to Vertex AI Agent Engine.

Uses the Python SDK AdkApp wrapper, which is the canonical deployment path
recommended by the ADK documentation for Agent Engine targets.

Usage:
    uv run python deployment/deploy.py

Required environment variables (.env or shell):
    GOOGLE_CLOUD_PROJECT   - GCP project ID
    GOOGLE_CLOUD_LOCATION  - GCP region (e.g. us-central1)
    GCS_STAGING_BUCKET     - GCS URI for staging artifacts (e.g. gs://my-bucket)

Optional:
    AGENT_ENGINE_DISPLAY_NAME - Display name for the deployed agent
                                (default: "BigQuery Multi-Agent App")
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load .env from repo root (two levels up from this file).
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

import vertexai  # noqa: E402 -- must import after env vars are loaded
from google.adk.deploy import AdkApp  # noqa: E402
from vertexai import agent_engines  # noqa: E402

_REQUIRED_VARS = [
    "GOOGLE_CLOUD_PROJECT",
    "GOOGLE_CLOUD_LOCATION",
    "GCS_STAGING_BUCKET",
]


def _check_env() -> dict[str, str]:
    """Validate required environment variables and return them."""
    missing = [v for v in _REQUIRED_VARS if not os.getenv(v)]
    if missing:
        print(f"Error: missing required environment variables: {', '.join(missing)}")
        print("Copy .env.example to .env and fill in the values.")
        sys.exit(1)
    return {v: os.environ[v] for v in _REQUIRED_VARS}


def main() -> None:
    """Deploy the root agent to Vertex AI Agent Engine."""
    env = _check_env()

    project_id = env["GOOGLE_CLOUD_PROJECT"]
    location = env["GOOGLE_CLOUD_LOCATION"]
    staging_bucket = env["GCS_STAGING_BUCKET"]
    display_name = os.getenv("AGENT_ENGINE_DISPLAY_NAME", "BigQuery Multi-Agent App")

    # Import root_agent here so that ADK module-level side-effects (toolset
    # registration, etc.) happen after the env vars are loaded.
    from bq_multi_agent_app import agent as agent_module  # noqa: PLC0415

    root_agent = agent_module.root_agent

    vertexai.init(project=project_id, location=location, staging_bucket=staging_bucket)

    print(f"Deploying '{display_name}' to Agent Engine...")
    print(f"  Project : {project_id}")
    print(f"  Location: {location}")
    print(f"  Staging : {staging_bucket}")

    adk_app = AdkApp(agent=root_agent)

    # Environment variables forwarded to Agent Engine Runtime.
    # Telemetry vars enable Cloud Trace + prompt/response logging.
    runtime_env_vars = {
        "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": "true",
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "true",
    }
    # Forward app-specific env vars if set.
    _optional_env_vars = [
        "GOOGLE_GENAI_USE_VERTEXAI",
        "GOOGLE_CLOUD_PROJECT",
        "GOOGLE_CLOUD_LOCATION",
        "CODE_INTERPRETER_EXTENSION_NAME",
        "GOOGLE_OAUTH_CLIENT_ID",
        "GOOGLE_OAUTH_CLIENT_SECRET",
        "BQML_RAG_CORPUS_NAME",
    ]
    for var in _optional_env_vars:
        val = os.getenv(var)
        if val:
            runtime_env_vars[var] = val

    # Memory Bank: 4 managed topics + 1 custom domain topic.
    # Provides cross-session conversation persistence in Gemini Enterprise.
    # PreloadMemoryTool and LoadMemoryTool in the agent read from this bank.
    memory_bank_config = {
        "customization_configs": [
            {
                "memory_topics": [
                    {
                        "managed_memory_topic": {
                            "managed_topic_enum": "USER_PERSONAL_INFO"
                        }
                    },
                    {
                        "managed_memory_topic": {
                            "managed_topic_enum": "USER_PREFERENCES"
                        }
                    },
                    {
                        "managed_memory_topic": {
                            "managed_topic_enum": "KEY_CONVERSATION_DETAILS"
                        }
                    },
                    {
                        "managed_memory_topic": {
                            "managed_topic_enum": "EXPLICIT_INSTRUCTIONS"
                        }
                    },
                    {
                        "custom_memory_topic": {
                            "label": "data_analysis_context",
                            "description": (
                                "User's frequently used datasets, tables, preferred analysis "
                                "patterns, domain-specific context about their data, and "
                                "recurring analytical questions."
                            ),
                        }
                    },
                ]
            }
        ]
    }

    deployed = agent_engines.create(
        agent_engine=adk_app,
        config={
            "display_name": display_name,
            "requirements": [
                "google-cloud-aiplatform[agent_engines,adk]",
            ],
            "env_vars": runtime_env_vars,
            "context_spec": {
                "memory_bank_config": memory_bank_config,
            },
        },
    )

    resource_name = deployed.resource_name
    print("\nDeployment complete.")
    print(f"  Resource name: {resource_name}")
    print("\nAdd to your .env:")
    print(f"  AGENT_ENGINE_RESOURCE_NAME={resource_name}")


if __name__ == "__main__":
    main()
