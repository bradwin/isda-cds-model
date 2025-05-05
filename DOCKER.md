# Docker Usage Guide

## Docker Architecture Issues

If you encounter the error `no matching manifest for linux/amd64 in the manifest list entries` when pulling the Docker image, it's because the image was built for a different architecture. This is common when building on Apple Silicon (M1/M2) machines and trying to run on standard Linux servers.

## Building Docker Images for Multiple Architectures

### Option 1: Using the build script (Recommended)

1. Make the build script executable:
   ```bash
   chmod +x build-and-push.sh
   ```

2. Edit the `build-and-push.sh` script to update your Docker Hub username.

3. Run the build script:
   ```bash
   ./build-and-push.sh
   ```

This script uses Docker's BuildX feature to build images for both `linux/amd64` (standard Linux) and `linux/arm64` (ARM-based systems like Apple Silicon) architectures.

### Option 2: Building manually

If you prefer to build manually, use this command to build for multiple architectures:

```bash
# Create a buildx builder if you don't have one already
docker buildx create --name multi-platform-builder --use

# Build the image for multiple platforms
docker buildx build --platform linux/amd64,linux/arm64 -t yourusername/isda-cds-api:latest --push .
```

### Option 3: Building for a specific platform only

To build only for the linux/amd64 platform:

```bash
docker build --platform=linux/amd64 -t isda-cds-api:latest .
```

## Running the Docker Image

```bash
# Pull the image (if using a remote registry)
docker pull yourusername/isda-cds-api:latest

# Run the container
docker run -p 8000:8000 yourusername/isda-cds-api:latest
```

## Running Without Docker Hub

If you want to run the image locally without pushing to Docker Hub:

```bash
# Build with load option (only works for single architecture)
docker buildx build --platform=linux/amd64 -t isda-cds-api:latest --load .

# Run the container
docker run -p 8000:8000 isda-cds-api:latest
```

## Accessing the API

Once the container is running, access the API at:
- API endpoints: http://localhost:8000/api/
- Swagger UI documentation: http://localhost:8000/docs