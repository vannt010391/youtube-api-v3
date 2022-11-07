from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import YoutubeAPI
import json
import requests
from tqdm import tqdm
import asyncio, sys
from subprocess import run, PIPE
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlparse
from pathlib import PurePosixPath
import validators
from datetime import date, datetime


import  mimetypes, os


# Create your views here.
def homepage(request):
    return render(request, 'homepage/homepage.html')
       

def get_data(request):
    data = YoutubeAPI.objects.all()
    data = data.values()
    youtube_api = data[0]['api_key']
    
    def getPlaylistID(url):
        playlistId = url.split("=")[-1].split("&")[0].split("?")[0]
        return playlistId
        


    ### Get channel_id
    def getChannelIdFromCustomUrl(url):
        if "playlist" in url: 
            playlistId = url.split("=")[-1].split("&")[0].split("?")[0]
            url = f"https://www.googleapis.com/youtube/v3/playlistItems?playlistId={playlistId}&key={youtube_api}&part=snippet"
            d = requests.get(url).json()
            channelId = str(d['items'][0]['snippet']['channelId']).strip()
            print(channelId)
            return channelId
           
        else:
            d = requests.get(url).text
            soup = BeautifulSoup(d, "html.parser")
            try:
                channelId = soup.find("meta", {"itemprop": "channelId", "content": True})["content"].strip()
            except:
                channelId = None
            return channelId
    
    url = request.POST.get('url')

    ### Get all url Log - Colette updated on 07/11/2022
    time1 = datetime.now()
    with open("all-url-log.txt", 'a+', encoding="utf-8") as f1:
        log1 = time1.strftime("%d/%m/%Y %H:%M:%S")+ " " + url
        json.dump(log1, f1, indent = 4)
        f1.write('\n')

    ### Validate url
    result = validators.url(url)
    if result == True:
        response = requests.get(url)
        if response != 200:
            channel_id = getChannelIdFromCustomUrl(url)
            ### Get all url Log - Colette updated on 07/11/2022
            time2 = datetime.now()
            with open("youtubeurl-log.txt", 'a+', encoding="utf-8") as f2:
                log2 = time2.strftime("%d/%m/%Y %H:%M:%S")+ " " + url
                json.dump(log2, f2, indent = 4)
                f2.write('\n')
    
           
    else:
        output = "Your url is not correct"
        return render(request, 'homepage/homepage.html', {'data': output}) 
    
    if channel_id != None:
        if "playlist" in url:
            playlistId = getPlaylistID(url)
            print(playlistId)
            out = run([sys.executable, 'G:\\___epikla\\youtube-scrapper-project\\yt_stats-playlist.py', youtube_api, channel_id, playlistId], shell=False, stdout=PIPE)
            # return render(request, 'homepage/limit.html', {'data': out})
            
            request.session['channel_id'] = channel_id
            filename = playlistId +'.csv'
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            filepath = BASE_DIR + '/' + filename
            request.session['playlistId'] = playlistId
            if os.path.isfile(filepath):
                output = "Completed Process! You can download CSV File and/or Excel File "
                return render(request, 'homepage/playlistdata.html', {'data': output})
            else:
                output = "Quota exceed.It take 24 hour to reset quota. Please try again later. Thanks"
                return render(request, 'homepage/limit.html', {'data': output})
        else:
            out = run([sys.executable, 'G:\\___epikla\\youtube-scrapper-project\\yt_stats.py', youtube_api, channel_id], shell=False, stdout=PIPE)
            request.session['channel_id'] = channel_id
            filename = channel_id +'.csv'
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            filepath = BASE_DIR + '/' + filename
            if os.path.isfile(filepath):
                output = "Completed Process! You can download CSV File and/or Excel File "
                return render(request, 'homepage/data.html', {'data': output})
            else:
                output = "Quota exceed.It take 24 hour to reset quota. Please try again later. Thanks"
                return render(request, 'homepage/limit.html', {'data': output})
    else:
        output = "Your url is not correct"
        return render(request, 'homepage/homepage.html', {'data': output}) 

### for youtube url       
def download_file(request):
    data = request.session['channel_id']
    filename = data + '.csv'

    if filename != '' :
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = BASE_DIR + '/' + filename
        path = open(filepath, 'rb')
        mime_type, _ = mimetypes.guess_type(filepath)
        response = HttpResponse(path, content_type=mime_type)
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        return response
    else:
        return render(request, 'homepage/homepage.html')


def download_excel_file(request):
    
    data = request.session['channel_id']
    filename = data + '.xlsx'

    if filename != '' :
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = BASE_DIR + '/' + filename
        path = open(filepath, 'rb')
        mime_type, _ = mimetypes.guess_type(filepath)
        response = HttpResponse(path, content_type=mime_type)
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        return response
    
    else:
        return render(request, 'homepage/homepage.html')


### for playlist
def playlist_download_file(request):
    playlist = request.session['playlistId']
    filename_playlist = playlist + '.csv'

    if filename_playlist != '' :
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = BASE_DIR + '/' + filename_playlist
        path = open(filepath, 'rb')
        mime_type, _ = mimetypes.guess_type(filepath)
        response = HttpResponse(path, content_type=mime_type)
        response['Content-Disposition'] = "attachment; filename=%s" % filename_playlist
        return response
    
    else:
        return render(request, 'homepage/homepage.html')


def playlist_download_excel_file(request):

    playlist = request.session['playlistId']
    filename_playlist = playlist + '.xlsx'
   
    if filename_playlist != '':
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = BASE_DIR + '/' + filename_playlist
        path = open(filepath, 'rb')
        mime_type, _ = mimetypes.guess_type(filepath)
        response = HttpResponse(path, content_type=mime_type)
        response['Content-Disposition'] = "attachment; filename=%s" % filename_playlist
        return response
    else:
        return render(request, 'homepage/homepage.html')
    
            
    










