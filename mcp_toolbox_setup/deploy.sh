#!/bin/bash
set -e

# Load environment variables if .env file exists
if [ -f "../.env" ]; then
    echo "Loading environment from ../.env"
    export $(grep -v '^#' ../.env | xargs)
fi

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT}
REGION=${GOOGLE_CLOUD_LOCATION:-us-central1}
SERVICE_NAME="mcp-toolbox-bq"
REPOSITORY_NAME="mcp-toolbox"
IMAGE_NAME="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/${SERVICE_NAME}"
SERVICE_ACCOUNT="mcp-toolbox-identity"

# Check project ID
if [ -z "$PROJECT_ID" ]; then
    echo "Error: GOOGLE_CLOUD_PROJECT environment variable is not set"
    exit 1
fi

echo "Deploying MCP Toolbox to Cloud Run"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable run.googleapis.com \
                       cloudbuild.googleapis.com \
                       artifactregistry.googleapis.com \
                       iam.googleapis.com \
                       --project=$PROJECT_ID

# Create service account if needed
echo "Setting up service account..."
if ! gcloud iam service-accounts describe ${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com --project=$PROJECT_ID >/dev/null 2>&1; then
    gcloud iam service-accounts create $SERVICE_ACCOUNT \
        --display-name="BigQuery Agent Identity" \
        --project=$PROJECT_ID
fi

# Grant BigQuery permissions
echo "Granting BigQuery permissions..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member serviceAccount:${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com \
    --role roles/bigquery.user

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member serviceAccount:${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com \
    --role roles/bigquery.dataViewer

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member serviceAccount:${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com \
    --role roles/bigquery.jobUser

# Create Artifact Registry repository if needed
echo "Setting up Artifact Registry repository..."
if ! gcloud artifacts repositories describe $REPOSITORY_NAME --location=$REGION --project=$PROJECT_ID >/dev/null 2>&1; then
    gcloud artifacts repositories create $REPOSITORY_NAME \
        --repository-format=docker \
        --location=$REGION \
        --description="MCP Toolbox container images" \
        --project=$PROJECT_ID
fi

# Configure Docker authentication for Artifact Registry
echo "Configuring Docker authentication..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

# Build and push Docker image
echo "Building Docker image for linux/amd64 platform..."
docker build --platform linux/amd64 -t $IMAGE_NAME .

echo "Pushing to Artifact Registry..."
docker push $IMAGE_NAME

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --service-account ${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com \
    --region $REGION \
    --allow-unauthenticated \
    --memory 4Gi \
    --cpu 2 \
    --timeout 3600 \
    --max-instances 2 \
    --set-env-vars BIGQUERY_PROJECT=$PROJECT_ID \
    --project=$PROJECT_ID

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)

echo ""
echo "Deployment completed!"
echo "Service URL: $SERVICE_URL"
echo ""
echo "To delete the service:"
echo "  gcloud run services delete $SERVICE_NAME --region=$REGION --project=$PROJECT_ID"
