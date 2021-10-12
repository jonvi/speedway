import requests
from bs4 import BeautifulSoup
import time

def downloadPage(url, outputPath):
    r = requests.get(url, allow_redirects=True, headers={'User-Agent': 'Mozilla/5.0'})
    open(outputPath, 'wb').write(r.content)

def downloadRange(urlPrefix, year, startId, endId):
    element, tag, value = ('span', 'id', 'ctl00_Body_ucCompetitionHeader_lHeader')
    for gameId in range(startId, endId+1):
        url = urlPrefix + str(gameId)
        outputPath = 'games/{}/{}.html'.format(year, gameId)
        r = requests.get(url, allow_redirects=True, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(r.text, features="html.parser")
        title = soup.find(element, {tag: value}).getText()
        print(title)
        if 'Elitserien' in title or 'BAUHAUS Ligan 2021' in title:
            print("\tWriting game {} to file...".format(gameId))
            open(outputPath, 'wb').write(r.content)
        else:
            print("\tGame {} is not the right league. Omitting...".format(gameId))
        time.sleep(60)


if __name__ == '__main__':
    url = 'https://ta.svemo.se/Public/Pages/Competition/DrivingSchedule/CompetitionHeatSchema.aspx?Branch=Speedway&Season=2019&Serie=Elitserien&Resultfilter=APPROVED&Columns=FromDateShort,Name,HeatSchema,HeatResult&pagesize=100%%E2%%80%%9D&CompetitionId=10354'
    urlPrefix = 'https://ta.svemo.se/Public/Pages/Competition/DrivingSchedule/CompetitionHeatSchema.aspx?Branch=Speedway&Season=2019&Serie=Elitserien&Resultfilter=APPROVED&Columns=FromDateShort,Name,HeatSchema,HeatResult&pagesize=100%%E2%%80%%9D&CompetitionId='
    urlPrefixRecent = 'https://ta.svemo.se/Public/Pages/Competition/DrivingSchedule/CompetitionHeatSchema.aspx?Branch=speedway&Season=2021&Resultfilter=APPROVED&Columns=FromDateShort,Name,HeatSchema,HeatResult&pagesize=20&CompetitionId='
    #downloadPage(url, 'games/10354.html')
    #downloadRange(urlPrefix, 10282, 10353)
    #downloadRange(urlPrefix, 10762, 10772)
    # downloadRange(urlPrefixRecent, 2021, 12454, 13179) # 2021 regular season
    downloadRange(urlPrefixRecent, 2021, 13171, 13180) # 2021 Playoff season
