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
    'captain': ('tr', 'class', 'rgAltRow TeamCaptain'), # contain 'TeamCaptain' in class name
    'leader': ('tr', 'class', 'rgRow TeamLeader'), # contain 'TeamLeader' in class name
    'heatTime': ('tr', 'class', 'rgRow HeatTime'), # Might also be rgAltRow
}

class DriverHeat():
    def __init__(self, heatNumber, hoodColor, lane, score):
        self.heatNumber = heatNumber
        self.hoodColor = hoodColor
        self.lane = lane
        self.score = score

    def __str__(self):
        return "Heat: {}\t\tHood: {}\tScore: {}\tLane: {}".format(self.heatNumber, self.hoodColor, self.score, self.lane)
    
    def __repr__(self):
        return "Heat: {}\t\tHood: {}\tScore: {}\tLane: {}".format(self.heatNumber, self.hoodColor, self.score, self.lane)

class DriverResult:
    def __init__(self, driverName, gameId):
        self.driverName = driverName
        self.gameId = gameId
        self.heats = []

    def addHeat(self, driverHeat):
        self.heats.append(driverHeat)

    def __str__(self):
        return "Game: {}\tDriver {}\n".format(self.gameId, self.driverName) + "\n".join([heat.__repr__()  for heat in self.heats])

    def __repr__(self):
        return "Game: {}\tDriver {}\n".format(self.gameId, self.driverName)  + "\n".join([heat.__repr__() for heat in self.heats])

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

def getTeamLeaders(soup):
    element, tag, value = elements['leader']
    homeLeader, awayLeader = [leader.getText()[5:-18] for leader in soup.findAll(element, {tag: value})]
    return {
        'homeLeader': homeLeader,
        'awayleader': awayLeader
    }

def getTeamCaptains(soup):
    element, tag, value = elements['captain']
    # TODO: Splice may be problem in future
    homeCaptain, awayCaptain = [captain.getText()[5:-20] for captain in soup.findAll(element, {tag: value})]
    homeCaptain = ''.join([i for i in homeCaptain if not i.isdigit()])
    awayCaptain = ''.join([i for i in awayCaptain if not i.isdigit()])
    return {
        'homeCaptain': homeCaptain,
        'awayCaptain': awayCaptain
    }

def getRiderHeatResults(soup, riderNumber, gameId):
    hoodColors = ('R', 'B', 'V', 'G')
    riderPrefix = 'ctl00_Body_ucCompetitionHeatSchema_RadGrid1_ctl00__{}'
    riderSoup = soup.find("tr", {"id": riderPrefix.format(riderNumber)})
    driverNames = riderSoup.find("td", {"class": re.compile("DriverName")}).getText().split(" ")
    driver = driverNames[1] + " " + driverNames[2]

    heatSoup = riderSoup.findAll("td", {"class": re.compile('Points|DriverStatus')})
    print(riderSoup)

    heatNumbers = []
    for s in heatSoup:
        classNames = ''.join(s['class']).strip(), s.text
        
        heat = re.search('HeatHeat(.*)HoodColor', classNames[0])
        heatNumbers.append(heat.group(1))

    heats = [heatInfo.getText().replace('\xa0', '') .strip().replace('  ', '') for heatInfo in heatSoup]
    
    driverResult = DriverResult(gameId=gameId, driverName=driver) # TODO: Fix
    currentHeatIndex = 0
    for heat in heats:
        heatNumber = heatNumbers[currentHeatIndex]
        color = None
        score = None
        lane = None
        h = heat.split(" ")

        # Sometimes the hood color is in other position
        if h[0] in hoodColors:
            color = h[0]
            score = h[1]
            lane = h[2]
        else:
            color = h[2]
            score = h[0]
            lane = h[1]

        heatResult = DriverHeat(heatNumber, color, lane, score)
        driverResult.addHeat(heatResult)

        currentHeatIndex += 1
    return driverResult



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
    res = getRiderHeatResults(soup, riderNumber=1, gameId=10328)
    print(res)
    res = getRiderHeatResults(soup, riderNumber=2, gameId=10328)
    print(res)
