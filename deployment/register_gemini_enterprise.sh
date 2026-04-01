#!/bin/bash
#
# Register the deployed Agent Engine with Gemini Enterprise (Agentspace).
#
# This script is idempotent. On each run it:
#   - Step 1: Deletes any existing custom ADK agent registrations (those with
#             a provisionedReasoningEngine). Leaves Google built-in agents
#             (e.g. deep_research) untouched.
#   - Step 2: Creates or replaces the authorization resource with the current
#             OAuth credentials from .env (delete + recreate, because PATCH
#             silently ignores credential fields — Discovery Engine API bug).
#   - Step 3: Registers the agent with authorization_config.
#
# Steps are ordered so that the auth resource is never deleted while an agent
# still references it (which would cause a FAILED_PRECONDITION error).
#
# Prerequisites:
#   - Agent Engine must already be deployed (run deployment/deploy.sh first).
#   - The following vars must be set in .env:
#       AGENT_ENGINE_RESOURCE_NAME  fully-qualified reasoning engine resource name
#       GEMINI_ENTERPRISE_APP_ID    found in the Gemini Enterprise console
#       GOOGLE_CLOUD_PROJECT        project ID
#       GOOGLE_CLOUD_PROJECT_NUMBER project number (digits only)
#       GOOGLE_OAUTH_CLIENT_ID      OAuth 2.0 client ID
#       GOOGLE_OAUTH_CLIENT_SECRET  OAuth 2.0 client secret
#   - Optional:
#       AGENT_DISPLAY_NAME                   defaults to "BigQuery Multi-Agent App"
#       GEMINI_ENTERPRISE_ENDPOINT_LOCATION  defaults to "global"
#       AUTH_ID                              defaults to "bq-oauth"
#
# Usage:
#   chmod +x deployment/register_gemini_enterprise.sh
#   ./deployment/register_gemini_enterprise.sh
#
# References:
#   https://cloud.google.com/gemini/enterprise/docs/register-and-manage-an-adk-agent

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/../.env"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# pretty JSON_STRING — print as indented JSON, or raw on parse failure.
pretty() {
    echo "${1}" | python3 -m json.tool 2>/dev/null || echo "${1}"
}

# http_body CURL_RESPONSE — extract body (everything except the last status line).
http_body() {
    echo "${1}" | python3 -c "
import sys
lines = sys.stdin.read().splitlines()
print('\n'.join(lines[:-1]))
"
}

# http_status CURL_RESPONSE — extract the trailing HTTP status code line.
http_status() {
    echo "${1}" | tail -n1
}

