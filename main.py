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

# fetch comments
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

comments[:5]

# filter comments
hyperlink_pattern = re.compile(
    r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

threshold_ratio = 0.65
relevant_comments = []

for comment_text in comments:
    comment_text = comment_text.lower().strip()
    emojis = emoji.emoji_count(comment_text)

    text_characters = len(re.sub(r'\s', '', comment_text))

    if (any(char.isalnum() for char in comment_text) and not hyperlink_pattern.search(comment_text)):
        if emojis == 0 or (text_characters / (text_characters + emojis)) > threshold_ratio:
            relevant_comments.append(comment_text)

print(relevant_comments)

# store comments
f = open("ytcomments.txt", 'w', encoding='utf-8')
for idx, comment in enumerate(relevant_comments):
    f.write(str(comment)+"\n")
f.close()
print("Comments Stored Succesfully!")

# analyse comments
def sentiment_scores(comment, polarity):
    sentiment_obj = SentimentIntensityAnalyzer()
    sentiment_dict = sentiment_obj.polarity_scores(comment)
    polarity.append(sentiment_dict['compound'])
    return polarity

polarity = []
positive_comments = []
negative_comments = []
neutral_comments = []

f = open("ytcomments.txt", 'r', encoding='`utf-8')
comments = f.readlines()
f.close()

print("Analysing Comments...")
for index, items in enumerate(comments):
    polarity = sentiment_scores(items, polarity)

    if polarity[-1] > 0.05:
        positive_comments.append(items)
    elif polarity[-1] < 0.05:
        negative_comments.append(items)
    else:
        neutral_comments.append(items)

print(polarity[:8])

# overall polarity
avg_polarity = sum(polarity)/len(polarity)
if avg_polarity > 0.05:
    print("The video has a positive response by the viewers.")
elif avg_polarity < 0.05:
    print("The video has a negative response by the viewers.")
else:
    print("The video has a neutral response by the viewers.")

print("The comment with the most positive sentiment is \"", comments[polarity.index(max(polarity))], "\" with score", max(polarity), "and length", len(comments[polarity.index(max(polarity))]))

print("The comment with most negative sentiment is \"", comments[polarity.index(min(polarity))], "\" with score", min(polarity), "and length", len(comments[polarity.index(min(polarity))]))