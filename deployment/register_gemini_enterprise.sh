#!/bin/bash
#
# Register the deployed Agent Engine with Gemini Enterprise (formerly Agentspace).
#
# Prerequisites:
#   - Agent Engine must already be deployed (run deployment/deploy.py first).
#   - AGENT_ENGINE_RESOURCE_NAME must be set to the fully-qualified resource name
#     returned by deploy.py, e.g.:
#       projects/PROJECT_NUMBER/locations/REGION/reasoningEngines/ENGINE_ID
#   - Discovery Engine API must be enabled.
#   - OAuth 2.0 client must be configured with the Gemini Enterprise redirect URIs:
#       https://vertexaisearch.cloud.google.com/oauth-redirect
#       https://vertexaisearch.cloud.google.com/static/oauth/oauth.html
#
# Usage:
#   chmod +x deployment/register_gemini_enterprise.sh
#   ./deployment/register_gemini_enterprise.sh
#
# Environment variables (read from .env or shell):
#   GOOGLE_CLOUD_PROJECT         - GCP project ID
#   GOOGLE_CLOUD_LOCATION        - GCP region (default: us-central1)
#   AGENT_ENGINE_RESOURCE_NAME   - Fully-qualified Agent Engine resource name
#   GEMINI_ENTERPRISE_APP_ID     - Gemini Enterprise app ID (found in console)
#   AGENT_DISPLAY_NAME           - Display name shown in Gemini Enterprise
#
# References:
#   https://cloud.google.com/products/gemini/enterprise
#   https://cloud.google.com/generative-ai-app-builder/docs/agent-engine

set -e

# Load .env if present.
if [[ -f "$(dirname "$0")/../.env" ]]; then
    # shellcheck disable=SC1091
    source "$(dirname "$0")/../.env"
fi

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:?GOOGLE_CLOUD_PROJECT is required}"
LOCATION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
REASONING_ENGINE="${AGENT_ENGINE_RESOURCE_NAME:?AGENT_ENGINE_RESOURCE_NAME is required}"
AS_APP="${GEMINI_ENTERPRISE_APP_ID:?GEMINI_ENTERPRISE_APP_ID is required}"
DISPLAY_NAME="${AGENT_DISPLAY_NAME:-BigQuery Multi-Agent App}"

ACCESS_TOKEN="$(gcloud auth print-access-token)"
PROJECT_NUMBER="$(gcloud projects describe "${PROJECT_ID}" --format='value(projectNumber)')"

echo "=== Registering Agent with Gemini Enterprise ==="
echo "  Project    : ${PROJECT_ID} (${PROJECT_NUMBER})"
echo "  Location   : ${LOCATION}"
echo "  Engine     : ${REASONING_ENGINE}"
echo "  App ID     : ${AS_APP}"
echo "  Agent name : ${DISPLAY_NAME}"
echo ""

REGISTER_URL="https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_NUMBER}/locations/global/collections/default_collection/engines/${AS_APP}/assistants/default_assistant/agents"

PAYLOAD="$(cat <<JSON
{
  "displayName": "${DISPLAY_NAME}",
  "agentstoreAgentConfig": {
    "vertexAiReasoningEngineId": "${REASONING_ENGINE}"
  }
}
JSON
)"

RESPONSE="$(curl -s -X POST \
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "${PAYLOAD}" \
    "${REGISTER_URL}")"

echo "Response:"
echo "${RESPONSE}" | python3 -m json.tool 2>/dev/null || echo "${RESPONSE}"

if echo "${RESPONSE}" | grep -q '"name"'; then
    echo ""
    echo "Agent registered successfully."
    echo "View it in the Gemini Enterprise console:"
    echo "  https://console.cloud.google.com/gen-app-builder/engines?project=${PROJECT_ID}"
else
    echo ""
    echo "Registration may have failed -- check the response above."
    exit 1
fi
