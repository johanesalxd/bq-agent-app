#!/bin/bash

# AgentSpace Management Script
# This script provides functions to list, delete, and deploy agents in Google Cloud AgentSpace

set -e

# Configuration - Update these values with your actual project details
export PROJECT_ID="your-project-id" # String
export PROJECT_NUMBER="your-project-number" # String

export REASONING_ENGINE_ID="your-reasoning-engine-id" # String - Normally a 18-digit number
export REASONING_ENGINE_LOCATION="us-central1" # String - e.g. us-central1
export REASONING_ENGINE="projects/${PROJECT_ID}/locations/${REASONING_ENGINE_LOCATION}/reasoningEngines/${REASONING_ENGINE_ID}"

export AS_APP="your-agentspace-name" # String - Find it in Google Cloud AI Applications
export AS_LOCATION="global" # String - e.g. global, eu, us

export AGENT_DISPLAY_NAME="bq-agent-app" # String - this will appear as the name of the agent into your AgentSpace
AGENT_DESCRIPTION=$(cat <<EOF
This multi-agent system queries BigQuery for data, passes it to a data science agent for analysis, and returns insights and visualizations.
EOF
)
export AGENT_DESCRIPTION

DISCOVERY_ENGINE_PROD_API_ENDPOINT="https://discoveryengine.googleapis.com"
BASE_URL="${DISCOVERY_ENGINE_PROD_API_ENDPOINT}/v1alpha/projects/${PROJECT_NUMBER}/locations/${AS_LOCATION}/collections/default_collection/engines/${AS_APP}/assistants/default_assistant"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if required environment variables are set
check_config() {
    local missing_vars=()

    if [[ "$PROJECT_ID" == "your-project-id" ]]; then
        missing_vars+=("PROJECT_ID")
    fi

    if [[ "$PROJECT_NUMBER" == "your-project-number" ]]; then
        missing_vars+=("PROJECT_NUMBER")
    fi

    if [[ "$REASONING_ENGINE_ID" == "your-reasoning-engine-id" ]]; then
        missing_vars+=("REASONING_ENGINE_ID")
    fi

    if [[ "$AS_APP" == "your-agentspace-id" ]]; then
        missing_vars+=("AS_APP")
    fi

    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_error "Please update the following configuration variables in this script:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        exit 1
    fi
}

# Function to list all agents in the AgentSpace
list_agents() {
    log_info "Listing agents in AgentSpace..."

    local response=$(curl -s -X GET \
        -H "Authorization: Bearer $(gcloud auth print-access-token)" \
        -H "Content-Type: application/json" \
        -H "x-goog-user-project: ${PROJECT_ID}" \
        "${BASE_URL}/agents")

    if [[ $? -ne 0 ]]; then
        log_error "Failed to list agents"
        return 1
    fi

    echo "$response" | jq -r '.agents[]? | "Name: \(.name)\nDisplay Name: \(.displayName)\nDescription: \(.description)\n---"' 2>/dev/null || {
        log_warning "jq not found. Raw response:"
        echo "$response"
    }

    echo "$response"
}

# Function to find agent by display name
find_agent_by_display_name() {
    local display_name="$1"
    log_info "Looking for agent with display name: $display_name" >&2

    local response=$(curl -s -X GET \
        -H "Authorization: Bearer $(gcloud auth print-access-token)" \
        -H "Content-Type: application/json" \
        -H "x-goog-user-project: ${PROJECT_ID}" \
        "${BASE_URL}/agents")

    if [[ $? -ne 0 ]]; then
        log_error "Failed to list agents" >&2
        return 1
    fi

    # Extract agent name using jq if available, otherwise use grep/sed
    if command -v jq >/dev/null 2>&1; then
        echo "$response" | jq -r ".agents[]? | select(.displayName == \"$display_name\") | .name"
    else
        # Fallback method without jq
        echo "$response" | grep -o '"name":"[^"]*"' | grep -A1 "\"displayName\":\"$display_name\"" | head -1 | sed 's/"name":"//;s/"//'
    fi
}

