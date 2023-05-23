import cv2
import os
import time

# Directory to save the frames
train_directory = 'train'

# Create the directory if it doesn't exist
if not os.path.exists(train_directory):
    os.makedirs(train_directory)

# Webcam index (0 for the default webcam)
webcam_index = 0

# Interval between frame captures (in seconds)
capture_interval = 2

# Initialize the webcam
webcam = cv2.VideoCapture(webcam_index)

# Check if the webcam is opened correctly
if not webcam.isOpened():
    print("Failed to open webcam")
    exit()

# Variable to track the number of captured frames
frame_count = 0

# Start capturing frames
while True:
    # Read the current frame from the webcam
    ret, frame = webcam.read()

    if not ret:
        print("Failed to capture frame")
        break

    # Display the frame
    cv2.imshow("Webcam", frame)

    # Save the frame to the train directory
    frame_path = os.path.join(train_directory, f"frame_{frame_count}.jpg")
    cv2.imwrite(frame_path, frame)

    # Increment the frame count
    frame_count += 1

    # Wait for the specified interval
    time.sleep(capture_interval)

    # Check for 'q' key press to exit
    if cv2.waitKey(1) == ord('q'):
        break

# Release the webcam and close the windows
webcam.release()
cv2.destroyAllWindows()
