# Use an argument for the base image
ARG BASE_IMAGE=ultralytics/ultralytics:latest-jetson-jetpack6
FROM ${BASE_IMAGE}


# Use arguments for user, group IDs, and username
ARG USER_ID=1000
ARG GROUP_ID=1000
ARG USERNAME=jetbot

# Create a new user with specified user id, group id, and username
RUN groupadd -g ${GROUP_ID} ${USERNAME} && \
    useradd -u ${USER_ID} -g ${USERNAME} -m -s /bin/bash ${USERNAME} && \
    echo "${USERNAME}:${USERNAME}" | chpasswd && \
    adduser ${USERNAME} sudo && \
    (getent group video || groupadd -r video) && \
    usermod -aG video ${USERNAME}


# Change the ownership of the home directory to the new user
RUN chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}

# Create the necessary directory
RUN mkdir -p /home/${USERNAME}/.cache/clip_trt && \
chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}/.cache

# Set environment variables
ENV QT_X11_NO_MITSHM=1
ENV QT_QPA_PLATFORM=xcb
ENV QT_PLUGIN_PATH=/usr/local/lib/python3.10/dist-packages/cv2/qt/plugins
ENV DISPLAY=:0
ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=humble

# Define the ROS2 setup script path
ARG ROS2_SETUP=/opt/ros/$ROS_DISTRO/setup.bash


# Install v4l-utils and Qt packages
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    lsb-release \
    v4l-utils \
    qtbase5-dev \
    qtchooser \
    qt5-qmake \
    qtbase5-dev-tools \
    vim


# Install ultralytics tracking mode Python dependencies
RUN pip install lap>=0.5.12

# Add ROS2 repository and install ROS2 Humble
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | apt-key add - && \
    sh -c 'echo "deb http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" > /etc/apt/sources.list.d/ros2-latest.list' && \
    apt-get update && apt-get install -y \
    ros-humble-desktop \
    python3-rosdep \
    python3-colcon-common-extensions && \
    rosdep init && \
    rosdep update && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Source both ROS2 Humble and colcon build setup scripts
RUN echo "source /opt/ros/$ROS_DISTRO/setup.bash" >> ~/.bashrc
RUN echo "source /ros2_ws/install/setup.bash" >> /root/.bashrc

# Add ROS2 setup script to the jetbot user's .bashrc
RUN echo "source /opt/ros/$ROS_DISTRO/setup.bash" >> /home/${USERNAME}/.bashrc && \
    echo "source /ros2_ws/install/setup.bash" >> /home/${USERNAME}/.bashrc && \
    chown ${USERNAME}:${USERNAME} /home/${USERNAME}/.bashrc

# Install compatible setuptools version
RUN pip install setuptools==59.6.0

# Create ROS2 workspace
RUN mkdir -p /ros2_ws/src

# NOTE:
# The code under /ros2_ws/src/jetbot_vision_perception will NOT be built in this Docker image.
# Instead, it will be mounted into the container at runtime (e.g., via run.sh),
# and then built/installed inside the running container as part of the development workflow.
#
# This allows for live code changes without rebuilding the Docker image.

# *** FIX: Change ownership before switching user ***
RUN chown -R ${USERNAME}:${USERNAME} /ros2_ws


# Set the working directory
WORKDIR /app

# NOTE:
# The files under /app will NOT be copied or built in this Docker image.
# Instead, the /app directory will be mounted from the host machine at runtime (e.g., via run.sh),
# similar to how the ROS2 code is mounted. This allows for live code changes without rebuilding the image.


# Ensure the correct version of NumPy is installed before running the application
RUN pip check