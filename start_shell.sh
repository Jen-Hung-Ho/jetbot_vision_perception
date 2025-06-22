#!/bin/bash

# Check if a container ID is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <container_id>"
else
    CONTAINER_ID=$1
    # Execute the command inside the specified container
    docker exec -it $CONTAINER_ID bash -c "source /ros2_ws/install/setup.bash && exec bash"
fi