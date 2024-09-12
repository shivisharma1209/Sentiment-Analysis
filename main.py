from googleapiclient.discovery import build
import re 
import emoji
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os
# import matplotlib.pyplot as plt

API_KEY = os.environ['API_KEY']

youtube = build('youtube', 'v3', developerKey=API_KEY)

video_id = input('Enter Youtube Video URL: ')[-11:]
print("video id: " + video_id)

video_response = youtube.videos().list(
    part='snippet',
    id=video_id
).execute()

video_snippet = video_response['items'][0]['snippet']
uploader_channel_id = video_snippet['channelId']
print("channel id: " + uploader_channel_id)

print("Fetching Comments..")
comments = []
nextPageToken = None

while len(comments) < 600:
    request = youtube.commentThreads().list(
        part = 'snippet',
        videoId = video_id,
        maxResults = 100,
        pageToken = nextPageToken
    )
    response = request.execute()
    for item in response['items']:
        comment = item['snippet']['topLevelComment']['snippet']
        if comment['authorChannelId']['value'] != uploader_channel_id:
            comments.append(comment['textDisplay'])
    nextPageToken = response.get('nextPageToken')

    if not nextPageToken:
        break

print(comments[:5])
