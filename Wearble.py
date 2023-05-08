import cv2
import os
import time
import requests
from azure.storage.blob import BlockBlobService, PublicAccess

# Set up Azure Blob Storage connection
blob_service = BlockBlobService(account_name='<your-storage-account-name>', account_key='<your-storage-account-key>')
blob_service.create_container('<your-container-name>', public_access=PublicAccess.Container)

# Set up Azure Video Indexer connection
VI_ENDPOINT = '<your-video-indexer-endpoint>'
VI_ACCOUNT_ID = 'ee302646-e10a-4ecf-ab68-f13a3b17f260'
VI_SUBSCRIPTION_KEY = 'b44f18d021a1400e8c8f3dba40542b2a'
VI_LOCATION = 'East US'
VI_INDEXER_ID = '<your-video-indexer-indexer-id>'

# Define video recording parameters
WIDTH = 640
HEIGHT = 480
FPS = 30

# Define video length in seconds
VIDEO_LENGTH = 10

# Start video recording
filename = 'test_video.mp4'
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer = cv2.VideoWriter(filename, fourcc, FPS, (WIDTH, HEIGHT))
start_time = time.time()
while (time.time() - start_time) < VIDEO_LENGTH:
    ret, frame = video_writer.read()
    if ret:
        video_writer.write(frame)
    else:
        break

# Release video resources
video_writer.release()
video_writer.release()

# Upload video to Azure Blob Storage
blob_name = os.path.basename(filename)
blob_service.create_blob_from_path('<your-container-name>', blob_name, filename)

# Get video URL
blob_url = blob_service.make_blob_url('<your-container-name>', blob_name)

# Define Video Indexer API parameters
vi_params = {
    'name': os.path.splitext(blob_name)[0],
    'privacy': 'private',
    'videoUrl': blob_url,
    'language': 'English',
    'indexingPreset': 'FaceDetection'
}

# Call Video Indexer API to process video and detect faces
vi_headers = {
    'Ocp-Apim-Subscription-Key': VI_SUBSCRIPTION_KEY,
    'Content-Type': 'multipart/form-data'
}
vi_response = requests.post(f'{VI_ENDPOINT}/{VI_LOCATION}/Accounts/{VI_ACCOUNT_ID}/Videos?indexingPreset={VI_INDEXER_ID}', headers=vi_headers, params=vi_params)

print(vi_response.text)
