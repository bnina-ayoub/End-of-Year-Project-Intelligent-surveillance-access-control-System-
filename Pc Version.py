from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import CognitiveServicesCredentials
from msrest.authentication import ApiKeyCredentials
from azure.storage.fileshare import ShareServiceClient, ShareDirectoryClient, ShareFileClient
from array import array
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

#import face_recognition
from PIL import Image
import cv2
import numpy as np
import os
import time
import sys
import time
import datetime
import azure.cognitiveservices.speech as speechsdk

'''Object Detector AUthentication'''
ENDPOINT_cv = "https://pfaproject.cognitiveservices.azure.com/"
prediction_key = "84885c1265444390819a5df6c9f6fe47"

# Replace with your published iteration name and project ID
published_name = "FinalModelCard"
project_id = "ba1ef21d-6dbc-4ea6-a4fe-aab291aab144"

# Authenticate with the Custom Vision service
prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
predictor = CustomVisionPredictionClient(ENDPOINT_cv, prediction_credentials)
base_image_location = os.path.dirname(__file__)


approved = ['BNINA AYOUB']

'''
Authenticate
Authenticates your credentials and creates a client.
'''
subscription_key_ay = "5e6a70c79cb74f7497cda181e4e2c73a"
endpoint_ay = "https://pfaproject.cognitiveservices.azure.com/"

subscription_key_fir = "828bac2d56a34e4da9ea7db5a256c779"
endpoint_fir = "https://pfa-proj.cognitiveservices.azure.com/"




# Setting the name of the shared file
account_name = "pfarepository"
account_key = "q4JdcaRYynIn7EbAXmgXXCtqvxI9Pl8ebbMv88Te0dVfGw3chdz8i3qkCSOi9/bJNQ/Ft5fQqX/J+AStXd3h0Q=="
share_name = "surveilance-system-storage"

connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"

computervision_client = ComputerVisionClient(endpoint_fir, CognitiveServicesCredentials(subscription_key_fir))


'''
END - Authenticate
'''

speech_config = speechsdk.SpeechConfig(subscription=subscription_key_ay, region='eastus')
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
speech_config.speech_synthesis_language = 'fr-FR'
speech_config.speech_synthesis_voice_name = 'fr-FR-CelesteNeural'
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

#Footage when gpio PIR motion detector
WIDTH = 640
HEIGHT = 480
FPS = 30

# Define video length in seconds
VIDEO_LENGTH = 10

# Start video recording
cap = cv2.VideoCapture(0)
filename = 'test_video.mp4'
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer = cv2.VideoWriter(filename, fourcc, FPS, (WIDTH, HEIGHT))
start_time = time.time()
while (time.time() - start_time) < VIDEO_LENGTH:
    ret, frame = cap.read()
    if ret:
        video_writer.write(frame)
    else:
        break
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
share_service_client = ShareServiceClient.from_connection_string(connection_string)
# Get a ShareDirectoryClient object for the folder you want to upload the image to
Video_folder = share_service_client.get_share_client(share_name).get_directory_client("Videos")

# Upload the image to the folder
file_client = Video_folder.upload_file(f"footage_{timestamp}.mp4", data=open(os.path.join(base_image_location, filename), "rb"))
# Release video resources
cap.release()
video_writer.release()










'''
OCR

'''
print("===== Ne bouger pas =====")
base_image_location = os.path.join(os.path.dirname(__file__))



    # Convert the frame to a format expected by Custom Vision
    # Now there is a trained endpoint that can be used to make a prediction
        # Classify the image using Custom Vision

timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # Capture a frame from the webcam
cap = cv2.VideoCapture(0)

ret, frame = cap.read()
img_path = os.path.join(base_image_location, "Cards", f"card_detected_{timestamp}.jpg")
cv2.imwrite(img_path, frame)


share_service_client = ShareServiceClient.from_connection_string(connection_string)

