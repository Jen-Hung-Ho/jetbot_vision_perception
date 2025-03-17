from ultralytics import YOLO
import sys
import os
import cv2

# default model engine  -- more efficient
# python3 YOLLO_export_Models.py
# python3 YOLLO_export_Models.py onnx

def export_model(format="engine"):
    # Change the current working directory to the desired folder
    os.chdir("../data")

    # https://docs.ultralytics.com/models/yolov8/
    # Load a pre-trained YOLOv8n (nano) model using the Ultralytics library.
    # The "yolov8n.pt" file contains the model weights for the YOLOv8 nano variant,
    # which is a lightweight, fast, and efficient version suited for real-time applications.
    model = YOLO("yolov8n.pt")

    # Export the model based on the specified format
    if format == "onnx":
        print("1 onnx=ONNX")
        print(f"Export format: {format}")  # Print the format information
        # Set the desired file name for the exported model
        model_path = "yolov8n.onnx"
        # Export to TensorRT 'onnx' format
        model.export(format="onnx", dynamic=True)  # creates 'yolov8n.onnx'
        # Note: File will be saved as 'yolov8n.onnx' in the current working directory
        model_path = "yolov8n.onnx"
    elif format == "engine":
        print("2 engine=TensorRT")
        print(f"Export format: {format}")  # Print the format information
        # Export to TensorRT 'engine' format
        model.export(format="engine", dynamic=True, int8=False)  # creates 'yolov8n.engine'
        # Note: File will be saved as 'yolov8n.engine' in the current working directory
        model_path = "yolov8n.engine"
    else:
        raise ValueError("Unsupported format. Please choose 'onnx' or 'engine'.")

    print(f"Export format: {model_path}")  # Print the export information
    return model_path

if __name__ == "__main__":
    format = sys.argv[1] if len(sys.argv) > 1 else "engine"
    print(f"Export format: {format}")  # Print the format information

    model_path = export_model(format)

