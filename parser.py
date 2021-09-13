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
    def __init__(self, heatNumber, hoodColor, lane, score, status):
        self.heatNumber = heatNumber
        self.hoodColor = hoodColor
        self.lane = lane
        self.score = score
        self.status = status

    def __str__(self):
        return "Heat: {}    Hood: {}\tScore: {}\Status: {}\tLane: {}".format(self.heatNumber, self.hoodColor, self.score, self.status, self.lane)
    
    def __repr__(self):
        return "Heat: {}    Hood: {}\tScore: {}\tStatus {}\tLane: {}".format(self.heatNumber, self.hoodColor, self.score, self.status, self.lane)

    def __lt__(self, other):
         return self.heatNumber < other.heatNumber

class DriverResult:
    def __init__(self, driverName, team):
        self.driverName = driverName
        self.team = team
        self.heats = []

    def addHeat(self, driverHeat):
        self.heats.append(driverHeat)

    def __str__(self):
        return "Driver {} ({})\n".format(self.driverName, self.team) + "\n".join([heat.__repr__()  for heat in self.heats])

    def __repr__(self):
        return "Driver {} ({})\n".format(self.driverName, self.team)  + "\n".join([heat.__repr__() for heat in self.heats])

# Game(gameId, gameMetaData['date'], gameMetaData['league'], teamsAndScore['homeTeam'], teamsAndScore['awayTeam'])
class Game:
    def __init__(self, gameId, date, league, year, roundNumber, homeTeam, awayTeam, homeScore, awayScore):
        self.gameId = gameId
        self.date = date
        self.league = league
        self.year = year
        self.roundNumber = roundNumber
        self.homeTeam = homeTeam
        self.awayTeam = awayTeam
        self.attendance = None
        self.homeScore = homeScore
        self.awayScore = awayScore
        self.heatTimes = None
        self.homeCaptain = None
        self.awayCaptain = None
        self.homeLeader = None
        self.awayLeader = None
        self.driverResults = None

    def __repr__(self):
        return "Game {}: {} {} {} Round {} | {} ({}) - {} ({})".format(self.gameId, self.date, self.league, self.year, self.roundNumber, self.homeTeam, self.homeScore, self.awayTeam, self.awayScore) + "\n" + "\n".join([driverResult.__repr__() for driverResult in self.driverResults]) + "\n" + ", ".join([heat.__repr__() for heat in self.heatTimes]) + "\n" + "Home captain: {} | Away captain: {}\n".format(self.homeCaptain, self.awayCaptain) + "Home leader: {} | Away leader: {}".format(self.homeLeader, self.awayLeader)

    def addAttendance(self, attendance):
        self.attendance = int(attendance)

    def addResult(self, homeResult, awayResult):
        self.homeResult = homeResult
        self.awayResult = awayResult

    def addHeatTimes(self, heatTimes):
        self.heatTimes = heatTimes
    
    def addCaptains(self, homeCaptain, awayCaptain):
        self.homeCaptain = homeCaptain
        self.awayCaptain = awayCaptain
    
    def addLeaders(self, homeLeader, awayLeader):
        self.homeLeader = homeLeader
        self.awayLeader = awayLeader

    def addDriverResults(self, driverResults):
        self.driverResults = driverResults

def readFile(path):
    with open(path) as fp:
        return BeautifulSoup(fp, features="html.parser")

def getGameMetaData(soup):
    element, tag, value = elements['title']
    title = soup.find(element, {tag: value}).getText().split(" ")
    return {
        'date': title[0],
        'league': title[1],
        'year': title[2],
        'roundNumber': int(title[4])
    }

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
        'awayLeader': awayLeader
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

def getRiderHeatResults(soup, riderNumber, team):
    hoodColors = ('R', 'B', 'V', 'G')
    riderPrefix = 'ctl00_Body_ucCompetitionHeatSchema_RadGrid1_ctl00__{}'
    riderSoup = soup.find("tr", {"id": riderPrefix.format(riderNumber)})
    driverNames = riderSoup.find("td", {"class": re.compile("DriverName")}).getText().split(" ")
    driver = driverNames[1] + " " + driverNames[2]

    heatSoup = riderSoup.findAll("td", {"class": re.compile('Points|DriverStatus')})

    heatNumbers = []
    for s in heatSoup:
        classNames = ''.join(s['class']).strip(), s.text
        
        heat = re.search('HeatHeat(.*)HoodColor', classNames[0])
        heatNumbers.append(heat.group(1))

    heats = [heatInfo.getText().replace('\xa0', '') .strip().replace('  ', '') for heatInfo in heatSoup]
    
    driverResult = DriverResult(driverName=driver, team=team) # TODO: Fix
    currentHeatIndex = 0
    for heat in heats:
        heatNumber = heatNumbers[currentHeatIndex]
        color = None
        score = None
        status = None
        lane = None
        h = heat.split(" ")

        # Sometimes the hood color is in other position
        if h[0] in hoodColors:
            color = h[0]
            lane = int(h[2])
            if h[1].isnumeric():
                score = int(h[1])
            else:
                status = h[1]
        else:
            color = h[2]
            lane = int(h[1])
            if h[0].isnumeric():
                score = int(h[0])
            else:
                status = h[0]

        heatResult = DriverHeat(heatNumber, color, lane, score, status)
        driverResult.addHeat(heatResult)

        currentHeatIndex += 1
    return driverResult

def getRidersHeatResults(soup):
    homeRiderNumbers = [i for i in range(1, 8)]
    awayRiderNumbers = [i for i in range(11, 18)]
    riderNumbers = homeRiderNumbers + awayRiderNumbers
    
    driverResults = []
    for riderNumber in riderNumbers:
        if riderNumber in homeRiderNumbers:
            driverResult = getRiderHeatResults(soup, riderNumber, "HOME")
        else:
            driverResult = getRiderHeatResults(soup, riderNumber, "AWAY")
        driverResults.append(driverResult)
    
    return driverResults


def parseResult(soup, gameId):
    gameMetaData = getGameMetaData(soup)
    teamsAndScore = getTeamsAndScore(soup)
    # (gameId, date, league, year, roundNumber, homeTeam, awayTeam):
    game = Game(gameId, gameMetaData['date'], gameMetaData['league'], gameMetaData['year'], gameMetaData['roundNumber'], teamsAndScore['homeTeam'], teamsAndScore['awayTeam'], teamsAndScore['homeScore'], teamsAndScore['awayScore'])
    attendance = getAttendance(soup)
    game.addAttendance(attendance)
    teamLeaders = getTeamLeaders(soup)
    game.addLeaders(teamLeaders['homeLeader'], teamLeaders['awayLeader'])
    teamCaptains = getTeamCaptains(soup)
    game.addCaptains(teamCaptains['homeCaptain'], teamCaptains['awayCaptain'])
    heatTimes = getHeatTimes(soup)
    game.addHeatTimes(heatTimes)
    driverResults = getRidersHeatResults(soup)
    game.addDriverResults(driverResults)
    return game


    


if __name__ == '__main__':
    path = 'games/10328.html'
    soup = readFile(path)
    #res = parseResult(soup)
    #res = getTeamsAndScore(soup)
    #print(res)
    #res = getAttendance(soup)
    #res = getRiderHeatResults(soup, riderNumber=1, gameId=10328)
    #print(res)
    #res = getRiderHeatResults(soup, riderNumber=2, gameId=10328)
    #print(res)
    res = parseResult(soup, 10328)
    print(res)