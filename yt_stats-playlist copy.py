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


class YTstats:

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
        await self._convert_csv_excel()

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
        url = f"https://www.googleapis.com/youtube/v3/playlistItems?playlistId={self.playlistId}&key={self.api_key}&channelId={self.channel_id}&part=snippet"
        d = requests.get(url).json()
        data1 = d['items']

        nextpageToken = d['nextPageToken']
        total_result = d['pageInfo']['totalResults']
        result_per_page = d['pageInfo']['resultsPerPage']
        remaining = total_result // result_per_page
        
        if remaining >= 0:
            total_page = remaining + 1
        else:
            total_page = remaining
         
        for i in range(0, total_page + 1):
            nexturl = url + "&pageToken=" + nextpageToken
            data_per_page = requests.get(nexturl).json()
            nextpageToken = d['nextPageToken']
            data2 = data_per_page['items']
            

        jsonfile = self.playlistId + '.json'
        with open(jsonfile, 'w', encoding="utf-8") as f:
            json.dump(data1 + data2, f, indent=4)
        return jsonfile
    
    async def _convert_csv_excel(self):
        jsonfile = self.playlistId + '-format' '.json'
        csvfile = self.playlistId + '.csv'
        title = ["videoId", "kind", "playlistId","title","channelId","channelTitle","id","liveBroadcastContent","description","videoOwnerChannelTitle","videoOwnerChannelId", "publishedAt"]
        
        with open(jsonfile, 'r', encoding="utf-8") as file:
            file_data = json.load(file)

        data = []
        for item in range(len(file_data)):
            data.append(file_data[item])
    
        # with open(jsonfile, 'w', encoding="utf-8") as outputFile:
            # cw = csv.DictWriter(outputFile, title)
            # cw.writeheader()
            # for i, v in enumerate(data):
        for v in range(len(data)):
            # print(file_data(v))
            file_data[v]["videoId"] = file_data[v]['snippet']['resourceId']['videoId']
            # data[v].pop("kind", None)
            file_data[v]["kind"] = file_data[v]['kind']
            # data[v].pop("playlistId", None)
            file_data[v]["playlistId"] = file_data[v]['snippet']['playlistId']
            # data[v].pop("title", None)
            file_data[v]["title"] = file_data[v]['snippet']['title']
            # data[v].pop("channelId", None)
            
            file_data[v]["channelId"] = file_data[v]['snippet']['channelId']
            # data[v].pop("channelTitle", None)
            file_data[v]["channelTitle"] = file_data[v]['snippet']['channelTitle']
            # data[v].pop("publishedAt", None)
            file_data[v]["publishedAt"] = file_data[v]['snippet']['publishedAt']
            # data[v].pop("videoOwnerChannelTitle", None)
            file_data[v]["videoOwnerChannelTitle"] = file_data[v]['snippet']['videoOwnerChannelTitle']
            # data[v].pop("videoOwnerChannelId", None)
            file_data[v]["videoOwnerChannelId"] = file_data[v]['snippet']['videoOwnerChannelId']
            
            file_data[v]["description"] = str(file_data[v]['snippet']["description"]).replace("\n", r"\N")
            data.append(file_data[v])
                # cw.writerow(data)
        with open(jsonfile, 'w', encoding="utf-8") as outfile:
            json.dump(data, outfile, indent=4)
        
        pdObj = pd.read_json(jsonfile,encoding="utf-8" )
        csvData = pdObj.to_csv(csvfile, index=False, encoding="utf-8")



        # outputfile = self.channel_id + '.xlsx'
        # csv_data = []
        # with open(csvfile, encoding="utf-8") as file_obj:
        #     reader = csv.reader(file_obj)
        #     for row in reader:
        #         csv_data.append(row)
        # workbook = openpyxl.Workbook()
        # sheet = workbook.active
        # for row in csv_data:
        #     sheet.append(row)
        # workbook.save(outputfile)



async def app(api_key, channel_id, playlistId) -> None:
    youtube_channel = YTstats(api_key, channel_id, playlistId)
    await youtube_channel.extract_all()

    


output = asyncio.run(app(sys.argv[1], sys.argv[2], sys.argv[3]))
print(output)
