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

USAGE = """
Usage: python3 YOLO_detect.py [image_file] --model_path=<path> OR -p model_path:=<path> --format=<format>
       python3 YOLO_detect.py -? | -help

Examples:
  python3 YOLO_detect.py ../out/bus.jpg
  python3 YOLO_detect.py ../out/bus.jpg --model_path=/data/yolov11n.engine --format=engine
  python3 YOLO_detect.py ../out/bus.jpg -p model_path:=/data/yolov11n.pt --format=onnx

Arguments:
  image_file        (optional) Path to input image file (default: ../out/bus.jpg)
  --model_path=PATH (optional) Path to model file (default: ../data/yolov11n.engine)
  -p model_path:=PATH (optional) ROS2-style parameter for model path
  --format=FORMAT   (optional) Model format: 'engine' or 'onnx' (default: engine)

If model_path is not provided, defaults to ../data/yolov11n.engine
"""

def parse_model_path_arg(args):
    # Look for --model_path or -p model_path:=<path>
    for i, arg in enumerate(args):
        if arg.startswith("--model_path="):
            return arg.split("=", 1)[1]
        if arg == "-p" and i + 1 < len(args):
            param = args[i + 1]
            if param.startswith("model_path:="):
                return param.split(":=", 1)[1]
    return None

def parse_format_arg(args):
    # Look for --format
    for arg in args:
        if arg.startswith("--format="):
            return arg.split("=", 1)[1]
    return "engine"

def get_model(format="engine"):
    # Assume data folder is ../data relative to script location
    data_dir = "../data"

    # Load a YOLOv8n PyTorch model
    model = YOLO(os.path.join(data_dir, "yolov11n.pt"))

    # Export the model based on the specified format
    if format == "onnx":
        print("Exporting to onnx")
        # model.export(format="onnx")  # creates 'yolov11n.onnx'
        model_path = os.path.join(data_dir, "yolov11n.onnx")
    elif format == "engine":
        print("Using engine format")
        # model.export(format="engine")  # creates 'yolov11n.engine'
        model_path = os.path.join(data_dir, "yolov11n.engine")
    else:
        raise ValueError("Unsupported format. Please choose 'onnx' or 'engine'.")

    return model_path


def main(file_name, model_path, format):

    if not os.path.exists(model_path):
        print(f"Model path {model_path} does not exist. Attempting to get model from data folder.")
        model_path = get_model(format)

    # Load the exported model
    print(f"Loading model: {model_path}")
    trt_model = YOLO(model_path, task="detect")

    # Run inference on local file
    results = trt_model(file_name)

    # Load the image
    image = cv2.imread(file_name)

    # Get class names from the model
    class_names = trt_model.names

    # Draw bounding boxes
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Extract values from the tensor
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            class_id = int(box.cls[0])
            label = class_names[class_id] if class_id < len(class_names) else f"Class: {class_id}"
            cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Extract the file name without the extension
    base_name = os.path.splitext(os.path.basename(file_name))[0]

    # Save the image with bounding boxes
    output_file_name = f"../out/{base_name}_out.jpg"
    print(f"Output YOLO detection file name: {output_file_name}")
    cv2.imwrite(output_file_name, image)

if __name__ == "__main__":
    print(f"args: {sys.argv}")

    # Print usage and exit if -? or -help is present
    if any(arg in ("-?", "-help") for arg in sys.argv):
        print("===============================================")
        print(USAGE)
        print("===============================================")
        sys.exit(0)

    # Default values
    file_name = "../out/bus.jpg"
    model_path = None
    format = "engine"

    # Parse file_name if provided as first positional argument
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        file_name = sys.argv[1]

    # Parse model_path from args
    model_path = parse_model_path_arg(sys.argv)
    if not model_path:
        model_path = "../data/yolov11n.engine"

    # Parse format from args
    format = parse_format_arg(sys.argv)

    print(f"Input image: {file_name}")
    print(f"Model path: {model_path}")
    print(f"Format: {format}")

    main(file_name, model_path, format)