from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import CognitiveServicesCredentials
from msrest.authentication import ApiKeyCredentials
import cv2
from array import array
import os
from PIL import Image
import sys
import time
import datetime
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import azure.cognitiveservices.speech as speechsdk

'''Object Detector AUthentication'''
ENDPOINT_cv = "https://pfaproject.cognitiveservices.azure.com/"
prediction_key = ""

# Replace with your published iteration name and project ID
published_name = "Card Detector"
project_id = "ba1ef21d-6dbc-4ea6-a4fe-aab291aab144"

# Authenticate with the Custom Vision service
prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
predictor = CustomVisionPredictionClient(ENDPOINT_cv, prediction_credentials)
base_image_location = os.path.join (os.path.dirname(__file__), "Images")




'''
Authenticate
Authenticates your credentials and creates a client.
'''
subscription_key = ""
endpoint = ""


conn_str = "DefaultEndpointsProtocol=https;AccountName=pfarepository;AccountKey=q4JdcaRYynIn7EbAXmgXXCtqvxI9Pl8ebbMv88Te0dVfGw3chdz8i3qkCSOi9/bJNQ/Ft5fQqX/J+AStXd3h0Q==;EndpointSuffix=core.windows.net"

# Create the BlobServiceClient object which will be used to access the container
blob_service_client = BlobServiceClient.from_connection_string(conn_str=conn_str)

# Set the name of the container that you want to access
container_name = "cards"

# Get a reference to the container
container_client = blob_service_client.get_container_client(container_name)

computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))


'''
END - Authenticate
'''

speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region='eastus')
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
speech_config.speech_synthesis_language = 'fr-FR'
speech_config.speech_synthesis_voice_name = 'fr-FR-CelesteNeural'

speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

approved = ['BNINA AYOUB', 'MZALI FIRAS', 'BNINA AYOUS']

'''
OCR: Read File using the Read API, extract text - remote
This example will extract text in an image, then print results, line by line.
This API call can also extract handwriting style text (not shown).
'''
print("===== Read File - remote =====")
base_image_location = os.path.join(os.path.dirname(__file__))

cap = cv2.VideoCapture(0)

#while True:
    # Capture a frame from the webcam
ret, frame = cap.read()

    # Convert the frame to a format expected by Custom Vision
    # Now there is a trained endpoint that can be used to make a prediction
        # Classify the image using Custom Vision
img_path = os.path.join (base_image_location, "Cards", "card.jpg")
cv2.imwrite(img_path, frame)

timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

blob_client = container_client.get_blob_client(f"my_blob_{timestamp}.jpg")
img = cv2.imread(img_path)

# Construct the blob name with the timestamp
# Upload the file to Azure Blob Storage
with open(img_path, "rb") as data:
    blob_client.upload_blob(data)

# Get an image with text
read_image_url = blob_client.url

# Call API with URL and raw response (allows you to get the operation location)
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
    for prediction in results.predictions:
        if prediction.probability >= 0.8:
            print("\t" + prediction.tag_name + ": {0:.2f}% bbox.left = {1:.2f}, bbox.top = {2:.2f}, bbox.width = {3:.2f}, bbox.height = {4:.2f}".format(prediction.probability * 100, prediction.bounding_box.left, prediction.bounding_box.top, prediction.bounding_box.width, prediction.bounding_box.height))
            left = int(prediction.bounding_box.left * img.shape[1])
            top = int(prediction.bounding_box.top * img.shape[0])
            width = int(prediction.bounding_box.width * img.shape[1])
            height = int(prediction.bounding_box.height * img.shape[0])

    # draw the rectangle on the image
            cv2.rectangle(img, (left, top), (left+width, top+height),(255,215,0), 2)
            label = prediction.tag_name + ": {0:.2f}%".format(prediction.probability * 100)
            cv2.putText(img, label, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200, 0, 0), 2)

# Print the detected text, line by line
if prediction.tag_name == 'Carte Etudiant':
    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                if line.text in approved or 'BNI' in line.text or 'AYOU' in line.text:
                    speech_synthesis_result = speech_synthesizer.speak_text_async(line.text +', ...' + 'Accee Approvee').get()
                    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                        print("Speech synthesized for text [{}]".format(line.text))
                    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
                        cancellation_details = speech_synthesis_result.cancellation_details
                        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
                        if cancellation_details.reason == speechsdk.CancellationReason.Error:
                            if cancellation_details.error_details:
                                print("Error details: {}".format(cancellation_details.error_details))
                                print("Did you set the speech resource key and region values?")
                print(line.text)
                print(line.bounding_box)
elif prediction.tag_name == 'Carte ID':
    speech_synthesis_result = speech_synthesizer.speak_text_async('Les cartes identite ne sont pas acceptee').get()
print()


cv2.imshow("Image with predictions", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
'''
END - Read File - remote
'''

print("End of Computer Vision quickstart.")
