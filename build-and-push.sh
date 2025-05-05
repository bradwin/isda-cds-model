#!/bin/bash
# build-and-push.sh
# Script to build and push multi-architecture Docker images for ISDA CDS API

# Define variables
IMAGE_NAME="isda-cds-api"
IMAGE_TAG="latest"
DOCKER_HUB_USERNAME="bradwin"  # Replace with your Docker Hub username

# Build for multiple platforms
echo "Building multi-architecture Docker image..."
docker buildx create --name isda-builder --use || true
docker buildx inspect --bootstrap

# Build and push the multi-architecture image
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG} \
  --push \
  .

echo "Build and push completed successfully!"
echo ""
echo "To pull and run the image on a Linux/amd64 system, use:"
echo "docker pull ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"
echo "docker run -p 8000:8000 ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"