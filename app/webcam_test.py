import sys
import cv2

# Get the webcam device ID from the command-line argument
if len(sys.argv) > 1:
    device_id = int(sys.argv[1])
else:
    device_id = 0  # Default to /dev/video0 if no argument is provided

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