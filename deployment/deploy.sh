#!/bin/bash
#
# Deploy the BigQuery Multi-Agent App to Vertex AI Agent Engine.
#
# Uses the ADK CLI (adk deploy agent_engine) which deploys from source files,
# avoiding the deepcopy serialization issue with VertexAiCodeExecutor.
# Each run always creates a new Agent Engine instance.
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
# Deploy and automatically delete the previous engine + update .env:
#   ./deployment/deploy.sh --cleanup
#
# After deployment without --cleanup, copy the printed resource name to .env:
#   AGENT_ENGINE_RESOURCE_NAME=projects/.../locations/.../reasoningEngines/...
#   AGENT_ENGINE_ID=<numeric-id>

set -eo pipefail

# Resolve repo root and agent dir relative to this script.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
AGENT_DIR="${REPO_ROOT}/bq_multi_agent_app"
ENV_FILE="${REPO_ROOT}/.env"

# ---------------------------------------------------------------------------
# Parse --cleanup flag out of args before forwarding to adk deploy.
# ---------------------------------------------------------------------------

do_cleanup=0
passthrough_args=()
for arg in "$@"; do
    if [[ "${arg}" == "--cleanup" ]]; then
        do_cleanup=1
    else
        passthrough_args+=("${arg}")
    fi
done

main() {
    if [[ -f "${ENV_FILE}" ]]; then
        # shellcheck disable=SC1091
        source "${ENV_FILE}"
    fi

    local project="${GOOGLE_CLOUD_PROJECT:?GOOGLE_CLOUD_PROJECT is required in .env}"
    local project_number="${GOOGLE_CLOUD_PROJECT_NUMBER:?GOOGLE_CLOUD_PROJECT_NUMBER is required in .env}"
    # Use AGENT_ENGINE_REGION for the deployment region (not GOOGLE_CLOUD_LOCATION,
    # which is set to "global" to route model calls to the Vertex AI global endpoint).
    local region="${AGENT_ENGINE_REGION:-us-central1}"

    # Capture the old engine ID before deploying (used by --cleanup).
    local old_engine_id="${AGENT_ENGINE_ID:-}"

    echo "=== Deploying BigQuery Multi-Agent App to Agent Engine ==="
    echo "  Project : ${project}"
    echo "  Region  : ${region}"
    echo "  Agent   : ${AGENT_DIR}"
    if [[ "${do_cleanup}" -eq 1 ]]; then
        if [[ -n "${old_engine_id}" ]]; then
            echo "  Cleanup : will delete old engine ${old_engine_id} after deploy"
        else
            echo "  Cleanup : no previous engine ID in .env, skipping deletion"
        fi
    fi
    echo ""

    # Run adk deploy and capture stdout so we can parse the new engine ID.
    local deploy_output
    deploy_output=$(uv run adk deploy agent_engine \
        --project="${project}" \
        --region="${region}" \
        --display_name="${AGENT_DISPLAY_NAME:-BigQuery Multi-Agent App}" \
        --otel_to_cloud \
        --env_file="${ENV_FILE}" \
        --agent_engine_config_file="${AGENT_DIR}/.agent_engine_config.json" \
        "${passthrough_args[@]}" \
        "${AGENT_DIR}" 2>&1)

    # Always print the deploy output so the user sees it.
    echo "${deploy_output}"

    # Parse the new engine resource name from the adk deploy output.
    # Expected line: ✅ Created agent engine: projects/.../reasoningEngines/ID
    local new_resource_name
    new_resource_name=$(echo "${deploy_output}" | grep -o 'projects/[^ ]*reasoningEngines/[0-9]*' | head -1)

    if [[ -z "${new_resource_name}" ]]; then
        echo ""
        echo "ERROR: Could not parse new engine resource name from deploy output." >&2
        echo "       Deploy may have failed, or output format changed." >&2
        exit 1
    fi

    local new_engine_id
    new_engine_id=$(echo "${new_resource_name}" | grep -o '[0-9]*$')

    echo ""

    if [[ "${do_cleanup}" -eq 1 ]]; then
        # --- Update .env with new engine IDs ---
        echo "Updating .env with new engine IDs..."
        sed -i.bak \
            -e "s|^AGENT_ENGINE_RESOURCE_NAME=.*|AGENT_ENGINE_RESOURCE_NAME=${new_resource_name}|" \
            -e "s|^AGENT_ENGINE_ID=.*|AGENT_ENGINE_ID=${new_engine_id}|" \
            "${ENV_FILE}"
        rm -f "${ENV_FILE}.bak"
        echo "  AGENT_ENGINE_RESOURCE_NAME=${new_resource_name}"
        echo "  AGENT_ENGINE_ID=${new_engine_id}"

        # --- Delete old engine ---
        if [[ -z "${old_engine_id}" ]]; then
            echo "  No previous engine ID found in .env -- skipping deletion."
        elif [[ "${old_engine_id}" == "${new_engine_id}" ]]; then
            echo "  Old engine ID matches new engine ID -- skipping deletion."
        else
            echo ""
            echo "Deleting old engine ${old_engine_id}..."
            local old_resource="projects/${project_number}/locations/${region}/reasoningEngines/${old_engine_id}"
            local access_token
            access_token=$(gcloud auth print-access-token)
            local delete_status
            delete_status=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE \
                -H "Authorization: Bearer ${access_token}" \
                "https://${region}-aiplatform.googleapis.com/v1beta1/${old_resource}")

            if [[ "${delete_status}" == "200" || "${delete_status}" == "204" ]]; then
                echo "  Deleted engine ${old_engine_id} (HTTP ${delete_status})."
            elif [[ "${delete_status}" == "404" ]]; then
                echo "  Engine ${old_engine_id} not found (already deleted?)."
            else
                echo "  WARNING: Delete returned HTTP ${delete_status}. Engine may still exist." >&2
                echo "  You can delete it manually:" >&2
                echo "    gcloud ai reasoning-engines delete ${old_engine_id} --location=${region}" >&2
            fi
        fi

        echo ""
        echo "Deployment complete."
        echo "  New engine : ${new_resource_name}"
        echo "  .env       : updated automatically"
        echo ""
        echo "Next step: run ./deployment/register_gemini_enterprise.sh"
    else
        echo "Deployment complete."
        echo "Copy AGENT_ENGINE_RESOURCE_NAME and AGENT_ENGINE_ID from the output above to .env."
    fi
}

main
