import requests

def downloadPage(url, outputPath):
    r = requests.get(url, allow_redirects=True, headers={'User-Agent': 'Mozilla/5.0'})
    open(outputPath, 'wb').write(r.content)


if __name__ == '__main__':
    url = 'https://ta.svemo.se/Public/Pages/Competition/DrivingSchedule/CompetitionHeatSchema.aspx?Branch=Speedway&Season=2019&Serie=Elitserien&Resultfilter=APPROVED&Columns=FromDateShort,Name,HeatSchema,HeatResult&pagesize=100%%E2%%80%%9D&CompetitionId=10328'
    downloadPage(url, 'games')