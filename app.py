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
    video_by_chart = api.get_videos_by_chart(chart="mostPopular", region_code="PH", count=6)
    print(video_by_chart.nextPageToken)
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
    return render_template('index.html', error=None, videos=video_arr, nav='Home', pageToken=video_by_chart.nextPageToken)

@app.route('/next/<pageToken>/2')
def nextPage(pageToken):
    video_by_chart = api.get_videos_by_chart(chart="mostPopular", region_code="PH", count=6, page_token=pageToken)
    print(video_by_chart.nextPageToken)
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

def getSVG(category):
    youtubeCategories = {
        "Gaming": "<svg class='style-scope yt-icon' focusable='false' preserveAspectRatio='xMidYMid meet' style='pointer-events: none; display: block; width: 100%; height: 100%;' viewBox='0 0 24 24'><g class='style-scope yt-icon' fill-rule='evenodd'><path class='style-scope yt-icon' d='M22,13V8l-5-3l-5,3l0,0L7,5L2,8v5l10,6L22,13z M9,11H7v2H6v-2H4v-1h2V8h1v2h2V11z M15,13 c-0.55,0-1-0.45-1-1s0.45-1,1-1s1,0.45,1,1S15.55,13,15,13z M18,11c-0.55,0-1-0.45-1-1s0.45-1,1-1s1,0.45,1,1S18.55,11,18,11z'></path></g></svg>",
        "ScienceAndTechnology": "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 448 512'><!--! Font Awesome Pro 6.4.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path d='M288 0H160 128C110.3 0 96 14.3 96 32s14.3 32 32 32V196.8c0 11.8-3.3 23.5-9.5 33.5L10.3 406.2C3.6 417.2 0 429.7 0 442.6C0 480.9 31.1 512 69.4 512H378.6c38.3 0 69.4-31.1 69.4-69.4c0-12.8-3.6-25.4-10.3-36.4L329.5 230.4c-6.2-10.1-9.5-21.7-9.5-33.5V64c17.7 0 32-14.3 32-32s-14.3-32-32-32H288zM192 196.8V64h64V196.8c0 23.7 6.6 46.9 19 67.1L309.5 320h-171L173 263.9c12.4-20.2 19-43.4 19-67.1z'/></svg>",
        "NewsAndPolitics": "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><path d='M0 96C0 60.7 28.7 32 64 32H448c35.3 0 64 28.7 64 64V416c0 35.3-28.7 64-64 64H64c-35.3 0-64-28.7-64-64V96zM48 368v32c0 8.8 7.2 16 16 16H96c8.8 0 16-7.2 16-16V368c0-8.8-7.2-16-16-16H64c-8.8 0-16 7.2-16 16zm368-16c-8.8 0-16 7.2-16 16v32c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16V368c0-8.8-7.2-16-16-16H416zM48 240v32c0 8.8 7.2 16 16 16H96c8.8 0 16-7.2 16-16V240c0-8.8-7.2-16-16-16H64c-8.8 0-16 7.2-16 16zm368-16c-8.8 0-16 7.2-16 16v32c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16V240c0-8.8-7.2-16-16-16H416zM48 112v32c0 8.8 7.2 16 16 16H96c8.8 0 16-7.2 16-16V112c0-8.8-7.2-16-16-16H64c-8.8 0-16 7.2-16 16zM416 96c-8.8 0-16 7.2-16 16v32c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16V112c0-8.8-7.2-16-16-16H416zM160 128v64c0 17.7 14.3 32 32 32H320c17.7 0 32-14.3 32-32V128c0-17.7-14.3-32-32-32H192c-17.7 0-32 14.3-32 32zm32 160c-17.7 0-32 14.3-32 32v64c0 17.7 14.3 32 32 32H320c17.7 0 32-14.3 32-32V320c0-17.7-14.3-32-32-32H192z'/></svg>",
        "Sports": "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><path d='M417.3 360.1l-71.6-4.8c-5.2-.3-10.3 1.1-14.5 4.2s-7.2 7.4-8.4 12.5l-17.6 69.6C289.5 445.8 273 448 256 448s-33.5-2.2-49.2-6.4L189.2 372c-1.3-5-4.3-9.4-8.4-12.5s-9.3-4.5-14.5-4.2l-71.6 4.8c-17.6-27.2-28.5-59.2-30.4-93.6L125 228.3c4.4-2.8 7.6-7 9.2-11.9s1.4-10.2-.5-15l-26.7-66.6C128 109.2 155.3 89 186.7 76.9l55.2 46c4 3.3 9 5.1 14.1 5.1s10.2-1.8 14.1-5.1l55.2-46c31.3 12.1 58.7 32.3 79.6 57.9l-26.7 66.6c-1.9 4.8-2.1 10.1-.5 15s4.9 9.1 9.2 11.9l60.7 38.2c-1.9 34.4-12.8 66.4-30.4 93.6zM256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zm14.1-325.7c-8.4-6.1-19.8-6.1-28.2 0L194 221c-8.4 6.1-11.9 16.9-8.7 26.8l18.3 56.3c3.2 9.9 12.4 16.6 22.8 16.6h59.2c10.4 0 19.6-6.7 22.8-16.6l18.3-56.3c3.2-9.9-.3-20.7-8.7-26.8l-47.9-34.8z'/></svg>",
        "Music": "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><path d='M499.1 6.3c8.1 6 12.9 15.6 12.9 25.7v72V368c0 44.2-43 80-96 80s-96-35.8-96-80s43-80 96-80c11.2 0 22 1.6 32 4.6V147L192 223.8V432c0 44.2-43 80-96 80s-96-35.8-96-80s43-80 96-80c11.2 0 22 1.6 32 4.6V200 128c0-14.1 9.3-26.6 22.8-30.7l320-96c9.7-2.9 20.2-1.1 28.3 5z'/></svg>",
        "Entertainment": "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 640 512'><path d='M74.6 373.2c41.7 36.1 108 82.5 166.1 73.7c6.1-.9 12.1-2.5 18-4.5c-9.2-12.3-17.3-24.4-24.2-35.4c-21.9-35-28.8-75.2-25.9-113.6c-20.6 4.1-39.2 13-54.7 25.4c-6.5 5.2-16.3 1.3-14.8-7c6.4-33.5 33-60.9 68.2-66.3c2.6-.4 5.3-.7 7.9-.8l19.4-131.3c2-13.8 8-32.7 25-45.9C278.2 53.2 310.5 37 363.2 32.2c-.8-.7-1.6-1.4-2.4-2.1C340.6 14.5 288.4-11.5 175.7 5.6S20.5 63 5.7 83.9C0 91.9-.8 102 .6 111.8L24.8 276.1c5.5 37.3 21.5 72.6 49.8 97.2zm87.7-219.6c4.4-3.1 10.8-2 11.8 3.3c.1 .5 .2 1.1 .3 1.6c3.2 21.8-11.6 42-33.1 45.3s-41.5-11.8-44.7-33.5c-.1-.5-.1-1.1-.2-1.6c-.6-5.4 5.2-8.4 10.3-6.7c9 3 18.8 3.9 28.7 2.4s19.1-5.3 26.8-10.8zM261.6 390c29.4 46.9 79.5 110.9 137.6 119.7s124.5-37.5 166.1-73.7c28.3-24.5 44.3-59.8 49.8-97.2l24.2-164.3c1.4-9.8 .6-19.9-5.1-27.9c-14.8-20.9-57.3-61.2-170-78.3S299.4 77.2 279.2 92.8c-7.8 6-11.5 15.4-12.9 25.2L242.1 282.3c-5.5 37.3-.4 75.8 19.6 107.7zM404.5 235.3c-7.7-5.5-16.8-9.3-26.8-10.8s-19.8-.6-28.7 2.4c-5.1 1.7-10.9-1.3-10.3-6.7c.1-.5 .1-1.1 .2-1.6c3.2-21.8 23.2-36.8 44.7-33.5s36.3 23.5 33.1 45.3c-.1 .5-.2 1.1-.3 1.6c-1 5.3-7.4 6.4-11.8 3.3zm136.2 15.5c-1 5.3-7.4 6.4-11.8 3.3c-7.7-5.5-16.8-9.3-26.8-10.8s-19.8-.6-28.7 2.4c-5.1 1.7-10.9-1.3-10.3-6.7c.1-.5 .1-1.1 .2-1.6c3.2-21.8 23.2-36.8 44.7-33.5s36.3 23.5 33.1 45.3c-.1 .5-.2 1.1-.3 1.6zM530 350.2c-19.6 44.7-66.8 72.5-116.8 64.9s-87.1-48.2-93-96.7c-1-8.3 8.9-12.1 15.2-6.7c23.9 20.8 53.6 35.3 87 40.3s66.1 .1 94.9-12.8c7.6-3.4 16 3.2 12.6 10.9z'/></svg>",
        "FilmAndAnimation": "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><path d='M0 96C0 60.7 28.7 32 64 32H448c35.3 0 64 28.7 64 64V416c0 35.3-28.7 64-64 64H64c-35.3 0-64-28.7-64-64V96zM48 368v32c0 8.8 7.2 16 16 16H96c8.8 0 16-7.2 16-16V368c0-8.8-7.2-16-16-16H64c-8.8 0-16 7.2-16 16zm368-16c-8.8 0-16 7.2-16 16v32c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16V368c0-8.8-7.2-16-16-16H416zM48 240v32c0 8.8 7.2 16 16 16H96c8.8 0 16-7.2 16-16V240c0-8.8-7.2-16-16-16H64c-8.8 0-16 7.2-16 16zm368-16c-8.8 0-16 7.2-16 16v32c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16V240c0-8.8-7.2-16-16-16H416zM48 112v32c0 8.8 7.2 16 16 16H96c8.8 0 16-7.2 16-16V112c0-8.8-7.2-16-16-16H64c-8.8 0-16 7.2-16 16zM416 96c-8.8 0-16 7.2-16 16v32c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16V112c0-8.8-7.2-16-16-16H416zM160 128v64c0 17.7 14.3 32 32 32H320c17.7 0 32-14.3 32-32V128c0-17.7-14.3-32-32-32H192c-17.7 0-32 14.3-32 32zm32 160c-17.7 0-32 14.3-32 32v64c0 17.7 14.3 32 32 32H320c17.7 0 32-14.3 32-32V320c0-17.7-14.3-32-32-32H192z'/></svg>",
    }
    return youtubeCategories[category]

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

