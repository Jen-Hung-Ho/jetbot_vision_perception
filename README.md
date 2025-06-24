# JetBot Vision Perception with YOLO

**Short Description:**  
ROS2-based vision perception package for JetBot, utilizing YOLO models for real-time object detection and depth camera integration

build docker command:
docker build --network host -t jetbot_vision_perception 

- **run.sh user**  
  - Starts the Docker container as your current Linux user (non-root).
  - Usage:  
    ```bash
    ./run.sh user
    ```

- **start_shell.sh**  
  - (If present) Provides a quick way to enter an interactive shell inside the running Docker container.
  - Usage:  
    ```bash
    ./start_shell.sh
    ```

- **YOLO_export_Models.py**
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
# Jetbot ROS2 yolo_detection
> **Note:**  
> The provided Docker image includes only the ROS2 source code—it does **not** come with ROS2 pre-installed or built.  
> On first-time launch inside the container, you **must manually build the workspace** with:  
> 
> ```bash
> cd /ros2_ws && colcon build
> ```
> 
> You'll also see this reminder printed by `run.sh` if the `/ros2_ws/install/setup.bash` file is missing.

- Usage:
  ```bash
  # Navigate to the source directory
  cd ../ros2_ws
  # Build the package (requires root privileges)
  colcon build
  # Source the setup file
  . install/setup.bash
  # Launch YOLO detection node
  ros2 run jetbot_vision_perception yolo_detection
  ros2 run jetbot_vision_perception yolo_detection --ros-args -p model_path:=/data/yolov11n.engine
  ```


- python3 YOLO_export_Models.py engine 11
- python3 webcam_test.py
- python3 YOLO_detection_webcam.py
