#!/usr/bin/env python3
#
# Copyright (c) 2026, Jen-Hung Ho 
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

from ultralytics import YOLO
import sys
import os
import cv2

# default model engine  -- more efficient
# python3 YOLLO_export_Models.py
# python3 YOLLO_export_Models.py onnx 11

def export_model(format="engine", model_version="8"):
    # Change the current working directory to the desired folder
    os.chdir("../data")

    # https://docs.ultralytics.com/models/yolov8/
    # Load a pre-trained YOLOv8n (nano) model using the Ultralytics library.
    # The "yolov8n.pt" file contains the model weights for the YOLOv8 nano variant,
    # which is a lightweight, fast, and efficient version suited for real-time applications.

    # NOTE for model version:
    # - For version 8: If 'yolov8n.pt' does not exist under the data folder,
    #   it will be automatically downloaded from:
    #   https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt
    # - For version 11: You must manually download the weights from:
    #   https://huggingface.co/Ultralytics/YOLO11/blob/365ed86341e7a7456dbc4cafc09f138814ce9ff1/yolo11n.pt
    #   and rename the file to 'yolov11n.pt' in the data folder.

    # Choose model file based on version
    if model_version == "11":
        model_file = "yolov11n.pt"
        if not os.path.exists(model_file):
            print(f"[ERROR] '{model_file}' not found in ../data.")
            print("Please manually download the weights from:")
            print("  https://huggingface.co/Ultralytics/YOLO11/blob/365ed86341e7a7456dbc4cafc09f138814ce9ff1/yolo11n.pt")
            print(f"And rename the file to '{model_file}' in the data folder.")
            sys.exit(1)
    else:
        model_file = "yolov8n.pt"


    print(f"Using model: {model_file}")
    model = YOLO(model_file)

    # Export the model based on the specified format
    if format == "onnx":
        print("1 onnx=ONNX")
        print(f"Export format: {format}")  # Print the format information

        # Note: File will be saved as 'yolov8n.onnx' in the current working directory
        model_path = model_file.replace(".pt", ".onnx")

        # Export to TensorRT 'onnx' format
        model.export(format="onnx", dynamic=True)  # creates 'yolov8n.onnx'

    elif format == "engine":
        print("2 engine=TensorRT")
        print(f"Export format: {format}")  # Print the format information
        # Note: File will be saved as 'yolov8n.engine' in the current working directory
        model_path = model_file.replace(".pt", ".engine")

        # Export to TensorRT 'engine' format
        model.export(format="engine", dynamic=True, int8=False)  # creates 'yolov8n.engine'

    else:
        raise ValueError("Unsupported format. Please choose 'onnx' or 'engine'.")

    print(f"Export format: {model_path}")  # Print the export information
    return model_path

if __name__ == "__main__":

    if len(sys.argv) == 1:
        print("----------------------------------------------------------------")
        print("Usage: python3 YOLO_export_Models.py [engine|onnx] [8|11]")
        print("Example: python3 YOLO_export_Models.py engine 11")
        print("----------------------------------------------------------------")


    format = sys.argv[1] if len(sys.argv) > 1 else "engine"
    model_version = sys.argv[2] if len(sys.argv) > 2 else "8"


    print(f"Export format: {format}, Model version: {model_version}")

    model_path = export_model(format, model_version)

