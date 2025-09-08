# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Download and install MCP toolbox
RUN curl -O https://storage.googleapis.com/genai-toolbox/v0.14.0/linux/amd64/toolbox && \
    chmod +x toolbox

# Expose port (Cloud Run will set PORT environment variable)
EXPOSE 8080

# Set environment variables (will be overridden by Cloud Run deployment)
ENV BIGQUERY_PROJECT=""
ENV PORT=8080

# Start toolbox directly using PORT environment variable
CMD sh -c "./toolbox --prebuilt bigquery --address=0.0.0.0 --port=${PORT:-8080}"
