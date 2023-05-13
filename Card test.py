from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import CognitiveServicesCredentials
from msrest.authentication import ApiKeyCredentials
import face_recognition
from gpiozero import MotionSensor
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
prediction_key = "84885c1265444390819a5df6c9f6fe47"

# Replace with your published iteration name and project ID
published_name = "Card Detector"
project_id = "ba1ef21d-6dbc-4ea6-a4fe-aab291aab144"

# Authenticate with the Custom Vision service
prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
predictor = CustomVisionPredictionClient(ENDPOINT_cv, prediction_credentials)
base_image_location = os.path.join (os.path.dirname(__file__), "Images")

#FileShare Credentials
account_name = "pfarepository"
account_key = "q4JdcaRYynIn7EbAXmgXXCtqvxI9Pl8ebbMv88Te0dVfGw3chdz8i3qkCSOi9/bJNQ/Ft5fQqX/J+AStXd3h0Q=="
share_name = "surveilance-system-storage"

connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"




'''
Authenticate
Authenticates your credentials and creates a client.
'''
subscription_key_ay = "5e6a70c79cb74f7497cda181e4e2c73a"
endpoint_ay = "https://pfaproject.cognitiveservices.azure.com/"

subscription_key_fir = "828bac2d56a34e4da9ea7db5a256c779"
endpoint_fir = "https://pfa-proj.cognitiveservices.azure.com/"


conn_str = "DefaultEndpointsProtocol=https;AccountName=pfarepository;AccountKey=q4JdcaRYynIn7EbAXmgXXCtqvxI9Pl8ebbMv88Te0dVfGw3chdz8i3qkCSOi9/bJNQ/Ft5fQqX/J+AStXd3h0Q==;EndpointSuffix=core.windows.net"

# Create the BlobServiceClient object which will be used to access the container


computervision_client = ComputerVisionClient(endpoint_fir, CognitiveServicesCredentials(subscription_key_fir))

base_image_location = os.path.join(os.path.dirname(__file__))


approved = ['BNINA AYOUB', 'MZALI FIRAS', 'BNINA AYOUS']


cap = cv2.VideoCapture(0)

'''
OCR: Read File using the Read API, extract text - remote
This example will extract text in an image, then print results, line by line.
This API call can also extract handwriting style text (not shown).
    '''
print("===== Afficher Votre Carte Etudiant =====")



    # Capturing a frame from the webcam
img_path = os.path.join(base_image_location, "card.jpg")
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
time.sleep(5)
while 1:
    ret, frame = cap.read()
    fr = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
    fr = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)
    img = cv2.imread(img_path)
    cv2.imwrite(img_path, frame)
    share_service_client = ShareServiceClient.from_connection_string(connection_string)

    # Get a ShareDirectoryClient object for the folder you want to upload the image to
    Cards_folder = share_service_client.get_share_client(share_name).get_directory_client("Cards")

    # Upload the image to the folder
    file_client = Cards_folder.upload_file(f"card_detected_{timestamp}.jpg", data=open(img_path, "rb"))

    # Get the URL of the uploaded image
    file_url = file_client.url


    # Call API with URL and raw response (allows you to get the operation location)
    read_response = computervision_client.read(file_url,  raw=True)

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
            print("\t" + prediction.tag_name + ": {0:.2f}% bbox.left = {1:.2f}, bbox.top = {2:.2f}, bbox.width = {3:.2f}, bbox.height = {4:.2f}".format(prediction.probability * 100, prediction.bounding_box.left, prediction.bounding_box.top, prediction.bounding_box.width, prediction.bounding_box.height))
            left = int(prediction.bounding_box.left * img.shape[1])
            top = int(prediction.bounding_box.top * img.shape[0])
            width = int(prediction.bounding_box.width * img.shape[1])
            height = int(prediction.bounding_box.height * img.shape[0])

            # draw the rectangle on the image
            cv2.rectangle(img, (left, top), (left+width, top+height),(255,215,0), 2)
            label = prediction.tag_name + ": {0:.2f}%".format(prediction.probability * 100)
            cv2.putText(img, label, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200, 0, 0), 2)
    cv2.imshow("Image with predictions", img)

    # check flag to see if any cards were detected
    if 'Carte ID' in predictions:
            #engine.say('Les cartes id ne sont pas accepte')
            #engine.runAndWait()
            print('Les cartes id ne sont pas accepte')
            break
    elif 'Carte Etudiant' in predictions:
         for card in predictions:
                if card == 'Carte Etudiant':
                    exists = False
                    if read_result.status == OperationStatusCodes.succeeded:
                        text_detected = False
                        for text_result in read_result.analyze_result.read_results:
                            if text_result.lines:
                                text_detected = True
                                for line in text_result.lines:
                                    print(line.text)
                                    print(line.bounding_box)
                                    for name in approved:
                                        if name[0:3] in text_result.lines.text or name in text_result.lines.text :
                                        #for line in text_result.lines:
                                        #print(line.text)
                                        #print(line.bounding_box)
                                            nom = name
                                            exists =True 
                                            break      
                                    break
                                break        
                        if not text_detected:
                            #engine.say('Text nest pas claire')
                            #engine.runAndWait()
                            led.color = Color(0, 0, 0)
                            print("Text nest pas claire")
                        elif exists:
                            #Speech
                            print(nom)
                            led.color = Color(0, 1, 0)
                            #engine.say(str(nom),'...','Accée Approuvé')
                            #engine.runAndWait()
                            break
                            
                        else:
                            led.color = Color(0, 0, 0)
                            print('Acces Refusé')    
                            #engine.say('Acces Refusé')
                            #engine.runAndWait()     
    else:
        print('Aucune carte Etudiant n\'a éte detecte')
        #engine.say('Aucune carte Etudiant n\'a éte detecte')
        #engine.runAndWait()
    if cv2.waitKey(1) == ord('q') or exists:
         break
            #Speech

    # Print the URL of the uploaded image
print("URL of the uploaded image:", file_url)

cv2.waitKey(0)
cv2.destroyAllWindows()
'''
END - Read File - remote
'''

print("End of Program.")