from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import YoutubeAPI
import json
import requests
from tqdm import tqdm
import asyncio, sys
from subprocess import run, PIPE


import  mimetypes, os


# Create your views here.
def homepage(request):
    return render(request, 'homepage/homepage.html')
       

def get_data(request):
    data = YoutubeAPI.objects.all()
    data = data.values()
    youtube_api = data[0]['api_key'] 
    channel_name = request.POST.get('channel_name')
    # request.session['channel_name'] = channel_name
    url = f'https://www.youtube.com/c/{channel_name}'
    response = requests.get(url)
    if response.status_code == 200:
        out = run([sys.executable, 'G:\\___epikla\\youtube-scrapper-project\\yt_stats.py', youtube_api, channel_name], shell=False, stdout=PIPE)
        request.session['channel_name'] = channel_name
        filename = channel_name +'.csv'
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = BASE_DIR + '/' + filename
        if os.path.isfile(filepath):
            output = "Completed Process. Your file is: " + channel_name +'.csv'
            return render(request, 'homepage/data.html', {'data': output})
        else:
            output = "Quota exceed.It take 24 hour to reset quota. Please try again later. Thanks"
            return render(request, 'homepage/limit.html', {'data': output})
    else:
        output = "Channel name is not correct"
        return render(request, 'homepage/homepage.html', {'data': output}) 
       


def download_file(request):
    data = request.session['channel_name']
    filename = data + '.csv'
    if filename != '':
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = BASE_DIR + '/' + filename
        path = open(filepath, 'rb')
        mime_type, _ = mimetypes.guess_type(filepath)
        response = HttpResponse(path, content_type=mime_type)
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        return response
    else:
        return render(request, 'homepage/homepage.html')
            
    










