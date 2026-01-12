#!/usr/bin/env bash

# Enable Docker BuildKit
export DOCKER_BUILDKIT=1

# Default version to "latest" if not provided
VERSION=${1:-latest}

# Get the current username
USERNAME=$(whoami)

echo "Building Docker image: jetbot_vision_perception:$VERSION"
echo "Using USERNAME: $USERNAME, USER_ID: $(id -u), GROUP_ID: $(id -g)"

# Build the Docker image with the specified version tag
docker build --network=host --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) --build-arg USERNAME=$USERNAME -t jetbot_vision_perception:$VERSION .