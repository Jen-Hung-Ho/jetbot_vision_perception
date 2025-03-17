#!/bin/bash

# Uninstall any existing NumPy versions
pip uninstall -y numpy

# Install the specific version of NumPy required by YOLO
pip install numpy==1.23.5