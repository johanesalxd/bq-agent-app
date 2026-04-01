#!/bin/bash
#
# Register the deployed Agent Engine with Gemini Enterprise (Agentspace).
#
# Prerequisites:
#   - Agent Engine must already be deployed (run deployment/deploy.sh first).
#   - AGENT_ENGINE_RESOURCE_NAME must be set in .env to the fully-qualified
#     resource name returned by deploy.sh, e.g.:
#       projects/PROJECT_NUMBER/locations/REGION/reasoningEngines/ENGINE_ID
#   - GEMINI_ENTERPRISE_APP_ID must be set in .env (found in console).
#   - Discovery Engine API must be enabled.
#
# Usage:
#   chmod +x deployment/register_gemini_enterprise.sh
#   ./deployment/register_gemini_enterprise.sh
#
# References:
#   https://cloud.google.com/gemini/enterprise/docs/register-and-manage-an-adk-agent

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/../.env"

main() {
    if [[ -f "${ENV_FILE}" ]]; then
        # shellcheck disable=SC1091
        source "${ENV_FILE}"
    fi

    local project_id="${GOOGLE_CLOUD_PROJECT:?GOOGLE_CLOUD_PROJECT is required}"
    local reasoning_engine="${AGENT_ENGINE_RESOURCE_NAME:?AGENT_ENGINE_RESOURCE_NAME is required}"
    local as_app="${GEMINI_ENTERPRISE_APP_ID:?GEMINI_ENTERPRISE_APP_ID is required}"
    local display_name="${AGENT_DISPLAY_NAME:-BigQuery Multi-Agent App}"
    # Endpoint location: us, eu, or global. Gemini Enterprise apps are typically global.
    local endpoint_location="${GEMINI_ENTERPRISE_ENDPOINT_LOCATION:-global}"
    # Reasoning engine location extracted from the resource name.
    local reasoning_engine_location
    reasoning_engine_location="$(echo "${reasoning_engine}" | sed 's|.*/locations/\([^/]*\)/.*|\1|')"

    local access_token
    access_token="$(gcloud auth print-access-token)"

    echo "=== Registering Agent with Gemini Enterprise ==="
    echo "  Project      : ${project_id}"
    echo "  Endpoint     : ${endpoint_location}-discoveryengine.googleapis.com"
    echo "  Engine       : ${reasoning_engine}"
    echo "  App ID       : ${as_app}"
    echo "  Display name : ${display_name}"
    echo ""

    local register_url
    register_url="https://${endpoint_location}-discoveryengine.googleapis.com/v1alpha/projects/${project_id}/locations/global/collections/default_collection/engines/${as_app}/assistants/default_assistant/agents"

    local payload
    payload="$(printf '{
  "displayName": "%s",
  "description": "BigQuery analytics, data science, BQML, and conversational analytics via BQ Data Agents.",
  "adk_agent_definition": {
    "provisioned_reasoning_engine": {
      "reasoning_engine": "%s"
    }
  }
}' "${display_name}" "${reasoning_engine}")"

    local response
    response="$(curl -s -X POST \
        -H "Authorization: Bearer ${access_token}" \
        -H "Content-Type: application/json" \
        -H "X-Goog-User-Project: ${project_id}" \
        -d "${payload}" \
        "${register_url}")"

    echo "Response:"
    echo "${response}" | python3 -m json.tool 2>/dev/null || echo "${response}"

    if echo "${response}" | grep -q '"name"'; then
        echo ""
        echo "Agent registered successfully."
        echo "View it in the Gemini Enterprise console:"
        echo "  https://console.cloud.google.com/gemini-enterprise/engines?project=${project_id}"
    else
        echo ""
        echo "Registration may have failed -- check the response above."
        exit 1
    fi
}

main "$@"
