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
  - The YOLO_export_Models.py script is designed to export a pre-trained YOLOv8 model (specifically, the lightweight "yolov8n.pt" version) into a different format for deployment. You can run the script from the command line and specify the export format as either `onnx` or `engine` (TensorRT). If no format is specified, it defaults to TensorRT (`engine`).
  - An exported model file (`yolov8n.onnx` or `yolov8n.engine`) in the `../data` directory, ready for deployment or inference using ONNX or TensorRT runtimes.
  ```bash
  python3 YOLO_export_Models.py onnx
  ```
# Jetbot ROS2 yolo_detection
- Usage:
  ```bash
  # Navigate to the source directory
  cd ../ros2_ws/src
  # Build the package (requires root privileges)
  colcon build
  # Source the setup file
  . install/local_setup.bash
  # Launch YOLO detection node
  ros2 run jetbot_vision_perception yolo_detection
  ```


python3 YOLO_export_Models.py onnx
python3 webcam_test.py
python3 YOLO_detection_webcam.py
