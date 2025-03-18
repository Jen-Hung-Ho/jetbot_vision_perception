#!/usr/bin/env python3
#
# Copyright (c) 2025, Jen-Hung Ho 
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

