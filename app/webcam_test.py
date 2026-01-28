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

import sys
import cv2
import argparse

# Define usage message
USAGE = """
Usage: python3 webcam_test.py [webcam_id]
       python3 webcam_test.py -? | -help

Examples:
  python3 webcam_test.py
  python3 webcam_test.py 0
  python3 webcam_test.py 1

Arguments:
  webcam_id         (optional) Camera index (default: 0)

Description:
  Opens the specified webcam and displays the video feed in a window.
  Press 'q' to quit. The script uses OpenCV to capture and display frames.
  
  To find available webcam IDs, run: v4l2-ctl --list-devices
"""

# Check for help flags
if len(sys.argv) > 1 and (sys.argv[1] in ['-?', '-help', '--help']):
    print(f"arg:{sys.argv}")
    print("=" * 48)
    print(USAGE)
    sys.exit(0)

# Parse arguments
parser = argparse.ArgumentParser(add_help=False)  # Disable default help to customize
parser.add_argument('webcam_id', nargs='?', type=int, default=0, help='Camera index (default: 0)')

args = parser.parse_args()
device_id = args.webcam_id

print(f"display id:{device_id}")

# Open the video capture
cap = cv2.VideoCapture(device_id)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Display the resulting frame
    cv2.imshow('Webcam', frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close the window
cap.release()
cv2.destroyAllWindows()