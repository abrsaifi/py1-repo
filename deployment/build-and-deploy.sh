#!/bin/bash
# Docker Build and Deploy Script
# Builds and pushes images to registry

set -e

# Configuration
REGISTRY="${REGISTRY:-docker.io}"
USERNAME="${DOCKER_USERNAME}"
PASSWORD="${DOCKER_PASSWORD}"
IMAGE_NAME="${IMAGE_NAME:-converter}"
VERSION="${VERSION:-latest}"
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

if [ -z "$USERNAME" ] || [ -z "$PASSWORD" ]; then
    echo "ERROR: DOCKER_USERNAME and DOCKER_PASSWORD must be set"
    exit 1
fi

echo "=========================================="
echo "Building and Deploying Docker Images"
echo "=========================================="
echo "Registry: $REGISTRY"
echo "Image: $IMAGE_NAME"
echo "Version: $VERSION"
echo "Build date: $BUILD_DATE"
echo "Git commit: $GIT_COMMIT"
echo ""

# Login to registry
echo "Logging in to Docker registry..."
echo "$PASSWORD" | docker login -u "$USERNAME" --password-stdin "$REGISTRY" || exit 1

# Build backend image
echo "Building backend image..."
docker build \
    -t "$REGISTRY/$USERNAME/$IMAGE_NAME-backend:$VERSION" \
    -t "$REGISTRY/$USERNAME/$IMAGE_NAME-backend:latest" \
    --build-arg BUILD_DATE="$BUILD_DATE" \
    --build-arg GIT_COMMIT="$GIT_COMMIT" \
    --label "org.opencontainers.image.created=$BUILD_DATE" \
    --label "org.opencontainers.image.revision=$GIT_COMMIT" \
    -f Dockerfile .

# Build frontend image
echo "Building frontend image..."
docker build \
    -t "$REGISTRY/$USERNAME/$IMAGE_NAME-frontend:$VERSION" \
    -t "$REGISTRY/$USERNAME/$IMAGE_NAME-frontend:latest" \
    --build-arg BUILD_DATE="$BUILD_DATE" \
    --build-arg GIT_COMMIT="$GIT_COMMIT" \
    --label "org.opencontainers.image.created=$BUILD_DATE" \
    --label "org.opencontainers.image.revision=$GIT_COMMIT" \
    -f web/Dockerfile .

# Push images
echo "Pushing images to registry..."
docker push "$REGISTRY/$USERNAME/$IMAGE_NAME-backend:$VERSION"
docker push "$REGISTRY/$USERNAME/$IMAGE_NAME-backend:latest"
docker push "$REGISTRY/$USERNAME/$IMAGE_NAME-frontend:$VERSION"
docker push "$REGISTRY/$USERNAME/$IMAGE_NAME-frontend:latest"

# Scan images for vulnerabilities
if command -v trivy &> /dev/null; then
    echo ""
    echo "Scanning images for vulnerabilities..."
    trivy image "$REGISTRY/$USERNAME/$IMAGE_NAME-backend:$VERSION" || true
    trivy image "$REGISTRY/$USERNAME/$IMAGE_NAME-frontend:$VERSION" || true
else
    echo "Note: trivy not found, skipping vulnerability scan"
fi

# Cleanup
echo ""
echo "Logging out..."
docker logout "$REGISTRY"

echo "=========================================="
echo "✓ Build and deploy complete!"
echo "=========================================="