# Function to delete an agent by its full name
delete_agent() {
    local agent_name="$1"

    if [[ -z "$agent_name" ]]; then
        log_error "Agent name is required for deletion"
        return 1
    fi

    log_info "Deleting agent: $agent_name"

    local response=$(curl -s -X DELETE \
        -H "Authorization: Bearer $(gcloud auth print-access-token)" \
        -H "Content-Type: application/json" \
        -H "x-goog-user-project: ${PROJECT_ID}" \
        "${DISCOVERY_ENGINE_PROD_API_ENDPOINT}/v1alpha/${agent_name}")

    if [[ $? -eq 0 ]]; then
        log_success "Agent deleted successfully"
        return 0
    else
        log_error "Failed to delete agent"
        echo "$response"
        return 1
    fi
}

# Function to deploy agent to AgentSpace
deploy_agent() {
    log_info "Deploying agent '$AGENT_DISPLAY_NAME' to AgentSpace..."

    local response=$(curl -s -X POST \
        -H "Authorization: Bearer $(gcloud auth print-access-token)" \
        -H "Content-Type: application/json" \
        -H "x-goog-user-project: ${PROJECT_ID}" \
        "${BASE_URL}/agents" \
        -d '{
      "displayName": "'"${AGENT_DISPLAY_NAME}"'",
      "description": "'"${AGENT_DESCRIPTION}"'",
      "icon": {
        "uri": "https://fonts.gstatic.com/s/i/short-term/release/googlesymbols/corporate_fare/default/24px.svg"
      },
      "adk_agent_definition": {
        "tool_settings": {
          "toolDescription": "'"${AGENT_DESCRIPTION}"'"
        },
        "provisioned_reasoning_engine": {
          "reasoningEngine": "'"${REASONING_ENGINE}"'"
        }
      }
    }')

    if [[ $? -eq 0 ]]; then
        log_success "Agent deployed successfully"
        echo "$response"
        return 0
    else
        log_error "Failed to deploy agent"
        echo "$response"
        return 1
    fi
}

# Function to replace existing agent (delete old, deploy new)
replace_agent() {
    log_info "Starting agent replacement process..."

    # Find existing agent
    local existing_agent=$(find_agent_by_display_name "$AGENT_DISPLAY_NAME")

    if [[ -n "$existing_agent" ]]; then
        log_info "Found existing agent: $existing_agent"

        # Delete existing agent
        if delete_agent "$existing_agent"; then
            log_success "Existing agent deleted"

            # Wait a moment for the deletion to propagate
            log_info "Waiting 5 seconds for deletion to propagate..."
            sleep 5
        else
            log_error "Failed to delete existing agent"
            return 1
        fi
    else
        log_info "No existing agent found with display name '$AGENT_DISPLAY_NAME'"
    fi

    # Deploy new agent
    if deploy_agent; then
        log_success "Agent replacement completed successfully!"
        return 0
    else
        log_error "Failed to deploy new agent"
        return 1
    fi
}

# Function to list ReasoningEngine sessions
list_reasoning_engine_sessions() {
    log_info "Listing sessions for ReasoningEngine $REASONING_ENGINE_ID..."

    local response=$(curl -s -X GET \
        -H "Authorization: Bearer $(gcloud auth print-access-token)" \
        -H "Content-Type: application/json" \
        "https://${REASONING_ENGINE_LOCATION}-aiplatform.googleapis.com/v1beta1/projects/${PROJECT_ID}/locations/${REASONING_ENGINE_LOCATION}/reasoningEngines/${REASONING_ENGINE_ID}/sessions")

    if [[ $? -ne 0 ]]; then
        log_error "Failed to list ReasoningEngine sessions"
        return 1
    fi

    echo "$response" | jq -r '.sessions[]? | "Session ID: \(.name | split("/")[-1])\nName: \(.name)\n---"' 2>/dev/null || {
        log_warning "jq not found. Raw response:"
        echo "$response"
    }

    echo "$response"
}

