#!/bin/bash
#
# Deploy the BigQuery Multi-Agent App to Vertex AI Agent Engine.
#
# Uses the ADK CLI (adk deploy agent_engine) which deploys from source files,
# avoiding the deepcopy serialization issue with VertexAiCodeExecutor.
#
# Prerequisites:
#   - gcloud auth application-default login
#   - .env file in repo root with GOOGLE_CLOUD_PROJECT, AGENT_ENGINE_REGION,
#     GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET set
#
# Usage:
#   chmod +x deployment/deploy.sh
#   ./deployment/deploy.sh
#
# To update an existing deployment (pass the Agent Engine resource ID):
#   ./deployment/deploy.sh --agent_engine_id=RESOURCE_ID
#
# After deployment, copy the printed resource name to .env:
#   AGENT_ENGINE_RESOURCE_NAME=projects/.../locations/.../reasoningEngines/...
#   AGENT_ENGINE_ID=<numeric-id>

set -eo pipefail

# Resolve repo root and agent dir relative to this script.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
AGENT_DIR="${REPO_ROOT}/bq_multi_agent_app"
ENV_FILE="${REPO_ROOT}/.env"

main() {
    if [[ -f "${ENV_FILE}" ]]; then
        # shellcheck disable=SC1091
        source "${ENV_FILE}"
    fi

    local project="${GOOGLE_CLOUD_PROJECT:?GOOGLE_CLOUD_PROJECT is required in .env}"
    # Use AGENT_ENGINE_REGION for the deployment region (not GOOGLE_CLOUD_LOCATION,
    # which is set to "global" to route model calls to the Vertex AI global endpoint).
    # GOOGLE_CLOUD_AGENT_ENGINE_* vars are reserved by Agent Engine and cannot be
    # set via --env_file, so we use a plain AGENT_ENGINE_REGION var locally.
    local region="${AGENT_ENGINE_REGION:-us-central1}"

    echo "=== Deploying BigQuery Multi-Agent App to Agent Engine ==="
    echo "  Project : ${project}"
    echo "  Region  : ${region}"
    echo "  Agent   : ${AGENT_DIR}"
    echo ""

    # Pass through any extra arguments (e.g. --agent_engine_id for updates).
    uv run adk deploy agent_engine \
        --project="${project}" \
        --region="${region}" \
        --display_name="${AGENT_DISPLAY_NAME:-BigQuery Multi-Agent App}" \
        --otel_to_cloud \
        --env_file="${ENV_FILE}" \
        --agent_engine_config_file="${AGENT_DIR}/.agent_engine_config.json" \
        "$@" \
        "${AGENT_DIR}"

    echo ""
    echo "Deployment complete."
    echo "Copy AGENT_ENGINE_RESOURCE_NAME and AGENT_ENGINE_ID from the output above to .env."
}

main "$@"