@app.route('/watch/category')
def categories():
    return render_template('categories.html', error=None)

@app.route('/watch/category/<categoryName>')
def watchCategory(categoryName):
    youtubeCategories = {
        "Gaming": 20,
        "Sports":17,
        "ScienceAndTechnology":28,
        "NewsAndPolitics":25,
        "Music":10,
        "Entertainment":24,
        "FilmAndAnimation":1,
    }
    category_id =youtubeCategories.get(categoryName, None)
    svg = getSVG(categoryName)
    nav = categoryName
    if nav == 'ScienceAndTechnology':
        nav = 'Science & Technology'
    elif nav == "NewsAndPolitics":
        nav = 'News & Politics'
    elif nav == 'FilmAndAnimation':
        nav = 'Film & Animation'
    if category_id is None:
        return redirect('/')
    try:
        search_response = youtube.videos().list(
            part='snippet',
            videoCategoryId=category_id,
            chart='mostPopular',
            maxResults=6
        ).execute()
    except:
        search_response = youtube.videos().list(
            part='snippet',
            videoCategoryId=category_id,
            maxResults=6,
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
    return render_template('category.html', error=None, videos=video_arr, svg=svg, categoryName=categoryName, pageToken=search_response['nextPageToken'], nav=nav)

@app.route('/watch/category/<categoryName>/<pageToken>/2')
def watchCategoryPage(categoryName, pageToken):
    youtubeCategories = {
        "Gaming": 20,
        "Sports":17,
        "ScienceAndTechnology":28,
        "NewsAndPolitics":25,
        "Music":10,
        "Entertainment":24,
        "FilmAndAnimation":1,
    }

    category_id =youtubeCategories.get(categoryName, None)
    svg = getSVG(categoryName)
    nav = categoryName
    if nav =='ScienceAndTechnology':
        nav = 'Science & Technology'
    elif nav=="NewsAndPolitics":
        nav = 'News & Politics'
    elif nav=='FilmAndAnimation':
        nav = 'Film & Animation'
    if category_id is None:
        return redirect('/')
    try:
        search_response = youtube.videos().list(
            part='snippet',
            videoCategoryId=category_id,
            chart='mostPopular',
            maxResults=6,
            pageToken=pageToken
        ).execute()
    except:
        search_response = youtube.videos().list(
            part='snippet',
            videoCategoryId=category_id,
            maxResults=6,
            chart='mostPopular',
            pageToken=pageToken
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
    return render_template('category.html', error=None, videos=video_arr, svg=svg, categoryName=categoryName, nav=nav)

def getStatistics(videoId,videosDict):
    for video in videosDict:
        if videoId == video['id']:
            return video['statistics']


if __name__ == '__main__':
    app.run(host='localhost', port=8888, debug=True)