main() {
    if [[ -f "${ENV_FILE}" ]]; then
        # shellcheck disable=SC1091
        source "${ENV_FILE}"
    fi

    local project_id="${GOOGLE_CLOUD_PROJECT:?GOOGLE_CLOUD_PROJECT is required}"
    local project_number="${GOOGLE_CLOUD_PROJECT_NUMBER:?GOOGLE_CLOUD_PROJECT_NUMBER is required}"
    local reasoning_engine="${AGENT_ENGINE_RESOURCE_NAME:?AGENT_ENGINE_RESOURCE_NAME is required}"
    local as_app="${GEMINI_ENTERPRISE_APP_ID:?GEMINI_ENTERPRISE_APP_ID is required}"
    local oauth_client_id="${GOOGLE_OAUTH_CLIENT_ID:?GOOGLE_OAUTH_CLIENT_ID is required}"
    local oauth_client_secret="${GOOGLE_OAUTH_CLIENT_SECRET:?GOOGLE_OAUTH_CLIENT_SECRET is required}"
    local display_name="${AGENT_DISPLAY_NAME:-BigQuery Multi-Agent App}"
    # Endpoint location: us, eu, or global.
    local endpoint_location="${GEMINI_ENTERPRISE_ENDPOINT_LOCATION:-global}"
    # Authorization resource ID (arbitrary alphanumeric, stable across re-runs).
    local auth_id="${AUTH_ID:-bq-oauth}"

    local access_token
    access_token="$(gcloud auth print-access-token)"

    local base_url="https://${endpoint_location}-discoveryengine.googleapis.com/v1alpha"
    local auth_resource_url="${base_url}/projects/${project_id}/locations/global/authorizations"
    local auth_resource_name_url="${auth_resource_url}/${auth_id}"
    local agents_url="${base_url}/projects/${project_id}/locations/global/collections/default_collection/engines/${as_app}/assistants/default_assistant/agents"

    # Construct the authorization URI. cloud-platform scope covers BigQuery,
    # Dataplex, and other GCP APIs the toolsets may call internally.
    local bq_scope="https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcloud-platform"
    local redirect_uri="https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fstatic%2Foauth%2Foauth.html"
    local auth_uri
    auth_uri="https://accounts.google.com/o/oauth2/v2/auth"
    auth_uri+="?client_id=${oauth_client_id}"
    auth_uri+="&redirect_uri=${redirect_uri}"
    auth_uri+="&scope=${bq_scope}"
    auth_uri+="&include_granted_scopes=true"
    auth_uri+="&response_type=code"
    auth_uri+="&access_type=offline"
    auth_uri+="&prompt=consent"

    echo "=== BigQuery Multi-Agent: Gemini Enterprise Registration ==="
    echo "  Project ID     : ${project_id}"
    echo "  Project Number : ${project_number}"
    echo "  Endpoint       : ${endpoint_location}-discoveryengine.googleapis.com"
    echo "  Reasoning engine: ${reasoning_engine}"
    echo "  App ID         : ${as_app}"
    echo "  Display name   : ${display_name}"
    echo "  Auth ID        : ${auth_id}"
    echo ""

    # -----------------------------------------------------------------------
    # Step 1: Delete any existing agent registration pointing to our engine
    # -----------------------------------------------------------------------
    # Must happen BEFORE touching the auth resource — deleting an auth resource
    # while an agent still references it causes FAILED_PRECONDITION.
    # -----------------------------------------------------------------------
    echo "--- Step 1: Remove existing agent registrations ---"

    local list_response
    list_response="$(curl -s \
        -H "Authorization: Bearer ${access_token}" \
        -H "X-Goog-User-Project: ${project_id}" \
        "${agents_url}")"

    # Filter to custom ADK agents only (those with a provisionedReasoningEngine).
    # This preserves Google built-in agents (e.g. deep_research) which have no
    # adkAgentDefinition, while deleting ALL prior custom registrations regardless
    # of which reasoning engine they point to. This handles the case where the
    # agent was redeployed and the engine resource name changed.
    local existing_agents
    existing_agents="$(echo "${list_response}" | python3 -c "
import json, sys
data = json.load(sys.stdin)
agents = data.get('agents', [])
for a in agents:
    name = a.get('name', '')
    has_engine = bool(
        a.get('adkAgentDefinition', {})
         .get('provisionedReasoningEngine', {})
         .get('reasoningEngine', '')
    )
    if name and has_engine:
        print(name)
" 2>/dev/null || true)"

    local agents_deleted=false
    if [[ -n "${existing_agents}" ]]; then
        echo "Found existing agent(s) -- deleting:"
        while IFS= read -r agent_name; do
            echo "  Deleting: ${agent_name}"
            local del_status
            del_status="$(curl -s -o /dev/null -w "%{http_code}" -X DELETE \
                -H "Authorization: Bearer ${access_token}" \
                -H "X-Goog-User-Project: ${project_id}" \
                "${base_url}/${agent_name}")"
            echo "  Delete status: ${del_status}"
        done <<< "${existing_agents}"
        agents_deleted=true
        # Wait for deletions to propagate before touching the auth resource.
        echo "  Waiting 10s for deletions to propagate..."
        sleep 10
    else
        echo "No existing agent registrations found."
    fi
    echo ""

    # -----------------------------------------------------------------------
    # Step 2: Create or replace authorization resource
    # -----------------------------------------------------------------------
    # PATCH silently ignores credential fields (Discovery Engine API bug), so
    # we always delete + recreate to guarantee the current .env credentials
    # are reflected in the resource.
    # -----------------------------------------------------------------------
    echo "--- Step 2: Create or replace authorization resource (${auth_id}) ---"

    local auth_payload
    auth_payload="$(printf '{
  "name": "projects/%s/locations/global/authorizations/%s",
  "serverSideOauth2": {
    "clientId": "%s",
    "clientSecret": "%s",
    "authorizationUri": "%s",
    "tokenUri": "https://oauth2.googleapis.com/token"
  }
}' \
        "${project_id}" \
        "${auth_id}" \
        "${oauth_client_id}" \
        "${oauth_client_secret}" \
        "${auth_uri}")"

    # Check whether the authorization resource already exists.
    local get_response get_status
    get_response="$(curl -s -w "\n%{http_code}" \
        -H "Authorization: Bearer ${access_token}" \
        -H "X-Goog-User-Project: ${project_id}" \
        "${auth_resource_name_url}")"
    get_status="$(http_status "${get_response}")"

    if [[ "${get_status}" == "200" ]]; then
        # Exists — delete it first before recreating.
        echo "Authorization resource exists -- replacing..."
        local del_auth_status
        del_auth_status="$(curl -s -o /dev/null -w "%{http_code}" -X DELETE \
            -H "Authorization: Bearer ${access_token}" \
            -H "X-Goog-User-Project: ${project_id}" \
            "${auth_resource_name_url}")"
        if [[ "${del_auth_status}" != "200" ]]; then
            echo "Failed to delete existing authorization resource (HTTP ${del_auth_status})."
            exit 1
        fi
        echo "  Deleted (HTTP ${del_auth_status})."
    elif [[ "${get_status}" == "404" ]]; then
        echo "Authorization resource not found -- creating..."
    else
        echo "Unexpected status ${get_status} checking authorization resource:"
        pretty "$(http_body "${get_response}")"
        exit 1
    fi

    local auth_response auth_body auth_status
    auth_response="$(curl -s -w "\n%{http_code}" -X POST \
        -H "Authorization: Bearer ${access_token}" \
        -H "Content-Type: application/json" \
        -H "X-Goog-User-Project: ${project_id}" \
        -d "${auth_payload}" \
        "${auth_resource_url}?authorizationId=${auth_id}")"
    auth_status="$(http_status "${auth_response}")"
    auth_body="$(http_body "${auth_response}")"

    if [[ "${auth_status}" == "200" ]] || [[ "${auth_status}" == "201" ]]; then
        echo "  Authorization resource created (HTTP ${auth_status})."
    else
        echo "Failed to create authorization resource (HTTP ${auth_status}):"
        pretty "${auth_body}"
        exit 1
    fi

    # Wait for the new auth resource to propagate before registering the agent.
    if [[ "${agents_deleted}" == "true" ]]; then
        echo "  Waiting 5s for auth resource to propagate..."
        sleep 5
    fi
    echo ""

    # -----------------------------------------------------------------------
    # Step 3: Register agent with authorization_config
    # -----------------------------------------------------------------------
    echo "--- Step 3: Register agent with authorization_config ---"

    local auth_resource_name="projects/${project_number}/locations/global/authorizations/${auth_id}"

    local register_payload
    register_payload="$(printf '{
  "displayName": "%s",
  "description": "BigQuery analytics, data science, BQML, and conversational analytics via BQ Data Agents.",
  "adk_agent_definition": {
    "provisioned_reasoning_engine": {
      "reasoning_engine": "%s"
    }
  },
  "authorization_config": {
    "tool_authorizations": [
      "%s"
    ]
  }
}' \
        "${display_name}" \
        "${reasoning_engine}" \
        "${auth_resource_name}")"

    local register_response
    register_response="$(curl -s -X POST \
        -H "Authorization: Bearer ${access_token}" \
        -H "Content-Type: application/json" \
        -H "X-Goog-User-Project: ${project_id}" \
        -d "${register_payload}" \
        "${agents_url}")"

    echo "Response:"
    pretty "${register_response}"

    if echo "${register_response}" | grep -q '"name"'; then
        echo ""
        echo "Agent registered successfully with OAuth authorization."
        echo ""
        echo "Next steps:"
        echo "  1. Open Gemini Enterprise and start a conversation with the agent."
        echo "  2. When the agent attempts a BigQuery tool call, you should see an"
        echo "     OAuth consent prompt asking for BigQuery access."
        echo "  3. Authorize access and verify the agent can query your data."
        echo ""
        echo "View in console:"
        echo "  https://console.cloud.google.com/gemini-enterprise/engines?project=${project_id}"
    else
        echo ""
        echo "Registration may have failed -- check the response above."
        exit 1
    fi
}

main "$@"
