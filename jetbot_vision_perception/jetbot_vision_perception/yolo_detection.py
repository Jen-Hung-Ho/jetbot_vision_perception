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
from rclpy.parameter import Parameter
from rcl_interfaces.msg import ParameterType, SetParametersResult
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError # Package to convert between ROS and OpenCV Images
import message_filters
import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.utils import LOGGER
from collections import defaultdict
import logging

# Set ultralytics logger to warning level to avoid cluttering the console
LOGGER.setLevel(logging.WARNING)

class YOLODetectionNode(Node):

    def parameter_callback(self, params):
        for param in params:
            if param.name == 'start' and param.type_ == Parameter.Type.BOOL:
                self.start = param.value
                self.get_logger().info('start= {}'.format(bool(param.value)))
            elif param.name == 'target_class' and param.type_ == Parameter.Type.STRING:
                self.target_class = param.value
                self.get_logger().info('target_class= {}'.format(self.target_class))
            elif param.name == 'tracking_mode' and param.type_ == Parameter.Type.BOOL:
                self.tracking_mode = param.value
                self.get_logger().info('tracking_mode= {}'.format(bool(param.value)))


        return SetParametersResult(successful=True)

    def __init__(self):
        super().__init__('yolo_detection_node')
        
        self.start = self.declare_parameter('start', True).get_parameter_value().bool_value
        self.debug = self.declare_parameter('debug', False).get_parameter_value().bool_value
        self.model_path = self.declare_parameter('model_path', '/data/yolov8n.pt').get_parameter_value().string_value
        self.target_class = self.declare_parameter('target_class', 'person').get_parameter_value().string_value
        self.tracking_mode = self.declare_parameter('tracking_mode', False).get_parameter_value().bool_value
        self.camera_color_topic = self.declare_parameter('camera_color_topic', '/camera/color/image_raw').get_parameter_value().string_value
        self.camera_depth_topic = self.declare_parameter('camera_depth_topic', '/camera/depth/image_raw').get_parameter_value().string_value
        self.img_pub_topic = self.declare_parameter('image_depth_topic', 'depth_image_raw').get_parameter_value().string_value

        self.get_logger().info("-----------------------------------------------------")
        self.get_logger().info('start              : {}'.format(self.start))
        self.get_logger().info('model_path         : {}'.format(self.model_path))
        self.get_logger().info('camera_color_topic : {}'.format(self.camera_color_topic))
        self.get_logger().info('camera_depth_topic : {}'.format(self.camera_depth_topic))
        self.get_logger().info('pub_img_depth_topic: {}'.format(self.img_pub_topic))
        self.get_logger().info('target_class       : {}'.format(self.target_class))
        self.get_logger().info('tracking_mode      : {}'.format(self.tracking_mode))
        self.get_logger().info("-----------------------------------------------------")

        # Add parameters callback 
        self.add_on_set_parameters_callback(self.parameter_callback)

        # YOLO model initialization
        # model_path = "/data/yolov8n.pt"
        # self.trt_model = YOLO(self.model_path, task="detect")
        self.trt_model = YOLO(self.model_path)

        self.declare_parameter('class_labels', '')
        self.track_history = defaultdict(lambda: [])

        # Set class_labels to YOLO model's class names and update the parameter server
        # This ensures the parameter server always reflects the actual model classes
        if hasattr(self.trt_model, "names") and self.trt_model.names:
            self.class_labels = ','.join(self.trt_model.names.values())
            self.get_logger().info("-----------------------------------------------------")
            self.get_logger().info(f"Class labels: {self.class_labels}")
            self.get_logger().info("-----------------------------------------------------")
        else:
            self.class_labels = ''
            self.get_logger().warn("YOLO model does not provide class names.")


        # Update class_labels to the parameter server
        self.set_parameters([
            rclpy.parameter.Parameter(
                'class_labels',
                rclpy.Parameter.Type.STRING,
                self.class_labels
            )
        ])


        # CvBridge initialization
        self.bridge = CvBridge()

        # Subscriptions
        # self.create_subscription(Image, '/camera/color/image_raw', self.color_image_callback, 10)
        # self.create_subscription(Image, '/camera/depth/image_raw', self.depth_image_callback, 10)
        self.color_sub = message_filters.Subscriber(self, Image, self.camera_color_topic)
        self.depth_sub = message_filters.Subscriber(self, Image, self.camera_depth_topic)

        # ApproximateTimeSynchronizer to synchronize color and depth images
        # This synchronizer will ensure that both color and depth images are processed togethe
        self._synchronizer = message_filters.ApproximateTimeSynchronizer( 
            [self.color_sub, self.depth_sub], queue_size=10, slop=0.1)
        self._synchronizer.registerCallback(self.sync_image_callbacks)

        # Create the publisher, This publish wil will publish an Image
        # to the image_row topic, The queue size is 10 messages
        self.image_pub = self.create_publisher(Image, self.img_pub_topic, 10)

        # Initialize depth frame
        self.depth_frame = None  # Store depth frame

    #
    # Synchronize color and depth image callbacks
    # This is used to ensure that both color and depth images are processed together
    #
    def sync_image_callbacks(self, color_msg, depth_msg):
        self.get_logger().debug('Synchronized color and depth images received')

        if (self.start == True):
            try:
                # Convert ROS Image messages to OpenCV images
                color_frame = self.bridge.imgmsg_to_cv2(color_msg, "bgr8")
                depth_frame = self.bridge.imgmsg_to_cv2(depth_msg, "16UC1")
                # Store depth frame for processing
                self.depth_frame = depth_frame  * 0.001  # Convert mm to meters

                # Run YOLO detection or tracking
                if self.tracking_mode:
                    results = self.trt_model.track(color_frame, stream=True, persist=True, tracker="bytetrack.yaml")
                else:
                    results = self.trt_model.predict(color_frame)

                # Process results (draw boxes, publish, etc.)
                self.process_results(color_frame, results)
            except Exception as e:
                self.get_logger().error(f"Failed to process synchronized images: {e}")



    #
    #   Process results from YOLO detection or tracking
    #
    def process_results(self, color_frame, results):
        if self.depth_frame is None:
            self.get_logger().warn("Depth frame is not available.")
            return

        person_detected_and_close = False

        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                conf = box.conf[0].cpu().numpy()
                cls = int(box.cls[0].cpu().numpy())

                class_name = self.trt_model.names[cls]

                # Calculate median depth within bounding box
                object_depth = np.median(self.depth_frame[y1:y2, x1:x2])
                label = f"{self.trt_model.names[cls]}: {conf:.2f}, {object_depth:.2f}m"

                # Tracking mode: get track ID if available ---
                track_id = getattr(box, 'id', None)
                if track_id is not None:
                    label = f"ID {int(track_id[0].cpu().numpy())} | {label}"

                # Default color: green
                box_color = (0, 255, 0)

                # If in tracking mode and person is close, use yellow
                # TODO: tempory code for testing YOLO tracking mode
                if self.tracking_mode and class_name == "person" and object_depth < 0.7:
                    box_color = (0, 255, 255)  # Yellow
                    person_detected_and_close = True
                    if self.tracking_mode:
                        self.get_logger().info(
                            "SYNC-HO: Tracked person within {:.2f}m, track_id: {}".format(object_depth,
                                int(track_id[0].cpu().numpy()) if track_id is not None else "N/A"
                            )
                        )

                # TODO: tempory code for testing YOLO tracking mode
                if self.tracking_mode and track_id is not None:
                    tid = int(track_id[0].cpu().numpy())
                    center = (int((x1 + x2) / 2), int((y1 + y2) / 2))
                    self.track_history[tid].append(center)
                    # Limit history length
                    max_history = 30
                    if len(self.track_history[tid]) > max_history:
                        self.track_history[tid].pop(0)
                    # Draw the track history
                    points = self.track_history[tid]
                    for j in range(1, len(points)):
                        cv2.line(color_frame, points[j - 1], points[j], (0, 0, 255), 2)

                # Draw bounding box and label
                cv2.rectangle(color_frame, (x1, y1), (x2, y2), box_color, 2)
                cv2.putText(color_frame, label, (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color, 2)


        # Switch to tracking mode if person detected and close
        if person_detected_and_close and not self.tracking_mode:
            self.get_logger().info("Person detected within 0.7m! Switching to YOLO tracking mode.")
            self.trt_model = YOLO(self.model_path, task="track")
            self.tracking_mode = True

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
