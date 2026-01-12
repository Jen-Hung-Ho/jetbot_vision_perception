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

import os
import sys
import cv2
from ultralytics import YOLO

USAGE = """
Usage: python3 YOLO_detection_webcam.py [webcam_id] --model_path=<path> OR -p model_path:=<path>
       python3 YOLO_detection_webcam.py -? | -help

Examples:
  python3 YOLO_detection_webcam.py
  python3 YOLO_detection_webcam.py 0 --model_path=/data/yolov11n.engine
  python3 YOLO_detection_webcam.py 0 -p model_path:=/data/yolov11n.pt

       
Arguments:
  webcam_id         (optional) Camera index (default: 0)
  --model_path=PATH (optional) Path to model file
  -p model_path:=PATH (optional) ROS2-style parameter for model path

If model_path is not provided, defaults to /data/yolov11n.engine
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

def main(webcam_id, model_path):


    # Open the webcam
    cap = cv2.VideoCapture(webcam_id)  # Change the index if you have multiple cameras

    # Load the exported model with the specified task type
    trt_model = YOLO(model_path, task="detect")
    
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Perform object detection
        results = trt_model(frame)

        # Process the results
        for result in results:
            # print(f"HOJ:{result.verbose()}- end")
            # Draw bounding boxes and labels on the image
            boxes = result.boxes  # Get the boxes from results
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()  # Get the coordinates
                conf = box.conf[0].cpu().numpy()  # Confidence score
                cls = int(box.cls[0].cpu().numpy())  # Class ID
            
                # Draw bounding box
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(frame, f"{trt_model.names[cls]}: {conf:.2f}", (int(x1), int(y1) - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Display the resulting frame
        cv2.imshow("Webcam Object Detection", frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the webcam and close windows
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    print(f"arg:{sys.argv}")

    # Print usage and exit if -? or -help is present
    if any(arg in ("-?", "-help") for arg in sys.argv):
        print("===============================================")
        print(USAGE)
        print("===============================================")
        sys.exit(0)

     # Default values
    webcam_id = 0
    model_path = None

    # Parse webcam id if provided
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        webcam_id = int(sys.argv[1])

    # Parse model_path from args
    model_path = parse_model_path_arg(sys.argv)
    if not model_path:
        # Fallback to second positional argument if present
        if len(sys.argv) > 2 and not sys.argv[2].startswith("-"):
            model_path = sys.argv[2]
        else:
            # print("Usage: python3 YOLO_detection_webcam.py [webcam_id] --model_path=<path> OR -p model_path:=<path>")
            # sys.exit(1)
            # Default model path
            model_path = "/data/yolov11n.engine"


    print(f"Camera id: {webcam_id}")
    print(f"Model path: {model_path}")


    main(webcam_id, model_path)