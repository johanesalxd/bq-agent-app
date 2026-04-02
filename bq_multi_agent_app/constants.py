"""
Shared constants for the BigQuery Multi-Agent App.

Centralised here to avoid circular imports between agent.py and sub-agents.
"""

import os

# Gemini 3 models are only available on the Vertex AI global endpoint
# (https://aiplatform.googleapis.com/), not on regional endpoints.
# The google.genai.Client reads GOOGLE_CLOUD_LOCATION to construct the base URL.
# We set it here — before any Gemini client is instantiated — so that the
# AdkApp template's fallback (which sets it to the Agent Engine region) is
# preempted. Sessions and memory use GOOGLE_CLOUD_AGENT_ENGINE_LOCATION, which
# the AdkApp template sets independently from the deployment region.
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"

# Gemini model used by all agents. Change here to update the whole system.
MODEL_NAME = "gemini-3.1-pro-preview"
