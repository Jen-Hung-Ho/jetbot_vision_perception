from ultralytics import YOLO
import sys
import os
import cv2

def get_model(format="engine"):
    # Change the current working directory to the desired folder
    os.chdir("../data")

    # Load a YOLOv8n PyTorch model
    model = YOLO("yolov8n.pt")

    # Export the model based on the specified format
    if format == "onnx":
        print("1 onnx")
        # print(f"Export format: {format}")  # Print the format information
        # model.export(format="onnx")  # creates 'yolov8n.onnx'
        model_path = "yolov8n.onnx"
    elif format == "engine":
        print("2 engine")
        # print(f"Export format: {format}")  # Print the format information
        # model.export(format="engine")  # creates 'yolov8n.engine'
        model_path = "yolov8n.engine"
    else:
        raise ValueError("Unsupported format. Please choose 'onnx' or 'engine'.")

    return model_path


def main(file_name, format):

    model_path = get_model(format)

    # Load the exported model
    print(f"Load model: {model_path}")  # Print the format information
    # Load the exported model with the specified task type
    trt_model = YOLO(model_path, task="detect")

    # Run inference on local file
    results = trt_model(file_name)
    # Run inference on URL
    # results = trt_model("https://ultralytics.com/images/bus.jpg")

    # Load the image
    image = cv2.imread(file_name)

    # List of class names (you can update this list with the actual class names)
    # class_names = ["person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch", "potted plant", "bed", "dining table", "toilet", "TV", "laptop", "mouse", "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"]
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
    print(f"Ouput YOLO detection file name:{output_file_name}")
    cv2.imwrite(output_file_name, image)

if __name__ == "__main__":
    print(f"arg:{sys.argv}")
    format = sys.argv[2] if len(sys.argv) > 2 else "engine"
    print(f"Export format: {format}")  # Print the format information
    file_name = sys.argv[1] if len(sys.argv) > 1 else "../out/bus.jpg"
    print(f"Input image: {file_name}")  # Print the format information

    main(file_name, format)