# MCP Toolbox Deployment Guide

This guide explains how to deploy the MCP (Model Context Protocol) BigQuery toolbox for use with Vertex AI Agent Engine and local development. The toolbox provides BigQuery database operations through a standardized protocol that can be consumed by AI agents.

You can run the MCP Toolbox either locally or deploy it as a service on Google Cloud Run.

## Prerequisites

- Google Cloud Project with billing enabled
- Google Cloud CLI (`gcloud`) installed and authenticated
- Docker installed
- BigQuery API enabled in your project
- Cloud Run API enabled in your project (for Cloud Run deployment)

## Local Deployment

Running the toolbox locally is ideal for development and testing.

1.  **Install the MCP toolbox:**
    If you haven't already, install the toolbox binary.
    ```bash
    cd setup/mcp_toolbox
    chmod +x install-mcp-toolbox.sh
    ./install-mcp-toolbox.sh
    ```

2.  **Set Environment Variables:**
    Ensure your `BIGQUERY_PROJECT` is set. The application will read it from your `.env` file.
    ```bash
    # Make sure you are in the root directory of the project
    export $(cat ../../.env | grep -v '^#' | xargs)
    ```

3.  **Run the Toolbox Server:**
    Start the server, pointing it to your custom `tools.yaml` configuration.
    ```bash
    cd setup/mcp_toolbox
    ./toolbox --tools-file=tools.yaml --port=5000
    ```
    The toolbox will now be running at `http://127.0.0.1:5000`.

## Cloud Run Deployment

Deploying to Cloud Run provides a scalable, managed service that can be accessed from both local environments and cloud-based AI agents.

### Quick Start

1.  **Set Environment Variables:**
    The deployment script will load variables from the `.env` file in the root directory.
    ```bash
    # Make sure you are in the root directory of the project
    export $(cat .env | grep -v '^#' | xargs)
    ```

2.  **Deploy to Cloud Run:**
    Run the automated deployment script.
    ```bash
    cd setup/mcp_toolbox
    chmod +x deploy.sh
    ./deploy.sh
    ```

3.  **Update Application Configuration:**
    - After deployment, the script will output a **Service URL**.
    - Update the `TOOLBOX_URL` in your project's `.env` file to point to this new URL.

### Deployment Details

#### Container Configuration

The deployment uses a Docker container to run the MCP toolbox.

-   **Base Image:** `python:3.11-slim`
-   **Port:** The container exposes port `8080`, which is the default for Cloud Run.
-   **Command:** The `Dockerfile` uses the following command to start the server, which correctly uses the `tools.yaml` configuration file:
    ```
    CMD ["sh", "-c", "./toolbox --tools-file=tools.yaml --address=0.0.0.0 --port=${PORT:-8080}"]
    ```

#### Cloud Run Service

-   **Service Name:** `mcp-toolbox-bq`
-   **Region:** `us-central1` (configurable in `deploy.sh`)
-   **Authentication:** The service is deployed with `--allow-unauthenticated`, but your tools can be configured to require authentication.

#### IAM and Permissions

The `deploy.sh` script automatically handles the necessary permissions:

1.  **Creates a service account:** `mcp-toolbox-identity@{PROJECT_ID}.iam.gserviceaccount.com`
2.  **Grants BigQuery permissions:** `roles/bigquery.user`, `roles/bigquery.dataViewer`, and `roles/bigquery.jobUser`.
3.  **Assigns the service account** to the Cloud Run service.

### Troubleshooting

You can view logs for your deployed service to diagnose any issues.

```bash
# View Cloud Run logs
gcloud logs read --service=mcp-toolbox-bq --region=$REGION --project=$PROJECT_ID

# Stream real-time logs
gcloud logs tail --service=mcp-toolbox-bq --region=$REGION --project=$PROJECT_ID
```

### Security Considerations

- The service account is granted minimal necessary permissions for BigQuery operations.
- Review the `tools.yaml` file to understand what operations are exposed.
- For production, consider restricting access further by removing `--allow-unauthenticated` and implementing stricter IAM policies.

## Support

For issues related to:
- **MCP Toolbox:** Check the [GenAI Toolbox documentation](https://googleapis.github.io/genai-toolbox/)
- **Cloud Run:** Check the [Cloud Run documentation](https://cloud.google.com/run/docs)
- **BigQuery:** Check the [BigQuery documentation](https://cloud.google.com/bigquery/docs)