# Function to delete a specific ReasoningEngine session
delete_reasoning_engine_session() {
    local session_id="$1"

    if [[ -z "$session_id" ]]; then
        log_error "Session ID is required for deletion"
        return 1
    fi

    log_info "Deleting ReasoningEngine session: $session_id"

    local response=$(curl -s -X DELETE \
        -H "Authorization: Bearer $(gcloud auth print-access-token)" \
        -H "Content-Type: application/json" \
        "https://${REASONING_ENGINE_LOCATION}-aiplatform.googleapis.com/v1beta1/projects/${PROJECT_ID}/locations/${REASONING_ENGINE_LOCATION}/reasoningEngines/${REASONING_ENGINE_ID}/sessions/${session_id}")

    if [[ $? -eq 0 ]]; then
        log_success "Session $session_id deleted successfully"
        return 0
    else
        log_error "Failed to delete session $session_id"
        echo "$response"
        return 1
    fi
}

# Function to delete all ReasoningEngine sessions
delete_all_reasoning_engine_sessions() {
    log_info "Deleting all sessions for ReasoningEngine $REASONING_ENGINE_ID..."

    local response=$(curl -s -X GET \
        -H "Authorization: Bearer $(gcloud auth print-access-token)" \
        -H "Content-Type: application/json" \
        "https://${REASONING_ENGINE_LOCATION}-aiplatform.googleapis.com/v1beta1/projects/${PROJECT_ID}/locations/${REASONING_ENGINE_LOCATION}/reasoningEngines/${REASONING_ENGINE_ID}/sessions")

    if [[ $? -ne 0 ]]; then
        log_error "Failed to list ReasoningEngine sessions"
        return 1
    fi

    # Extract session IDs using jq if available
    local session_ids
    if command -v jq >/dev/null 2>&1; then
        session_ids=$(echo "$response" | jq -r '.sessions[]?.name | split("/")[-1]' 2>/dev/null)
    else
        # Fallback method without jq
        session_ids=$(echo "$response" | grep -o '"name":"[^"]*"' | sed 's/"name":"//;s/"//' | sed 's/.*\///')
    fi

    if [[ -z "$session_ids" ]]; then
        log_info "No sessions found to delete"
        return 0
    fi

    local session_count=$(echo "$session_ids" | wc -l)
    log_info "Found $session_count session(s) to delete"

    # Delete each session
    local failed_count=0
    while IFS= read -r session_id; do
        if [[ -n "$session_id" ]]; then
            if ! delete_reasoning_engine_session "$session_id"; then
                ((failed_count++))
            fi
        fi
    done <<< "$session_ids"

    if [[ $failed_count -eq 0 ]]; then
        log_success "All sessions deleted successfully"
        return 0
    else
        log_warning "$failed_count session(s) failed to delete"
        return 1
    fi
}

