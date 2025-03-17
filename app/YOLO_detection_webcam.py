import os
import sys
import cv2
from ultralytics import YOLO


def get_model(format="engine"):
    # Change the current working directory to the desired folder
    os.chdir("../data")


    # Retrieve the model path based on the specified format
    if format == "onnx":
        print("1 onnx")
        model_path = "yolov8n.onnx"
    elif format == "engine":
        print("2 engine")
        model_path = "yolov8n.engine"
    else:
        raise ValueError("Unsupported format. Please choose 'onnx' or 'engine'.")

    return model_path


def main(webcam_id, format):


    # Open the webcam
    cap = cv2.VideoCapture(webcam_id)  # Change the index if you have multiple cameras
    # Load the YOLOv8 model
    model_path = get_model(format)

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
    format = sys.argv[2] if len(sys.argv) > 2 else "engine"
    print(f"Export format: {format}")  # Print the format information
    webcam_id = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    print(f"Camera id: {webcam_id}")  # Print the format information

    main(webcam_id, format)