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

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSDurabilityPolicy
from sensor_msgs.msg import Image

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib

import numpy as np
import cv2


class RTSPPublisherNode(Node):
    def __init__(self):
        super().__init__('rtsp_publisher')

        self.fps = 10  # match your caps framerate=10/1

        self.camera_color_topic = self.declare_parameter('camera_color_topic', '/camera/color/image_raw').get_parameter_value().string_value
        self.QosReliability = self.declare_parameter('qos_reliability', False).get_parameter_value().bool_value

        self.get_logger().info('RTSPPublisherNode initialized')

        self.get_logger().info('--------------------------------------------------')
        self.get_logger().info('Subscribing to ROS2 topic: {}'.format(self.camera_color_topic))
        self.get_logger().info('QosReliability      : {}'.format(self.QosReliability))
        self.get_logger().info('--------------------------------------------------')

        # QoS settings
        qos_profile = QoSProfile(depth=10)
        if self.QosReliability:
            qos_profile.reliability = QoSReliabilityPolicy.RELIABLE
        else:
            qos_profile.reliability = QoSReliabilityPolicy.BEST_EFFORT
        qos_profile.durability = QoSDurabilityPolicy.VOLATILE

        # ROS2 subscription (Gemini 335 color stream)
        self.subscription = self.create_subscription(
            Image,
            self.camera_color_topic,
            self.image_callback,
            qos_profile
        )

        # Initialize GStreamer
        Gst.init(None)

        # RTSP server setup
        self.server = GstRtspServer.RTSPServer()
        self.server.props.service = "8554"

        factory = GstRtspServer.RTSPMediaFactory()
        factory.set_shared(True)

        # Hardware-accelerated H.264 encoding pipeline for Jetson
        # Pipeline: appsrc → videoconvert → x264enc → rtph264pay
        pipeline_str = (
            "appsrc name=mysrc is-live=true format=time "
            "! capsfilter caps=video/x-raw,format=RGB,width=848,height=480,framerate=10/1 "
            "! videoconvert "
            "! video/x-raw,format=NV12 "
            "! nvvidconv "
            "! video/x-raw(memory:NVMM),format=NV12,framerate=10/1 "
            "! nvv4l2h264enc insert-sps-pps=true iframeinterval=10 bitrate=4000000 "
            "profile=0 level=4 preset-level=1 "
            "! h264parse config-interval=1 "
            "! rtph264pay name=pay0 pt=96"
        )


        # Sofware version for x264enc, if you don't have nvv4l2h264enc installed
        # Pipeline: appsrc → videoconvert → x264enc → rtph264pay
        """ pipeline_str = (
            "appsrc name=mysrc is-live=true format=time "
            "caps=video/x-raw,format=BGR,width=1280,height=720,framerate=10/1 "
            "! videoconvert "
            "! video/x-raw,format=NV12 "
            "! x264enc tune=zerolatency speed-preset=ultrafast bitrate=200000 "
            "! rtph264pay name=pay0 pt=96" 
        ) """


        factory.set_launch(pipeline_str)

        # Connect media-configure callback
        factory.connect("media-configure", self.on_media_config)

        mount_points = self.server.get_mount_points()
        mount_points.add_factory("/ros2stream", factory)

        self.server.attach(None)
        self.get_logger().info("RTSP server started at rtsp://<jetson-ip>:8554/ros2stream")

        # Store appsrc reference later
        self.appsrc = None
        self.pipeline = None              # keep pipeline reference
        self.ready_to_push = False        # flag to control pushing
        self.timestamp = 0                # initialize timestamp

        # GLib main loop for GStreamer
        self.loop = GLib.MainLoop()
        self.glib_thread = self.create_thread(self.loop.run)


    #
    #   Helper function to create a daemon thread
    #
    def create_thread(self, target):
        import threading
        t = threading.Thread(target=target, daemon=True)
        t.start()
        return t


    #
    #   Callback for when the RTSP media is configured
    #
    def on_media_config(self, factory, media):
        """Called when the RTSP stream is created."""
        self.get_logger().info("RTSP media-config triggered")

        # Get the pipeline
        pipeline = media.get_element()
        self.pipeline = pipeline          # store pipeline

        # Connect to RTSPMedia 'unprepared' signal to detect client disconnect
        media.connect("unprepared", self.on_media_unprepared)


        # Find appsrc by name
        self.appsrc = pipeline.get_child_by_name("mysrc")

        if self.appsrc:
            self.get_logger().info("Connected ROS2 → GStreamer appsrc")
            self.appsrc.set_property("stream-type", 0)
            self.appsrc.set_property("format", Gst.Format.TIME)
            self.appsrc.set_property("do-timestamp", True)
            self.ready_to_push = True     # allow pushing when client connected
            self.timestamp = 0            # reset timestamp per session        
        else:
            self.get_logger().error("Failed to find appsrc element!")
            self.ready_to_push = False



    #
    #   RTSPMedia unprepared handler (client disconnect / teardown)
    #
    def on_media_unprepared(self, media):
        self.get_logger().info("RTSP media unprepared (client disconnected). Stopping push.")
        self.ready_to_push = False
        self.appsrc = None
        self.pipeline = None


    #
    # Image callback for handling incoming ROS2 image messages
    #
    def image_callback(self, msg):

        # Take a local snapshot to avoid race with unprepared callback
        appsrc = self.appsrc

        # Do not push if no client or pipeline flushed
        if appsrc is None or not self.ready_to_push:
            self.get_logger().debug(f"Received image frame, size: {msg.width}x{msg.height}")
            return

        # Convert ROS2 Image → NumPy array (RGB8)
        frame = np.frombuffer(msg.data, dtype=np.uint8).reshape(msg.height, msg.width, 3)

        # Convert RGB → BGR for OpenCV/GStreamer
        # frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)


        # Encode into GStreamer buffer (still RGB)
        data = frame.tobytes()
        buf = Gst.Buffer.new_allocate(None, len(data), None)
        buf.fill(0, data)

        # Correct 10 FPS Timestamping
        buf.duration = Gst.util_uint64_scale_int(1, Gst.SECOND, self.fps)
        # timestamp = getattr(self, "timestamp", 0)
        buf.pts = buf.dts = self.timestamp
        self.timestamp = self.timestamp + buf.duration

        # Push buffer using local appsrc reference to avoid race with unprepared callback
        try:
            retval = appsrc.emit("push-buffer", buf)
        except AttributeError:
            # appsrc disappeared between snapshot and emit -> just stop
            self.get_logger().warn("appsrc become None during push_buffer, skip frame")
            return

        if retval == Gst.FlowReturn.FLUSHING:
            self.get_logger().warn("Pipeline is flushing, skipping frame")
        elif retval != Gst.FlowReturn.OK:
            self.get_logger().warn(f"Failed to push buffer: {retval}")


def main(args=None):
    rclpy.init(args=args)
    node = RTSPPublisherNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
