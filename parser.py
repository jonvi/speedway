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
    def __init__(self, heatNumber, hoodColor, lane, score, status, homeScore, awayScore):
        self.heatNumber = heatNumber
        self.hoodColor = hoodColor
        self.lane = lane
        self.score = score
        self.status = status
        self.homeScore = homeScore
        self.awayScore = awayScore

    def __str__(self):
        return "Heat: {}     ({}-{})    Hood: {}\tScore: {}\tStatus: {}\tLane: {}".format(self.heatNumber, self.homeScore, self.awayScore, self.hoodColor, self.score, self.status, self.lane)
    
    def __repr__(self):
        return "Heat: {}     ({}-{})    Hood: {}\tScore: {}\tStatus {}\tLane: {}".format(self.heatNumber, self.homeScore, self.awayScore, self.hoodColor, self.score, self.status, self.lane)

    def __lt__(self, other):
         return self.heatNumber < other.heatNumber
  
    def __gt__(self, other):
        return ((self.heatNumber) > (other.heatNumber))
  
    def __le__(self, other):
        return ((self.heatNumber) <= (other.heatNumber))
  
    def __ge__(self, other):
        return ((self.heatNumber) >= (other.heatNumber))
  
    def __eq__(self, other):
        return (self.heatNumber == other.heatNumber)

class DriverResult:
    def __init__(self, driverName, team):
        self.driverName = driverName
        self.team = team
        self.heats = []

    def addHeat(self, driverHeat):
        self.heats.append(driverHeat)
        self.heats = sorted(self.heats) # TODO sort one time only

    def __str__(self):
        return "Driver: {} ({})\n".format(self.driverName, self.team) + "\n".join([heat.__repr__()  for heat in self.heats])

    def __repr__(self):
        return "Driver: {} ({})\n".format(self.driverName, self.team)  + "\n".join([heat.__repr__() for heat in self.heats])

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
    finalWords = ['Kvartsfinal', 'Semifinal', 'Final']
    element, tag, value = elements['title']
    title = soup.find(element, {tag: value}).getText().split(" ")
    roundNumber = int(title[4])

    for word in finalWords:
        if word in title:
            # Multiply round by 100 to identify final games
            roundNumber = roundNumber * 100
            break

    return {
        'date': title[0],
        'league': title[1],
        'year': title[2],
        'roundNumber': roundNumber
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
    leaderRows = soup.findAll(element, {tag: value})
    homeLeader, awayLeader = [leader.findAll('td', {'class': "DriverName"}) for leader in leaderRows]
    return {
        'homeLeader': homeLeader[0].getText().replace("LL: ", ""),
        'awayLeader': awayLeader[0].getText().replace("LL: ", "")
    }

def getHeatScores(soup):
    # TODO: Refactor
    homeScores = []
    homeScoreRows = soup.find('tr', {'id': 'ctl00_Body_ucCompetitionHeatSchema_RadGrid1_ctl00__9'})
    for row in homeScoreRows:
        rowString = str(row.getText())
        if rowString and rowString.isdigit():
            homeScores.append(int(rowString))

    awayScores = []
    awayScoreRows = soup.find('tr', {'id': 'ctl00_Body_ucCompetitionHeatSchema_RadGrid1_ctl00__19'})
    for row in awayScoreRows:
        rowString = str(row.getText())
        if rowString and rowString.isdigit():
            awayScores.append(int(rowString))

    if(len(homeScores) != len(awayScores)):
        print("ERROR: heat score mismatch!")
        return "ERROR"

    return homeScores, awayScores

def getTeamCaptains(soup):
    element, tag, value = elements['captain']
    captainRows = soup.findAll(element, {tag: value})
    homeCaptain, awayCaptain = [captain.findAll('td', {'class': "DriverName"}) for captain in captainRows]

    homeCaptain = homeCaptain[0].getText().replace("LK: ", "")
    awayCaptain = awayCaptain[0].getText().replace("LK: ", "")

    if homeCaptain == "" or homeCaptain == " ":
        homeCaptain = None

    if awayCaptain == ""  or awayCaptain == "":
        awayCaptain = None

    return {
        'homeCaptain': homeCaptain,
        'awayCaptain': awayCaptain
    }

def getRiderHeatResults(soup, riderNumber, team, homeScores, awayScores):
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
        heatNumber = int(heatNumbers[currentHeatIndex])
        if heatNumber == 16: # Bogus bonus round
            continue
        #print("currentHeatIndex: {}\tHeatNumber: {}\tlen(homeScores): {}".format(currentHeatIndex, heatNumber, len(homeScores)))
        homeScore = homeScores[heatNumber-1]
        awayScore = awayScores[heatNumber-1]
        color = None
        score = None
        status = None
        lane = None
        h = heat.split(" ")

        # Sometimes the hood color is in other position
        if h[0] in hoodColors and h[2].isnumeric():
            color = h[0]
            lane = int(h[2])
            if h[1].isnumeric():
                score = int(h[1])
            else:
                status = h[1]
        elif h[0].isalpha() and h[2].isalpha():
            status = h[0]
            lane = int(h[1])
            color = h[2]
        else:
            color = h[2]
            lane = int(h[1])
            if h[0].isnumeric():
                score = int(h[0])
            else:
                status = h[0]

        heatResult = DriverHeat(heatNumber, color, lane, score, status, homeScore, awayScore)
        driverResult.addHeat(heatResult)

        currentHeatIndex += 1
    return driverResult

def getRidersHeatResults(soup, homeScores, awayScores):
    homeRiderNumbers = [i for i in range(1, 8)]
    awayRiderNumbers = [i for i in range(11, 18)]
    riderNumbers = homeRiderNumbers + awayRiderNumbers
    
    driverResults = []
    for riderNumber in riderNumbers:
        if riderNumber in homeRiderNumbers:
            driverResult = getRiderHeatResults(soup, riderNumber, "HOME", homeScores, awayScores)
        else:
            driverResult = getRiderHeatResults(soup, riderNumber, "AWAY", homeScores, awayScores)
        driverResults.append(driverResult)
    
    return driverResults


def parseResult(soup, gameId):
    print("\tLooking at game: {}".format(gameId))
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
    homeScores, awayScores = getHeatScores(soup)
    #print(gameId)
    #for i in range(len(homeScores)):
    #    print(homeScores[i],'-', awayScores[i])
    driverResults = getRidersHeatResults(soup, homeScores, awayScores)
    game.addDriverResults(driverResults)
    return game


    


if __name__ == '__main__':
    gameId = 10329
    path = 'games/{}.html'.format(gameId)
    soup = readFile(path)
    #getHeatScores(soup)
    res = parseResult(soup, gameId)
    #print(res)

    #path = 'games/10329.html'
    #soup = readFile(path)
    #res = parseResult(soup, 10329)
    #print(res)

