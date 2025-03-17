import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from ultralytics import YOLO

class YOLODetectionNode(Node):
    def __init__(self):
        super().__init__('yolo_detection_node')
        
        # YOLO model initialization
        model_path = "/data/yolov8n.engine"  # Replace with the actual path
        self.trt_model = YOLO(model_path, task="detect")
        
        # CvBridge initialization
        self.bridge = CvBridge()
        
        # Subscriptions
        self.create_subscription(Image, '/camera/color/image_raw', self.color_image_callback, 10)
        self.create_subscription(Image, '/camera/depth/image_raw', self.depth_image_callback, 10)
    
    def color_image_callback(self, msg):
        self.get_logger().info('Received color image')
        try:
            # Convert ROS Image to OpenCV frame
            frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            # YOLO detection
            results = self.trt_model(frame)
            self.process_results(frame, results)
        except Exception as e:
            self.get_logger().error(f"Failed to process color image: {e}")
    
    def depth_image_callback(self, msg):
        self.get_logger().info('Received depth image')
        try:
            # Convert ROS Image to OpenCV frame
            frame = self.bridge.imgmsg_to_cv2(msg, "16UC1")
            # For depth, process if required for YOLO
            # Example usage
        except Exception as e:
            self.get_logger().error(f"Failed to process depth image: {e}")

    def process_results(self, frame, results):
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                conf = box.conf[0].cpu().numpy()
                cls = int(box.cls[0].cpu().numpy())
                # Draw bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{self.trt_model.names[cls]}: {conf:.2f}", (x1, y1 - 5), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        # Display the frame
        cv2.imshow("YOLO Detection", frame)
        cv2.waitKey(1)

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
