import cv2
import time
import requests
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials

# Azure Face API credentials
KEY = "4a7158b4ae374fa2b927491eca747f48"

# This endpoint will be used in all examples in this quickstart.
ENDPOINT = "https://surveillance-face.cognitiveservices.azure.com/"

PERSON_GROUP_ID = 'admin'

# Create a Face client
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))

# Open video capture device (webcam)
cap = cv2.VideoCapture(0)

# Check if the capture device was successfully opened
if not cap.isOpened():
    print('Unable to open the camera')
    exit()

# Wait for camera to warm up
print('Pausing for 10 seconds to avoid triggering rate limit on free account...')
time.sleep(10)

# Start the video stream loop
while True:
    # Capture a frame from the video stream
    ret, frame = cap.read()
    
    # Check if the frame was successfully captured
    if not ret:
        print('Unable to capture a frame')
        continue
    
    # Detect faces in the frame
    faces = face_client.face.detect_with_url(frame, detection_model='detection_04', recognition_model='recognition_04', return_face_attributes=['age', 'gender', 'emotion'])
    
    # Loop through each detected face
    for face in faces:
        # Get face rectangle coordinates
        rect = face.face_rectangle
        x = rect.left
        y = rect.top
        w = rect.width
        h = rect.height
        
        # Draw a rectangle around the face
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Only take the face if it is of sufficient quality.
        if face.face_attributes.quality_for_recognition == 'High' or face.face_attributes.quality_for_recognition == 'Medium':
            # Identify the person in the person group
            results = face_client.face.identify([face.face_id], PERSON_GROUP_ID)
            if not results:
                print('No person identified in the person group')
            else:
                identified_face = results[0]
                if len(identified_face.candidates) > 0:
                    # Get the person's name
                    person = face_client.person_group_person.get(PERSON_GROUP_ID, identified_face.candidates[0].person_id)
                    person_name = person.name
                    
                    # Display the person's name above the rectangle
                    cv2.putText(frame, person_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
    # Display the frame with detected faces
    cv2.imshow('Video', frame)
    
    # Wait for a key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture device and destroy any windows
cap.release()
cv2.destroyAllWindows()
