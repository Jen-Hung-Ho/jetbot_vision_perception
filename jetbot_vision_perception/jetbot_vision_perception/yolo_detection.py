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

import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import ParameterType, SetParametersResult, Parameter
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError # Package to convert between ROS and OpenCV Images
import cv2
import numpy as np
from ultralytics import YOLO

class YOLODetectionNode(Node):

    def parameter_callback(self, params):
        for param in params:
            if param.name == 'start' and param.type_ == Parameter.Type.BOOL:
                self.start = param.value
                self.get_logger().info('start= {}'.format(bool(param.value)))

        return SetParametersResult(successful=True)

    def __init__(self):
        super().__init__('yolo_detection_node')
        
        self.start = self.declare_parameter('start', True).get_parameter_value().bool_value
        self.debug = self.declare_parameter('debug', False).get_parameter_value().bool_value
        self.model_path = self.declare_parameter('model_path', '/data/yolov8n.engine').get_parameter_value().string_value
        self.camera_color_topic = self.declare_parameter('camera_color_topic', '/camera/color/image_raw').get_parameter_value().string_value
        self.camera_depth_topic = self.declare_parameter('camera_depth_topic', '/camera/depth/image_raw').get_parameter_value().string_value
        self.img_pub_topic = self.declare_parameter('image_depth_topic', 'depth_image_raw').get_parameter_value().string_value
        
        self.get_logger().info('start              : {}'.format(self.start))
        self.get_logger().info('model_path         : {}'.format(self.model_path))
        self.get_logger().info('camera_color_topic : {}'.format(self.camera_color_topic))
        self.get_logger().info('camera_depth_topic : {}'.format(self.camera_depth_topic))
        self.get_logger().info('pub_img_depth_topic: {}'.format(self.img_pub_topic))

        # Add parameters callback 
        self.add_on_set_parameters_callback(self.parameter_callback)

        # YOLO model initialization
        # model_path = "/data/yolov8n.engine"
        self.trt_model = YOLO(self.model_path, task="detect")
        
        # CvBridge initialization
        self.bridge = CvBridge()
        
        # Subscriptions
        # self.create_subscription(Image, '/camera/color/image_raw', self.color_image_callback, 10)
        self.create_subscription(Image, self.camera_color_topic, self.color_image_callback, 10)
        # self.create_subscription(Image, '/camera/depth/image_raw', self.depth_image_callback, 10)
        self.create_subscription(Image, self.camera_depth_topic, self.depth_image_callback, 10)

        # Create the publisher, This publish wil will publish an Image
        # to the image_row topic, The queue size is 10 messages
        self.image_pub = self.create_publisher(Image, self.img_pub_topic, 10)

        # Initialize depth frame
        self.depth_frame = None  # Store depth frame


    def color_image_callback(self, msg):
        self.get_logger().debug('Received color image')
        try:
            # Convert ROS Image to OpenCV frame
            frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            # YOLO detection
            results = self.trt_model(frame)
            self.process_results(frame, results)
        except Exception as e:
            self.get_logger().error(f"Failed to process color image: {e}")
    
    def depth_image_callback(self, msg):
        self.get_logger().debug('Received depth image')
        try:
            # Convert ROS Image to OpenCV frame
            frame = self.bridge.imgmsg_to_cv2(msg, "16UC1")
            # For depth, process if required for YOLO
            # Convert depth image to meters
            self.depth_frame = frame * 0.001  # Scale millimeters to meters
        except Exception as e:
            self.get_logger().error(f"Failed to process depth image: {e}")

    def process_results(self, color_frame, results):
        if self.depth_frame is None:
            self.get_logger().warn("Depth frame is not available.")
            return

        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                conf = box.conf[0].cpu().numpy()
                cls = int(box.cls[0].cpu().numpy())

                # Calculate median depth within bounding box
                object_depth = np.median(self.depth_frame[y1:y2, x1:x2])
                label = f"{self.trt_model.names[cls]}: {conf:.2f}, {object_depth:.2f}m"

                # Draw bounding box
                cv2.rectangle(color_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(color_frame, f"{self.trt_model.names[cls]}: {conf:.2f}", (x1, y1 - 5), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.putText(color_frame, label, (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


        if self.debug:
            # Display the frame
            cv2.imshow("YOLO Detection", color_frame)
            cv2.waitKey(1)

        try:
            self.image_pub.publish(self.bridge.cv2_to_imgmsg(color_frame, "bgr8"))
        except CvBridgeError as e:
            self.get_logger().error(e)

def main(args=None):
    rclpy.init(args=args)
    node = YOLODetectionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down YOLO Detection Node')
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
