import asyncio
import io
import cv2
import os
import sys
import time
import uuid
import requests
from urllib.parse import urlparse
from io import BytesIO
from azure.storage.blob import BlobServiceClient
# To install this module, run:
# python -m pip install Pillow
from PIL import Image, ImageDraw
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person, QualityForRecognition


# This key will serve all examples in this document.
KEY = "4a7158b4ae374fa2b927491eca747f48"

# This endpoint will be used in all examples in this quickstart.
ENDPOINT = "https://surveillance-face.cognitiveservices.azure.com/"

# Base url for the Verify and Facelist/Large Facelist operations
IMAGE_BASE_URL = 'https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/Face/images/'

# Used in the Person Group Operations and Delete Person Group examples.
# You can call list_person_groups to print a list of preexisting PersonGroups.
# SOURCE_PERSON_GROUP_ID should be all lowercase and alphanumeric. For example, 'mygroupname' (dashes are OK).
PERSON_GROUP_ID = 'admins' # assign a random ID (or name it anything)

# Used for the Delete Person Group example.
TARGET_PERSON_GROUP_ID = 'visitor' # assign a random ID (or name it anything)

# Create an authenticated FaceClient.
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))

'''
Create the PersonGroup
'''
# Create empty Person Group. Person Group ID must be lower case, alphanumeric, and/or with '-', '_'.
print('Person group:', PERSON_GROUP_ID)
#face_client.person_group.create(person_group_id=PERSON_GROUP_ID, name=PERSON_GROUP_ID, recognition_model='recognition_04')

# Define woman friend
#admin = face_client.person_group_person.create(PERSON_GROUP_ID, name="Admin")

# Define connection string to your storage account
conn_str = "DefaultEndpointsProtocol=https;AccountName=indexstoragebnina;AccountKey=/fRZ7plLTwWPGbYFtzVY2hBoTwX9sUnNN8o/hRXaf/qaqFaxBIj065v8a3HHxA3DW/mKMIDhPL+S+AStOjTk2w==;EndpointSuffix=core.windows.net"

# Create the BlobServiceClient object which will be used to access the container
blob_service_client = BlobServiceClient.from_connection_string(conn_str=conn_str)

# Set the name of the container that you want to access
container_name = "faces"

# Get a reference to the container
container_client = blob_service_client.get_container_client(container_name)
'''
Detect faces and register them to each person
'''
# Find all jpeg images of friends in working directory (TBD pull from web instead)
admin_images = [blob.name for blob in container_client.list_blobs()]
print(admin_images)
# Add to child person
for image in admin_images:
    # Check if the image is of sufficent quality for recognition.
    sufficientQuality = True
    detected_faces = face_client.face.detect_with_url(url=image, detection_model='detection_03', recognition_model='recognition_04', return_face_attributes=['qualityForRecognition'])
    for face in detected_faces:
        if face.face_attributes.quality_for_recognition != QualityForRecognition.high:
            sufficientQuality = False
            print("{} has insufficient quality".format(face))
            break
        face_client.person_group_person.add_face_from_url(PERSON_GROUP_ID, admin.person_id, image)
        print("face {} added to person {}".format(face.face_id, admin.person_id))
    if not sufficientQuality: continue


'''
Train PersonGroup
'''
# Train the person group
print("pg resource is {}".format(PERSON_GROUP_ID))
rawresponse = face_client.person_group.train(PERSON_GROUP_ID, raw= True)
print(rawresponse)

while (True):
    training_status = face_client.person_group.get_training_status(PERSON_GROUP_ID)
    print("Training status: {}.".format(training_status.status))
    print()
    if (training_status.status is TrainingStatusType.succeeded):
        break
    elif (training_status.status is TrainingStatusType.failed):
        face_client.person_group.delete(person_group_id=PERSON_GROUP_ID)
        sys.exit('Training the person group has failed.')
    time.sleep(5)

'''
Identify a face against a defined PersonGroup
'''
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
        
# Group image for testing against
test_image = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/Face/images/identification1.jpg"

print('Pausing for 10 seconds to avoid triggering rate limit on free account...')
time.sleep (10)

# Detect faces
face_ids = []
# We use detection model 3 to get better performance, recognition model 4 to support quality for recognition attribute.
faces = face_client.face.detect_with_url(test_image, detection_model='detection_03', recognition_model='recognition_04', return_face_attributes=['qualityForRecognition'])
for face in faces:
    # Only take the face if it is of sufficient quality.
    if face.face_attributes.quality_for_recognition == QualityForRecognition.high or face.face_attributes.quality_for_recognition == QualityForRecognition.medium:
        face_ids.append(face.face_id)

# Identify faces
results = face_client.face.identify(face_ids, PERSON_GROUP_ID)
print('Identifying faces in image')
if not results:
    print('No person identified in the person group')
for identifiedFace in results:
    if len(identifiedFace.candidates) > 0:
        print('Person is identified for face ID {} in image, with a confidence of {}.'.format(identifiedFace.face_id, identifiedFace.candidates[0].confidence)) # Get topmost confidence score

        # Verify faces
        verify_result = face_client.face.verify_face_to_person(identifiedFace.face_id, identifiedFace.candidates[0].person_id, PERSON_GROUP_ID)
        print('verification result: {}. confidence: {}'.format(verify_result.is_identical, verify_result.confidence))
    else:
        print('No person identified for face ID {} in image.'.format(identifiedFace.face_id))
 

print()
print('End of quickstart.')