import cv2
import time
# Open video capture device (webcam)
cap = cv2.VideoCapture(0)

# Check if the capture device was successfully opened
if not cap.isOpened():
    print('Unable to open the camera')
    exit()

# Wait for camera to warm up
print('Pausing for 10 seconds to avoid triggering rate limit on free account...')
# Start the video stream loop
while True:
    # Capture a frame from the video stream
    ret, frame = cap.read()
    
    # Check if the frame was successfully captured
    if not ret:
        print('Unable to capture a frame')
        continue
    
    # Detect faces in the frame
    
    
    # Loop through each detected face
        # Only take the face if it is of sufficient quality.
    # Display the frame with detected faces
    cv2.imshow('Video', frame)
    
    # Wait for a key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture device and destroy any windows
cap.release()
cv2.destroyAllWindows()