# Function to delete ReasoningEngine
delete_reasoning_engine() {
    local force_flag="$1"
    local dry_run="$2"

    if [[ "$dry_run" == "true" ]]; then
        log_info "🔍 DRY RUN MODE - No actual deletions"
    fi

    if [[ "$force_flag" == "true" ]]; then
        log_info "Force deleting ReasoningEngine $REASONING_ENGINE_ID..."

        if [[ "$dry_run" == "true" ]]; then
            log_info "[DRY RUN] Would force delete ReasoningEngine $REASONING_ENGINE_ID"
            return 0
        fi

        local response=$(curl -s -X DELETE \
            -H "Authorization: Bearer $(gcloud auth print-access-token)" \
            -H "Content-Type: application/json" \
            "https://${REASONING_ENGINE_LOCATION}-aiplatform.googleapis.com/v1beta1/projects/${PROJECT_ID}/locations/${REASONING_ENGINE_LOCATION}/reasoningEngines/${REASONING_ENGINE_ID}?force=true")

        if [[ $? -eq 0 ]]; then
            log_success "ReasoningEngine and all child resources deleted successfully!"
            return 0
        else
            log_error "Failed to delete ReasoningEngine"
            echo "$response"
            return 1
        fi
    else
        log_info "Using step-by-step deletion approach..."

        if [[ "$dry_run" == "true" ]]; then
            log_info "[DRY RUN] Would delete all sessions first, then ReasoningEngine"
            list_reasoning_engine_sessions
            return 0
        fi

        # Delete all sessions first
        if delete_all_reasoning_engine_sessions; then
            log_info "All sessions deleted. Now deleting ReasoningEngine..."
        else
            log_warning "Some sessions failed to delete. Continuing with ReasoningEngine deletion..."
        fi

        # Delete the ReasoningEngine
        local response=$(curl -s -X DELETE \
            -H "Authorization: Bearer $(gcloud auth print-access-token)" \
            -H "Content-Type: application/json" \
            "https://${REASONING_ENGINE_LOCATION}-aiplatform.googleapis.com/v1beta1/projects/${PROJECT_ID}/locations/${REASONING_ENGINE_LOCATION}/reasoningEngines/${REASONING_ENGINE_ID}")

        if [[ $? -eq 0 ]]; then
            log_success "ReasoningEngine deleted successfully!"
            return 0
        else
            log_error "Failed to delete ReasoningEngine"
            echo "$response"
            return 1
        fi
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  list                    - List all agents in the AgentSpace"
    echo "  deploy                  - Deploy a new agent to AgentSpace"
    echo "  delete                  - Delete agent by display name"
    echo "  replace                 - Replace existing agent (delete + deploy)"
    echo "  delete-reasoning-engine - Delete ReasoningEngine and its sessions"
    echo "  list-sessions          - List all ReasoningEngine sessions"
    echo "  delete-sessions        - Delete all ReasoningEngine sessions"
    echo "  help                   - Show this help message"
    echo ""
    echo "Options for delete-reasoning-engine:"
    echo "  --force                - Force delete ReasoningEngine and all child resources"
    echo "  --dry-run              - Show what would be deleted without actually deleting"
    echo ""
    echo "Examples:"
    echo "  $0 list"
    echo "  $0 deploy"
    echo "  $0 delete"
    echo "  $0 replace"
    echo "  $0 delete-reasoning-engine"
    echo "  $0 delete-reasoning-engine --force"
    echo "  $0 delete-reasoning-engine --dry-run"
    echo "  $0 list-sessions"
    echo "  $0 delete-sessions"
}

# Main execution
main() {
    local command="${1:-replace}"
    local force_flag="false"
    local dry_run="false"

    # Parse options for delete-reasoning-engine command
    if [[ "$command" == "delete-reasoning-engine" ]]; then
        shift # Remove the command from arguments
        while [[ $# -gt 0 ]]; do
            case $1 in
                --force)
                    force_flag="true"
                    shift
                    ;;
                --dry-run)
                    dry_run="true"
                    shift
                    ;;
                *)
                    log_error "Unknown option: $1"
                    show_usage
                    exit 1
                    ;;
            esac
        done
    fi

    case "$command" in
        "list")
            check_config
            list_agents
            ;;
        "deploy")
            check_config
            deploy_agent
            ;;
        "delete")
            check_config
            local agent_name=$(find_agent_by_display_name "$AGENT_DISPLAY_NAME")
            if [[ -n "$agent_name" ]]; then
                delete_agent "$agent_name"
            else
                log_warning "No agent found with display name '$AGENT_DISPLAY_NAME'"
            fi
            ;;
        "replace")
            check_config
            replace_agent
            ;;
        "delete-reasoning-engine")
            check_config
            delete_reasoning_engine "$force_flag" "$dry_run"
            ;;
        "list-sessions")
            check_config
            list_reasoning_engine_sessions
            ;;
        "delete-sessions")
            check_config
            delete_all_reasoning_engine_sessions
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            log_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
