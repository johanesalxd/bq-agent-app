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

main() {
    # Load .env if present.
    if [[ -f "$(dirname "$0")/../.env" ]]; then
        # shellcheck disable=SC1091
        source "$(dirname "$0")/../.env"
    fi

    local project_id="${GOOGLE_CLOUD_PROJECT:?GOOGLE_CLOUD_PROJECT is required}"
    local location="${GOOGLE_CLOUD_LOCATION:-us-central1}"
    local reasoning_engine="${AGENT_ENGINE_RESOURCE_NAME:?AGENT_ENGINE_RESOURCE_NAME is required}"
    local as_app="${GEMINI_ENTERPRISE_APP_ID:?GEMINI_ENTERPRISE_APP_ID is required}"
    local display_name="${AGENT_DISPLAY_NAME:-BigQuery Multi-Agent App}"

    local access_token
    access_token="$(gcloud auth print-access-token)"
    local project_number
    project_number="$(gcloud projects describe "${project_id}" --format='value(projectNumber)')"

    echo "=== Registering Agent with Gemini Enterprise ==="
    echo "  Project    : ${project_id} (${project_number})"
    echo "  Location   : ${location}"
    echo "  Engine     : ${reasoning_engine}"
    echo "  App ID     : ${as_app}"
    echo "  Agent name : ${display_name}"
    echo ""

    local register_url
    register_url="https://discoveryengine.googleapis.com/v1alpha/projects/${project_number}/locations/global/collections/default_collection/engines/${as_app}/assistants/default_assistant/agents"

    # Build JSON payload safely using printf to avoid special-character issues.
    local payload
    payload="$(printf '{"displayName":"%s","agentstoreAgentConfig":{"vertexAiReasoningEngineId":"%s"}}' \
        "${display_name}" "${reasoning_engine}")"

    local response
    response="$(curl -s -X POST \
        -H "Authorization: Bearer ${access_token}" \
        -H "Content-Type: application/json" \
        -d "${payload}" \
        "${register_url}")"

    echo "Response:"
    echo "${response}" | python3 -m json.tool 2>/dev/null || echo "${response}"

    if echo "${response}" | grep -q '"name"'; then
        echo ""
        echo "Agent registered successfully."
        echo "View it in the Gemini Enterprise console:"
        echo "  https://console.cloud.google.com/gen-app-builder/engines?project=${project_id}"
    else
        echo ""
        echo "Registration may have failed -- check the response above."
        exit 1
    fi
}

main "$@"
