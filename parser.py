from bs4 import BeautifulSoup
import requests
import re

elements = {
    'title': ('span', 'id', 'ctl00_Body_ucCompetitionHeader_lHeader'),
    'abbreviations': ('table', 'border', 0),
    'score': ('div', 'class', 'floatLeft'),
    'attendance': ('div', 'class', 'clearer'),
    'heatSchema': ('div', 'id', 'ctl00_Body_ucCompetitionHeatSchema'),
    'teams': ('tr', 'class', 'rgRow Team'),
    'drivers': ('tr', 'id', 'ctl00_Body_ucCompetitionHeatSchema_RadGrid1_ctl00__[row]'), # contain 'Driver' in class name
    'captain': ('tr', 'id', 'ctl00_Body_ucCompetitionHeatSchema_RadGrid1_ctl00__[row]'), # contain 'TeamCaptain' in class name
    'leader': ('tr', 'id', 'ctl00_Body_ucCompetitionHeatSchema_RadGrid1_ctl00__[row]'), # contain 'TeamLeader' in class name
    'heatTime': ('tr', 'class', 'rgRow HeatTime'), # Might also be rgAltRow
}

def readFile(path):
    with open(path) as fp:
        return BeautifulSoup(fp, features="html.parser")

def getTeamsAndScore(soup):
    element, tag, value = elements['score']
    scoreSoup = soup.find(element, {tag: value})
    homeTeam, homeScore, awayTeam, awayScore = [row.getText() for row in scoreSoup.findAll('h2')]
    return {
        'homeTeam': homeTeam,
        'awayTeam': awayTeam,
        'homeScore': homeScore,
        'awayScore': awayScore
    }

def getAttendance(soup):
    attendance = soup.findAll(text=re.compile('Publik'))[0].split('\xa0')[1]
    return int(attendance)

def getHeatTimes(soup):
    heatTimes = [float(heatTime.getText().replace(",", ".")) for heatTime in soup.findAll("td", {"class": re.compile('HeatTime')})]
    return heatTimes


def parseResult(soup):
    # <span class="text1" id="ctl00_Body_ucCompetitionHeader_lHeader">2019-07-02 Elitserien 2019 Omgång 12 Pir - Vet</span>

    resultDivId = 'ctl00_Body_ucCompetitionHeader'
    return soup.find("div", {"id": resultDivId})


if __name__ == '__main__':
    path = 'games/10328.html'
    soup = readFile(path)
    #res = parseResult(soup)
    #res = getTeamsAndScore(soup)
    #print(res)
    #res = getAttendance(soup)
    res = getHeatTimes(soup)
    print(res)
