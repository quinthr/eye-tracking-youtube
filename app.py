from flask import Flask, render_template, request, redirect
from datetime import datetime
from pyyoutube import Api
from googleapiclient.discovery import build
from humanize import naturaltime
import json

app = Flask(__name__)
api = Api(api_key='AIzaSyC8lB66iFy73lpu5jzUCPDjQdnK3J_h3uA')
api_key = 'AIzaSyC8lB66iFy73lpu5jzUCPDjQdnK3J_h3uA'
youtube = build('youtube', 'v3', developerKey=api_key)


@app.route('/')
def index():
    video_by_chart = api.get_videos_by_chart(chart="mostPopular", region_code="PH", count=12)
    video_arr = []
    for video in video_by_chart.items:
        video_dict = {}
        video_dict['id'] = video.id
        video_dict['title'] = video.snippet.title
        video_dict['thumbnails'] = video.snippet.thumbnails
        video_dict['date'] = humanizeTime(video.snippet.publishedAt)
        video_dict['views'] = nFormatter(video.statistics.viewCount, 1)
        video_dict['channel'] = video.snippet.channelTitle
        video_dict['channelThumbnail'] = fetchChannelThumbnail(video.snippet.channelId)
        video_arr.append(video_dict)
    return render_template('index.html', error=None, videos=video_arr, nav='Home')

def humanizeTime(date):
    now = datetime.now()
    dt = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
    time_difference = now - dt
    formatted_time = naturaltime(time_difference)
    return  formatted_time

def fetchChannelThumbnail(channelId):
    # Fetch channel thumbnail
    channel_response = youtube.channels().list(
        part='snippet',
        id=channelId
    ).execute()
    channel_thumbnail = channel_response['items'][0]['snippet']['thumbnails']['high']['url']
    return channel_thumbnail

def nFormatter(num, digits):
    lookup = [
        {"value": 1, "symbol": ""},
        {"value": 1e3, "symbol": "k"},
        {"value": 1e6, "symbol": "M"},
        {"value": 1e9, "symbol": "G"},
        {"value": 1e12, "symbol": "T"},
        {"value": 1e15, "symbol": "P"},
        {"value": 1e18, "symbol": "E"}
    ]
    rx = r"\.0+$|(\.[0-9]*[1-9])0+$"
    num = float(num)  # Convert num to float
    item = next((item for item in lookup[::-1] if num >= item["value"]), None)
    if item:
        return f"{num / item['value']:.{digits}f}".rstrip("0").rstrip(".") + item["symbol"]
    else:
        return "0"


@app.route('/watch/<videoId>')
def watch(videoId):
    video_arr = []
    video_dict = {}
    video = api.get_video_by_id(video_id=videoId).items
    video_dict['id'] = videoId
    video_dict['title'] = video[0].snippet.title
    video_dict['thumbnails'] = video[0].snippet.thumbnails
    video_arr.append(video_dict)
    videos = youtube.search().list(
        part='snippet',
        type='video',
        relatedToVideoId=videoId,
        maxResults=3
    ).execute()
    for videoIndex in videos.get('items', []):
        video_dict = {}
        video_dict['id'] = videoIndex['id']['videoId']
        video_dict['title'] = videoIndex['snippet']['title']
        video_dict['thumbnails'] = videoIndex['snippet']['thumbnails']
        video_arr.append(video_dict)
    return render_template('video.html', error=None, videos=video_arr)

@app.route('/watch/category/<categoryName>')
def watchCategory(categoryName):
    youtubeCategories = {
        "Gaming": 20,
        "Sports":17,
        "Science and Technology":28,
        "News and Politics":25,
        "Music":10,
        "Entertainment":24,
        "Film and Animation":1,
    }
    category_id =youtubeCategories.get(categoryName, None)
    if category_id is None:
        return redirect('/')
    try:
        search_response = youtube.videos().list(
            part='snippet',
            videoCategoryId=category_id,
            chart='mostPopular',
            maxResults=12
        ).execute()
    except:
        search_response = youtube.videos().list(
            part='snippet',
            videoCategoryId=category_id,
            maxResults=12,
            chart='mostPopular'
        ).execute()

    video_ids = [item['id'] for item in search_response.get('items', [])]
    videos_response = youtube.videos().list(
        part='statistics',
        id=','.join(video_ids)
    ).execute()
    videos = videos_response['items']
    video_arr = []
    for video in search_response.get('items', []):
        video_dict = {}
        video_dict['id'] = video['id']
        stats = getStatistics(video['id'], videos)
        video_dict['title'] = video['snippet']['title']
        video_dict['thumbnails'] = video['snippet']['thumbnails']
        video_dict['date'] = humanizeTime(video['snippet']['publishedAt'])
        video_dict['views'] = nFormatter(stats['viewCount'], 1)
        video_dict['channel'] = video['snippet']['channelTitle']
        video_dict['channelThumbnail'] = fetchChannelThumbnail(video['snippet']['channelId'])
        video_arr.append(video_dict)
    return render_template('index.html', error=None, videos=video_arr, nav=categoryName)

def getStatistics(videoId,videosDict):
    for video in videosDict:
        if videoId == video['id']:
            return video['statistics']


if __name__ == '__main__':
    app.run(host='localhost', port=8888, debug=True)
