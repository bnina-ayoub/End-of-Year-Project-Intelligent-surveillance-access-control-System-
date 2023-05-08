import requests
import json
import time

# Set API endpoint, account ID, and location
api_url = "https://api.videoindexer.ai"
account_id = "7dc5099e-dd44-45c4-b1b5-e47d53609bcc"
location = "eastus"  # Replace with the account's location, or with “trial” if this is a trial account
api_key = "b44f18d021a1400e8c8f3dba40542b2a"

# Create the http client
session = requests.Session()
session.headers.update({'Ocp-Apim-Subscription-Key': api_key})

# Obtain account access token
account_access_token_request_url = f"{api_url}/auth/{location}/Accounts/{account_id}/AccessToken?allowEdit=true"
account_access_token_request_result = session.get(account_access_token_request_url)
account_access_token = account_access_token_request_result.json()

session.headers.pop('Ocp-Apim-Subscription-Key', None)

# Upload a video
video_url = "https://pfarepository.blob.core.windows.net/faces/basicvideo.mp4"  # Replace with the video URL
upload_url = f"{api_url}/{location}/Accounts/{account_id}/Videos?accessToken={account_access_token}&name=some_name&description=some_description&privacy=private&partition=some_partition&videoUrl={video_url}"
upload_request_result = session.post(upload_url)
upload_result = upload_request_result.json()

# Get the video ID from the upload result
print(upload_result)
video_id = upload_result["id"]

# Obtain video access token
session.headers.update({'Ocp-Apim-Subscription-Key': api_key})
video_access_token_request_url = f"{api_url}/auth/{location}/Accounts/{account_id}/Videos/{video_id}/AccessToken?allowEdit=true"
video_access_token_request_result = session.get(video_access_token_request_url)
video_access_token = video_access_token_request_result.json()

session.headers.pop('Ocp-Apim-Subscription-Key', None)

# Wait for the video index to finish
while True:
    time.sleep(10)

    video_get_index_request_url = f"{api_url}/{location}/Accounts/{account_id}/Videos/{video_id}/Index?accessToken={video_access_token}&language=English"
    video_get_index_request_result = session.get(video_get_index_request_url)
    video_get_index_result = video_get_index_request_result.json()

    processing_state = video_get_index_result["state"]

    print("\nState:")
    print(processing_state)

    # Job is finished
    if processing_state != "Uploaded" and processing_state != "Processing":
        print("\nFull JSON:")
        print(json.dumps(video_get_index_result))
        break

# Search for the video
search_request_url = f"{api_url}/{location}/Accounts/{account_id}/Videos/Search?accessToken={account_access_token}&id={video_id}"
search_request_result = session.get(search_request_url)
search_result = search_request_result.json()

print("\nSearch:")
print(json.dumps(search_result))

# Get insights widget url
insights_widget_request_url = f"{api_url}/{location}/Accounts/{account_id}/Videos/{video_id}/InsightsWidget?accessToken={video_access_token}&widgetType=Keywords&allowEdit=true"
insights_widget_request_result = session.get(insights_widget_request_url)
insights_widget_link = insights_widget_request_result.headers['location']

print("\nInsights Widget url:")
print(insights_widget_link)

# Get player widget url
player_widget_request_url = f"{api_url}/{location}/Accounts/{account_id}/Videos/{video_id}/PlayerWidget?accessToken={video_access_token}"
player_widget_request_result = session.get(player_widget_request_url)
player_widget_link = player_widget_request_result.headers['location']

print("\nPlayer Widget url:")
print(player_widget_link)