# Get a ShareDirectoryClient object for the folder you want to upload the image to
Cards_folder = share_service_client.get_share_client(share_name).get_directory_client("Cards")

# Upload the image to the folder
file_client = Cards_folder.upload_file(f"card_detected_{timestamp}.jpg", data=open(img_path, "rb"))

# Print the URL of the uploaded image

# Construct the blob name with the timestamp
# Upload the file to Azure Blob Storage

# Get an image with text
read_image_url = file_client.url + "?sv=2022-11-02&ss=bfqt&srt=sco&sp=rwdlacupiytfx&se=2023-05-11T20:50:33Z&st=2023-05-11T12:50:33Z&spr=https,http&sig=mVBNeHhHmTOwdrelw7ylmV5PzSYydGhaoT5wQZz2rM0%3D"
print("URL of the uploaded image:", read_image_url)
print(read_image_url)

img = cv2.imread(img_path)
# Call API with URL and raw response (allows you to get the operation location)

# Encode the image URL
read_response = computervision_client.read(read_image_url,  raw=True)

# Get the operation location (URL with an ID at the end) from the response
read_operation_location = read_response.headers["Operation-Location"]
# Grab the ID from the URL
operation_id = read_operation_location.split("/")[-1]

# Call the "GET" API and wait for it to retrieve the results 
while True:
    read_result = computervision_client.get_read_result(operation_id)
    if read_result.status not in ['notStarted', 'running']:
        break
    time.sleep(1)
# show the image with rectangles drawn on it
with open(img_path, 'rb') as data:
    results = predictor.detect_image(project_id, published_name, data)
    
    # set flag to False initially
card_detected = False

# loop through predictions
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

# check flag to see if any cards were detected
# Print the detected text, line by line
if 'Carte ID' in predictions:
        speech_synthesis_result = speech_synthesizer.speak_text_async('Les cartes identite ne sont pas acceptee').get()
        print()
elif 'Carte Etudiant' in predictions:
     for card in predictions:
            if card == 'Carte Etudiant':
                exists = False
                if read_result.status == OperationStatusCodes.succeeded:
                    text_detected = False
                    for text_result in read_result.analyze_result.read_results:
                        text_detected = True
                        for line in text_result.lines:
                            print(line.text)
                            print(line.bounding_box)
                        if text_result.lines[5].text in approved or text_result.lines[5].text[0:3] in approved[0][0:3]:
                            #for line in text_result.lines:
                            #print(line.text)
                            #print(line.bounding_box)
                            exists =True        
                    if not text_detected:
                        speech_synthesis_result = speech_synthesizer.speak_text_async("Le Texte n\'est pas clair ou vous n'avez pas l'acces, essayer de prendre une autre photo bien claire pour verifier").get()
                        print("Text nest pas claire")
                    elif exists:
                        speech_synthesis_result = speech_synthesizer.speak_text_async(text_result.lines[5].text +', ...' + 'Accee Approvee').get()
                        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                                print("Speech synthesized for text [{}]".format(text_result.lines[5].text))
                        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
                                cancellation_details = speech_synthesis_result.cancellation_details
                                print("Speech synthesis canceled: {}".format(cancellation_details.reason))
                                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                                    if cancellation_details.error_details:
                                        print("Error details: {}".format(cancellation_details.error_details))
                                        print("Did you set the speech resource key and region values?")
                                        print(text_result.lines[5].text)         

            elif card == 'Carte ID':
                    speech_synthesis_result = speech_synthesizer.speak_text_async('Les cartes identite ne sont pas acceptee').get()
                    print()
else:
        speech_synthesis_result = speech_synthesizer.speak_text_async('Aucune carte E n\'a été Detecté').get()


cv2.imshow("Image with predictions", img)
cv2.waitKey(10000)
cv2.destroyAllWindows()
'''
END - Read File - remote
'''

print("End of Computer Vision quickstart.")