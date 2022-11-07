from dbm import dumb
from fileinput import filename
import json
import requests
from tqdm import tqdm
import asyncio, sys
import isodate, csv, datetime, os
from bs4 import BeautifulSoup
import pandas as pd
import openpyxl
import csv, re
from googleapiclient.discovery import build
from datetime import timedelta


class YTstats2:

    def __init__(self, api_key, channel_id, playlistId):
        self.api_key = api_key
        self.channel_id = channel_id
        self.playlistId = playlistId
        self.channel_statistics = None
        self.video_data = None

    async def extract_all(self):
        # await self.get_channel_statistics()
        # await self.getVideoData()
        # await self._get_channel_content()
        await self._get_video_info()
        await self._convert_csv()
        await self._convert_excel()

    async def get_channel_statistics(self):
        """Extract the channel statistics"""
        print('get channel statistics...')
        url = f'https://www.googleapis.com/youtube/v3/channels?part=statistics&id={self.channel_id}&key={self.api_key}'
        pbar = tqdm(total=1)
        
        json_url = requests.get(url)
        data = json.loads(json_url.text)
        try:
            data = data['items'][0]['statistics']
        except KeyError:
            print('Could not get channel statistics')
            data = {}

        self.channel_statistics = data
        pbar.update()
        pbar.close()
        print(data)
        return data
    

    async def _get_video_info(self):
        data = []
        jsonfile = self.playlistId + '.json'
        url = f"https://www.googleapis.com/youtube/v3/playlistItems?playlistId={self.playlistId}&key={self.api_key}&channelId={self.channel_id}&part=snippet"
        d = requests.get(url).json()
        data1 = d['items']
        data.append(data1)
        
        nextpageToken = d['nextPageToken']
                 
        while nextpageToken != None:
            nexturl = url + "&pageToken=" + nextpageToken
            data_per_page = requests.get(nexturl).json()
            if 'nextPageToken' in data_per_page:
                nextpageToken = data_per_page['nextPageToken']
            else: nextpageToken = None
            data2 = data_per_page['items']
            data.append(data2)
        with open(jsonfile, 'w', encoding="utf-8") as f:
            json.dump(data, f, indent=4)
            
        
    
    async def _convert_csv(self):
        jsonfile = self.playlistId + '.json'
        csvfile = self.playlistId + '.csv'
       
        with open(jsonfile, 'r', encoding="utf-8") as file:
            file_data = json.load(file)
        
        def Convert(lst):
            res_dct = {}
            count = 0
            for i in range(len(lst)):
                for j in range(len(lst[i])):
                    res_dct[count] = lst[i][j]
                    count += 1
            return res_dct

        data = Convert(file_data)

        title = ["videoId","kind","playlistId","title","channelId","channelTitle","id","description","videoOwnerChannelTitle","videoOwnerChannelId","publishedAt"]
        with open(csvfile, 'w+', encoding="utf-8", newline='') as csvfile:
            cw = csv.DictWriter(csvfile, title)
            cw.writeheader()
            for i, v in enumerate(data):
                data[v]["videoId"] = data[v]["snippet"]["resourceId"]["videoId"]
                data[v]["kind"] = data[v]["kind"]
                data[v]["playlistId"] = data[v]["snippet"]["playlistId"]
                data[v]["title"] = data[v]["snippet"]["title"]
                data[v]["channelId"] = data[v]["snippet"]["channelId"]
                data[v]["channelTitle"] = data[v]["snippet"]["channelTitle"]
                data[v]["id"] = data[v]["id"]
                data[v]["description"] = str(data[v]["snippet"]["description"]).replace("\n", r"\N") 
                # data[v]["videoOwnerChannelTitle"] = data[v]["snippet"]["videoOwnerChannelTitle"]
                # data[v]["videoOwnerChannelId"] = data[v]["snippet"]["videoOwnerChannelId"]
                data[v]["publishedAt"] = data[v]["snippet"]["publishedAt"]
                data[v].pop("snippet", None)
                data[v].pop("etag", None)
                data[v].pop("id", None)
                data[v].pop("videoOwnerChannelTitle", None)
                data[v].pop("videoOwnerChannelId", None)
                cw.writerow(data[v])

    async def _convert_excel(self):
        csvfile = self.playlistId + '.csv'
        outputfile = self.playlistId + '.xlsx'
        csv_data = []
        with open(csvfile, encoding="utf-8") as file_obj:
            reader = csv.reader(file_obj)
            for row in reader:
                csv_data.append(row)
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        for row in csv_data:
            sheet.append(row)
        workbook.save(outputfile)



async def app1(api_key, channel_id, playlistId) -> None:
    youtube_channel = YTstats2(api_key, channel_id, playlistId)
    await youtube_channel.extract_all()

    


output = asyncio.run(app1(sys.argv[1], sys.argv[2], sys.argv[3]))
print(output)
