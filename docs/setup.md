## JetBot Vision Perception with YOLO Model - Setup Guide

1. **Docker Base Image** <br>
   This project’s Docker image is derived from the following base image:
   ```
   ARG BASE_IMAGE=ultralytics/ultralytics:latest-jetson-jetpack6
   ```
   > The base image is maintained by Ultralytics and is available on Docker Hub:
https://hub.docker.com/r/ultralytics/ultralytics

2. **Clone the Repository** <br>
   Open your terminal and run the following command to clone the repository:
   ```bash
   git clone https://github.com/Jen-Hung-Ho/jetbot_vision_perception
   ```

3. **Navigate to the Repository Directory** <br>
   Change to the directory of the cloned repository:
   ```bash
   cd jetbot_vision_perception
   ```

4. **Build the Docker Image** <br>
   This step builds the project’s Docker image and automatically installs the ROS 2 Humble environment inside the container.
   Ensure the `build.sh` script has execute permissions. If not, add execute permissions using:
   ```bash
   chmod +x build.sh
   ```

   Then, run the `build.sh` script to build the Docker image:
   ```bash
   ./build.sh
   ```
   
5. **Start Docker** <br>
   Execute the following commands to run the docker as your current Linux user (non_root).
   ```bash
   . run.sh user
   ```
    
6. **Attach to an Existing Running Docker Container** <br>
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
   ```
7. **Exporting YOLO models for deployment**
   - The YOLO_export_Models.py script is designed to export a pre-trained YOLO model (specifically, the lightweight "yolov8n.pt" or "yolov11n.pt" versions) into a different format for deployment. You can run the script from the command line and specify:
    - the export format: onnx or engine (TensorRT)
    - the YOLO version: 8 or 11
   - If no format is specified, it defaults to TensorRT (`engine`).
   - It will generate an exported model file (`yolov8n.onnx`, `yolov8n.engine` or `yolov11n.onnx`, `yolov11n.engine`) in the `../data` directory, ready for deployment or inference using ONNX or TensorRT runtimes.
   ```bash
   Usage:   python3 YOLO_export_Models.py [engine|onnx] [8|11]
   Example: python3 YOLO_export_Models.py engine 11
   ```
   > **Note (for YOLOv11 users)**:
   > The yolov11n.pt weights must be downloaded manually from the following link and placed in the data/ folder:
   > [Download yolov11n.pt](https://huggingface.co/Ultralytics/YOLO11/blob/365ed86341e7a7456dbc4cafc09f138814ce9ff1/yolo11n.pt)
   > Be sure to rename the file to yolov11n.pt after downloading.
