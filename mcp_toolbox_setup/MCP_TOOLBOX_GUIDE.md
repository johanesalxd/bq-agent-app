# MCP Toolbox Cloud Run Deployment Guide

This guide explains how to deploy the MCP (Model Context Protocol) BigQuery toolbox to Google Cloud Run for use with Vertex AI Agent Engine and local development.

## Overview

The MCP toolbox provides BigQuery database operations through a standardized protocol that can be consumed by AI agents. This deployment creates a Cloud Run service that can be accessed from both local development environments and cloud-based AI agents.

## Prerequisites

- Google Cloud Project with billing enabled
- Google Cloud CLI (`gcloud`) installed and authenticated
- Docker installed (for local testing)
- BigQuery API enabled in your project
- Cloud Run API enabled in your project

## Quick Start

1. **Setup ENV variables**
   ```bash
   source .env
   export BIGQUERY_PROJECT=$BIGQUERY_PROJECT
   ```

2. **Install the MCP toolbox locally:**
   ```bash
   cd mcp_toolbox_setup
   chmod +x install-mcp-toolbox.sh
   ./install-mcp-toolbox.sh
   ```

3. **Deploy to Cloud Run:**
   ```bash
   cd mcp_toolbox_setup
   chmod +x deploy.sh
   ./deploy.sh
   ```

4. **Update your application configuration:**
   - Update the `TOOLBOX_URL` in your application's `.env.cloud` file to point to your deployed Cloud Run service
   - Ensure your application loads environment variables using `python-dotenv`

## File Structure

```
mcp_toolbox_setup/
├── MCP_TOOLBOX_GUIDE.md          # This guide
├── install-mcp-toolbox.sh        # Local toolbox installation script
├── Dockerfile                    # Container definition for Cloud Run
├── deploy.sh                     # Automated deployment script
└── .dockerignore                 # Docker build exclusions
```

## Deployment Details

### Container Configuration

The deployment uses a simplified single-process container that runs only the MCP toolbox:

- **Base Image:** `python:3.11-slim`
- **Port:** 5000
- **Command:** `./toolbox --prebuilt bigquery --address=0.0.0.0 --port=5000`
- **Authentication:** `allow-authenticated` (requires Google Cloud authentication)

### Cloud Run Service

- **Service Name:** `mcp-toolbox-bq`
- **Region:** `us-central1` (configurable)
- **CPU:** 1 vCPU
- **Memory:** 2Gi
- **Concurrency:** 80 requests per instance
- **Min Instances:** 0 (scales to zero when not in use)
- **Max Instances:** 10

### IAM and Permissions

The deployment script automatically:

1. Creates a service account: `mcp-toolbox-identity@{PROJECT_ID}.iam.gserviceaccount.com`
2. Grants BigQuery permissions:
   - `roles/bigquery.dataViewer`
   - `roles/bigquery.jobUser`
3. Assigns the service account to the Cloud Run service

## Troubleshooting

### Logs and Monitoring

```bash
# View Cloud Run logs
gcloud logs read --service=mcp-toolbox-bq --region=us-central1

# Stream real-time logs
gcloud logs tail --service=mcp-toolbox-bq --region=us-central1
```

## Security Considerations

- The service uses `allow-authenticated` which requires valid Google Cloud authentication
- Service account has minimal BigQuery permissions (read-only data access and job execution)
- No public internet access - requires authentication for all requests
- Container runs as non-root user for security

## Cost Optimization

- Service scales to zero when not in use (no cost during idle periods)
- CPU and memory are right-sized for typical BigQuery operations
- Consider setting up budget alerts for monitoring costs

## Advanced Configuration

### Custom Regions

To deploy to a different region, modify the `deploy.sh` script:

```bash
REGION="europe-west1"  # Change this line
```

### Resource Limits

To adjust CPU/memory, modify the deployment command in `deploy.sh`:

```bash
--cpu=2 \
--memory=4Gi \
```

### Custom Service Account

To use an existing service account, modify the `deploy.sh` script to skip service account creation and use your existing one.

## Integration with Vertex AI Agent Engine

Once deployed, the Cloud Run service URL can be used in Vertex AI Agent Engine configurations to provide BigQuery capabilities to your AI agents. The service will automatically handle authentication and provide secure access to your BigQuery data.

## Support

For issues related to:
- **MCP Toolbox:** Check the [GenAI Toolbox documentation](https://googleapis.github.io/genai-toolbox/)
- **Cloud Run:** Check the [Cloud Run documentation](https://cloud.google.com/run/docs)
- **BigQuery:** Check the [BigQuery documentation](https://cloud.google.com/bigquery/docs)
