from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import CognitiveServicesCredentials
from msrest.authentication import ApiKeyCredentials
from gpiozero import RGBLED
from colorzero import Color
#import face_recognition
#from gpiozero import MotionSensor
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

engine = pyttsx3.init()

# Set the voice to use
#voices = engine.getProperty('voices')
#engine.setProperty('voice', voices[1].id)

# Set the speech rate
#engine.setProperty('rate', 150)

'''Object Detector AUthentication'''
ENDPOINT_cv = "https://pfaproject.cognitiveservices.azure.com/"
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



conn_str = ""

# Create the BlobServiceClient object which will be used to access the container


computervision_client = ComputerVisionClient(endpoint_ay, CognitiveServicesCredentials(subscription_key_ay))

base_image_location = os.path.join(os.path.dirname(__file__))


approved = ['BNINA AYOUB', 'MZALI FIRAS', 'BNINA AYOUS']

led = RGBLED(red=18, green=23, blue=24)
cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480) 
'''
OCR: Read File using the Read API, extract text - remote
This example will extract text in an image, then print results, line by line.
This API call can also extract handwriting style text (not shown).
    '''
print("===== Afficher Votre Carte Etudiant =====")



    # Capturing a frame from the webcam
img_path = os.path.join(base_image_location,"Cards", "card.jpg")
ret, frame = cap.read()
cv2.imwrite(img_path, frame)
share_service_client = ShareServiceClient.from_connection_string(connection_string)
# Get a ShareDirectoryClient object for the folder you want to upload the image to
Cards_folder = share_service_client.get_share_client(share_name).get_directory_client("Cards")
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
# Upload the image to the folder
file_client = Cards_folder.upload_file(f"card_detected_{timestamp}.jpg", data=open(img_path, "rb"))
# Get the URL of the uploaded image
file_url = file_client.url
print(file_url)
img = cv2.imread(img_path)
# Call API with URL and raw response (allows you to get the operation location)
read_response = computervision_client.read(file_url + '?sv=2022-11-02&ss=bfqt&srt=sco&sp=rwdlacupiytfx&se=2023-05-23T21:14:32Z&st=2023-05-23T13:14:32Z&spr=https&sig=VSx9%2BUXdl%2B9jrQfEvD48uiwF6eDsl6j4pPn6xLNbbJc%3D',  raw=True)
# Get the operation location (URL with an ID at the end) from the response
read_operation_location = read_response.headers["Operation-Location"]
# Grab the ID from the URL
operation_id = read_operation_location.split("/")[-1]
# Calling the "GET" API and waiting for it to retrieve the results 
while True:
    read_result = computervision_client.get_read_result(operation_id)
    if read_result.status not in ['notStarted', 'running']:
        break
    time.sleep(1)
# show the image with rectangles drawn on it
with open(img_path, 'rb') as data:
    results = predictor.detect_image(project_id, published_name, data)
# looping through predictions
predictions = []
for prediction in results.predictions:
    if prediction.probability >= 0.9:
        predictions.append(prediction.tag_name)
        # set flag to True if at least one card is detected
        card_detected = True
        led.color = Color(0, 0, 1)
        print("\t" + prediction.tag_name + ": {0:.2f}% bbox.left = {1:.2f}, bbox.top = {2:.2f}, bbox.width = {3:.2f}, bbox.height = {4:.2f}".format(prediction.probability * 100, prediction.bounding_box.left, prediction.bounding_box.top, prediction.bounding_box.width, prediction.bounding_box.height))
        left = int(prediction.bounding_box.left * img.shape[1])
        top = int(prediction.bounding_box.top * img.shape[0])
        width = int(prediction.bounding_box.width * img.shape[1])
        height = int(prediction.bounding_box.height * img.shape[0])
        # draw the rectangle on the image
        cv2.rectangle(img, (left, top), (left+width, top+height),(255,215,0), 2)
        label = prediction.tag_name + ": {0:.2f}%".format(prediction.probability * 100)
        cv2.putText(img, label, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200, 0, 0), 2)

    # check flag to see if any cards were detected
if 'Carte ID' in predictions:
        led.color = Color(1, 0, 0)
        engine.say('Les cartes id ne sont pas accepte')
        engine.runAndWait()
        print('Les cartes id ne sont pas accepte')
elif 'Carte Etudiant' in predictions:
     for card in predictions:
            if card == 'Carte Etudiant':
                exists = False
                num_lines = 0
                if read_result.status == OperationStatusCodes.succeeded:
                    text_detected = False
                    for text_result in read_result.analyze_result.read_results:
                        if text_result.lines:
                            text_detected = True
                            num_lines += len(text_result.lines)
                            for line in text_result.lines:
                                print(line.text)
                                print(line.bounding_box)
                                for name in approved:
                                    for line in text_result.lines:
                                        if name[0:3] in line.text or name in line.text :
                                        #for line in text_result.lines:
                                        #print(line.text)
                                        #print(line.bounding_box)

                                            exists =True
                                            break  
                                break
                            break        
                    if not text_detected or num_lines < 3:
                        engine.say('Text nest pas claire')
                        engine.runAndWait()
                        led.color = Color(0, 0, 0)
                        print("Text nest pas claire")
                        break
                    elif exists:
                        #Speech
                        print(name, 'Accée Approuvé')
                        led.color = Color(0, 1, 0)
                        engine.say(str(nom),'...','Accée Approuvé')
                        engine.runAndWait()
                        break
                        
                    else:
                        led.color = Color(1, 0, 0)
                        print('Acces Refusé')    
                        engine.say('Acces Refusé')
                        engine.runAndWait()     
                        break
else:
    print('Aucune carte Etudiant n\'a éte detecte')
    #engine.say('Aucune carte Etudiant n\'a éte detecte')
    #engine.runAndWait()

cv2.imshow("Image with predictions", img)
        #Speech
# Print the URL of the uploaded image
print("URL of the uploaded image:", file_url)

cv2.waitKey(3000)
cap.release()
cv2.destroyAllWindows()
led.color = Color(0, 0, 0)
'''
END - Read File - remote
'''

print("End of Program.")
