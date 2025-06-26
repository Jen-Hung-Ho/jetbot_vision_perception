#!/bin/bash
# xhost +

# usage:
# run.sh admin
# run.sh user

# Get the user id and group id
ROOT="$(dirname "$(readlink -f "$0")")"
USER_ID=$(id -u)
USER_NAME=$(id -un)
GROUP_ID=$(id -g)
GROUP_NAME=$(id -gn)

# Set the environment variables
DISPLAY_VAR=$DISPLAY
ROS_DOMAIN_ID=7

# Set the volume mappings
VOLUME_X11=/tmp/.X11-unix/:/tmp/.X11-unix:rw
VOLUME_ROS_LOG=$HOME/.ros/log:/.ros/log

# Define Docker volumes and environment variables
ROOT=$(dirname "$0")
DOCKER_VOLUMES="
--volume=$VOLUME_X11 \
--volume=$ROOT/app:/app \
--volume=$ROOT/data:/data \
--volume=$ROOT/out:/out \
--volume=$ROOT/jetbot_vision_perception:/ros2_ws/src/jetbot_vision_perception \
--volume=$ROOT/install:/ros2_ws/install \
--volume=$ROOT/build:/ros2_ws/build \
--volume=/etc/passwd:/etc/passwd:ro \
--volume=/etc/group:/etc/group:ro \
--volume=$VOLUME_ROS_LOG \
"

DOCKER_ENV_VARS="
--env DISPLAY=$DISPLAY_VAR \
--env QT_X11_NO_MITSHM=1 \
--env QT_QPA_PLATFORM=xcb \
--env QT_PLUGIN_PATH=/usr/local/lib/python3.10/dist-packages/cv2/qt/plugins \
--env ROS_DOMAIN_ID=$ROS_DOMAIN_ID \
--env HOME=/tmp \
"

# check for V4L2 devices
V4L2_DEVICES=""

for i in {0..9}
do
    if [ -a "/dev/video$i" ]; then
        V4L2_DEVICES="$V4L2_DEVICES --device /dev/video$i "
    fi
done

# check for I2C devices
I2C_DEVICES=""

for i in {0..9}
do
    if [ -a "/dev/i2c-$i" ]; then
        I2C_DEVICES="$I2C_DEVICES --device /dev/i2c-$i "
    fi
done

DOCKER_DEVICES="
--device /dev/snd \
--device /dev/bus/usb \
--device=/dev/input \
"
DOCKER_ARGS="${DOCKER_VOLUMES} ${DOCKER_ENV_VARS} ${V4L2_DEVICES} ${I2C_DEVICES} ${DOCKER_DEVICES}"

# Set the docker image
# DOCKER_IMAGE=${DOCKER_IMAGE:-ultralytics/ultralytics:latest-jetson-jetpack6}
DOCKER_IMAGE=${DOCKER_IMAGE:-jetbot_vision_perception:latest}


# Define the NumPy version required by YOLO
NUMPY_VERSION=${NUMPY_VERSION:-1.23.5}

# Define the command to run inside the container
CMD="pip install numpy==$NUMPY_VERSION && \
    source /opt/ros/humble/setup.bash && \
    if [ -f /ros2_ws/install/setup.bash ]; then \
        source /ros2_ws/install/setup.bash; \
    else \
        echo 'WARNING: /ros2_ws/install/setup.bash not found! Please run '\''cd /ros2_ws && colcon build'\'' inside the container to build your ROS2 packages.'; \
    fi; \
    /bin/bash"

# Run the docker command
# Check if the first input parameter is 'admin'
if [ "$1" == "user" ]; then
    echo "Running as USER: $USER_NAME ($USER_ID):$GROUP_NAME ($GROUP_ID)"

    sudo docker run --runtime=nvidia -it --user $USER_ID:$GROUP_ID --group-add video --rm --net host --ipc=host --privileged\
        ${DOCKER_ARGS} \
        $DOCKER_IMAGE /bin/bash -c  "$CMD"
else
    echo "Running as ROOT user"
    docker run -it --rm --net host --ipc=host --runtime=nvidia --privileged\
        ${DOCKER_ARGS} \
        --workdir /app \
        $DOCKER_IMAGE /bin/bash -c "$CMD"
fi
