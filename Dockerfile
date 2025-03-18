# Use the base image
FROM ultralytics/ultralytics:latest-jetson-jetpack6


# Set environment variables
ENV QT_X11_NO_MITSHM=1
ENV QT_QPA_PLATFORM=xcb
ENV QT_PLUGIN_PATH=/usr/local/lib/python3.10/dist-packages/cv2/qt/plugins
ENV DISPLAY=:0
ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=humble

# Define the ROS2 setup script path
ARG ROS2_SETUP=/opt/ros/$ROS_DISTRO/setup.bash

# Uninstall any existing NumPy versions
# RUN pip uninstall -y numpy

# Install the specific version of NumPy required by YOLO
# RUN pip install --force-reinstal numpy==1.23.5

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

# Update the package list and install vi
# RUN apt-get update && apt-get install -y vim

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

# Install compatible setuptools version
RUN pip install setuptools==59.6.0

# Create ROS2 workspace
RUN mkdir -p /ros2_ws/src

# Copy the ROS2 package folder from the host machine to the container
COPY ./jetbot_vision_perception /ros2_ws/src/jetbot_vision_perception

# Build the ROS2 package
WORKDIR /ros2_ws
RUN /bin/bash -c "source ${ROS2_SETUP} && colcon build"


# Set the working directory
WORKDIR /app

# Copy the application files
COPY . /app

# Copy the custom script to uninstall and install NumPy
# COPY install_numpy.sh /app/install_numpy.sh

# Run the custom script
# RUN chmod +x /app/install_numpy.sh && /app/install_numpy.sh

# Ensure the correct version of NumPy is installed before running the application
RUN pip check