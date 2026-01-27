## JetBot Vision Perception with YOLO Model - Setup Guide

1. **Docker Base Image **:
   This project’s Docker image is derived from the following base image:
   ```
   ARG BASE_IMAGE=ultralytics/ultralytics:latest-jetson-jetpack6
   ```
   > The base image is maintained by Ultralytics and is available on Docker Hub:
https://hub.docker.com/r/ultralytics/ultralytics

2. **Clone the Repository**:
   Open your terminal and run the following command to clone the repository:
   ```bash
   git clone https://github.com/Jen-Hung-Ho/jetbot_vision_perception
   ```

3. **Navigate to the Repository Directory**:
   Change to the directory of the cloned repository:
   ```bash
   cd jetbot_vision_perception
   ```

4. **Build the Docker Image**:
   Ensure the `build.sh` script has execute permissions. If not, add execute permissions using:
   ```bash
   chmod +x build.sh
   ```

   Then, run the `build.sh` script to build the Docker image:
   ```bash
   ./build.sh
   ```
   
8. **Start Docker:**
   Execute the following commands to run the docker as your current Linux user (non_root).
   ```bash
   . run.sh user
   ```
    
9. **Attach to an Existing Running Docker Container**:
   To attach to an existing running Docker container, use the following commands:
   ```bash
   docker ps
   ```

   Identify the `CONTAINER ID` of the running container (e.g., `422fc05b7655`), then run:
   ```bash
   . start_shell.sh <CONTAINER_ID>
   ```

   For example:
   ```bash
   . start_ros2_shell.sh 422fc05b7655
