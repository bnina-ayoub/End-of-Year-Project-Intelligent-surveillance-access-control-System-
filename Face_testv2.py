from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import CognitiveServicesCredentials
from msrest.authentication import ApiKeyCredentials
import face_recognition
from gpiozero import MotionSensor, RGBLED
from colorzero import Color
import cv2
import numpy as np
from array import array
import os
from PIL import Image
import sys
import time
import datetime
from azure.storage.fileshare import ShareServiceClient, ShareDirectoryClient, ShareFileClient
import pyttsx3


'''Object Detector AUthentication'''
ENDPOINT_cv = ""
prediction_key = ""

# Replace with your published iteration name and project ID
published_name = ""
project_id = ""

# Authenticate with the Custom Vision service
prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
predictor = CustomVisionPredictionClient(ENDPOINT_cv, prediction_credentials)
base_image_location = os.path.join (os.path.dirname(__file__), "Images")

#FileShare Credentials
account_name = ""
account_key = ""
share_name = ""

connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"




'''
Authenticate
Authenticates your credentials and creates a client.
'''
subscription_key = ""
endpoint = ""


conn_str = "DefaultEndpointsProtocol=https;AccountName=pfarepository;AccountKey=q4JdcaRYynIn7EbAXmgXXCtqvxI9Pl8ebbMv88Te0dVfGw3chdz8i3qkCSOi9/bJNQ/Ft5fQqX/J+AStXd3h0Q==;EndpointSuffix=core.windows.net"



computervision_client = ComputerVisionClient(endpoint_fir, CognitiveServicesCredentials(subscription_key_fir))



def findEncodeing1(img):
        encodeList = []
        for i in img:
            i = cv2.cvtColor(i, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(i)[0]
            encodeList.append(encode)
        return encodeList

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Set the voice to use
#voices = engine.getProperty('voices')
#engine.setProperty('voice', voices[1].id)

# Set the speech rate
#engine.setProperty('rate', 150)
base_image_location = os.path.join(os.path.dirname(__file__))
img_path = os.path.join(base_image_location,"faces")
face_path = os.path.join(base_image_location,'Face.jpg')
imageList = os.listdir(img_path)
led = RGBLED(red=18, green=23, blue=24)
face = []
faces_name = []


'''
END - Authenticate
'''
approved = ['BNINA AYOUB', 'MZALI FIRAS', 'BNINA AYOUS']

#For the gpio PIR motion detector

pir = MotionSensor(12)

WIDTH = 640
HEIGHT = 480
FPS = 20.0

for i in imageList:
    face.append(cv2.imread(f'{img_path}/{i}'))
    faces_name.append(os.path.splitext(i)[0])

    # Start video recording
cap = cv2.VideoCapture(0)
filename = 'footage.avi'
fourcc = cv2.VideoWriter_fourcc(*'XVID')
video_writer = cv2.VideoWriter(filename, fourcc, FPS, (WIDTH, HEIGHT))
Proceed = False

encodeListKnown = findEncodeing1(face)
cap.set(3,640) # set Width
cap.set(4,480) # set Height
yes = 0
nn = 0
#engine.say('I am in the while')
#engine.runAndWait()
print('Waiting')
pir.wait_for_motion()
wait = time.time()
led.color = Color(0, 0, 1)
while pir.wait_for_motion() and not Proceed:
    ret, frame = cap.read()
    fr = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
    fr = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)
    video_writer.write(fr)
    cv2.imshow('Result',frame)
    faceCurentFrame = face_recognition.face_locations(fr)
    encodeCurentFrame = face_recognition.face_encodings(fr, faceCurentFrame)
    # print(len(encodeCurentFrame))
    # print(len(faceCurentFrame))
    matches = [0]
    matchesIndex = 0
    name = "Unknown"
    faceLoc = None
    for encodeface, faceLoc in zip(encodeCurentFrame, faceCurentFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeface)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeface)
        print(faceDis)
        matchesIndex = np.argmin(faceDis)
        # test=True
    print(matches)
    # faceDis is a list of the percentage of faces to compare. the low value is the close person
    # matches is a list of booleans contains true in the column of the person closest to the frame
    if faceLoc is not None:
        if (matches[matchesIndex]):
            name = faces_name[matchesIndex].upper()
            # print(name)
            # print(faceLoc)
            indexx = name[name.index('{') + 1: name.index('}')]
            name = name[0:name.index('(')]
            yes = yes + 1
        else:    
            nn = nn + 1
            print(nn)
        y1 = faceLoc[0] * 4
        x2 = faceLoc[1] * 4
        y2 = faceLoc[2] * 4
        x1 = faceLoc[3] * 4
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (0, 0, 255), cv2.FILLED) 
        cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0), 2)
        cv2.imshow('Result', frame)
    else:
        cv2.imshow('Result', frame)
        if time.time() - wait:
            print("NO FACE DETECTED")
            led.color = Color(0, 0, 0)

    if yes == 4:
        led.color = Color(0, 1, 0) 
        engine.say(str(name), 'Visage Identifie,... Montrer ta carte etudiant pour proceder')
        engine.runAndWait()
        print(indexx)
        Proceed = True
        video_writer.release()
    elif nn - yes == 300:
            engine.say(name, 'Visage non reconnue')
            engine.runAndWait()
            led.color = Color(1, 0, 0)
            video_writer.release()
            break
    
    key = cv2.waitKey(1)
cv2.imwrite(face_path, frame)
video_writer.release()

