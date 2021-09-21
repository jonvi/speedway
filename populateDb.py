import mysql.connector
from mysql.connector import Error
from sqlalchemy import create_engine
import pandas as pd
import parser
import createDb
from os import listdir
from os.path import isfile, join

def connect_to_db(database):
    try:
        connection = mysql.connector.connect(host='localhost',
                                            database=database,
                                            user='root',
                                            password='password')

        if connection.is_connected():
            db_Info = connection.get_server_info()
            print("Connected to MySQL Server version ", db_Info)
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            print("You're connected to database: ", record)
            return connection
        else:
            print("Could not connect to database")

    except Error as e:
        print("Error while connecting to MySQL", e)

def create_connection(database):
    db_connection_str = 'mysql+pymysql://root:password@localhost/' + database
    connection = create_engine(db_connection_str)
    return connection

def populateTeams():
    connection = create_connection("speedway")
    teamData = [["Dackarna", "Målilla"],
    ["Indianerna", "Kumla"],
    ["Lejonen", "Gislaved"],
    ["Kumla Indianerna Speedway", "Kumla"],
    ["Masarna", "Avesta"],
    ["Piraterna", "Motala"],
    ["Rospiggarna", "Hallstavik"],
    ["Eskilstuna Smederna", "Eskilstuna"],
    ["Västervik Speedway", "Västervik"],
    ["Vetlanda Speedway", "Vetlanda"]]

    df = pd.DataFrame(teamData, columns = ['name', 'city'])
    df.to_sql('team', connection, if_exists='append', index=False)

def getGameFilePaths():
    directory = "games"
    gameFiles = [directory + "/" + f for f in listdir(directory) if isfile(join(directory, f))]
    return sorted(gameFiles)

def getTeams(connection):
    df = pd.read_sql('SELECT * FROM team', con=connection)
    return dict(zip(df.name, df.id))


def insertDriver(connection, cursor, name):
    insertQuery = """INSERT IGNORE INTO driver (name)
    VALUES ('{}');""".format(name)
    cursor.execute(insertQuery)
    connection.commit()

    idQuery = """SELECT LAST_INSERT_ID();""".format(name)
    cursor.execute(idQuery)
    return cursor.fetchone()[0]

def insertLeader(connection, cursor, name):
    insertQuery = """INSERT IGNORE INTO leader (name)
    VALUES ('{}');""".format(name)
    cursor.execute(insertQuery)
    connection.commit()

    idQuery = """SELECT LAST_INSERT_ID();""".format(name)
    cursor.execute(idQuery)
    return cursor.fetchone()[0]

def insertCaptain(connection, cursor, name):
    insertQuery = """INSERT IGNORE INTO captain (name)
    VALUES ('{}');""".format(name)
    cursor.execute(insertQuery)
    connection.commit()

    idQuery = """SELECT LAST_INSERT_ID();""".format(name)
    cursor.execute(idQuery)
    return cursor.fetchone()[0]

def insertGameMetaData(connection, cursor, gameData, homeTeamId, awayTeamId, homeLeaderId, awayLeaderId, homeCaptainId, awayCaptainId):
    if homeCaptainId is not None and awayCaptainId is not None:
        insertQuery = """INSERT INTO game (id, year, date, league, roundNumber, homeTeamId, awayTeamId, 
        homeScore, awayScore, homeCaptainId, awayCaptainId, homeLeaderId, awayLeaderId, attendance)
        VALUES ({13}, {0}, '{1}', '{2}', {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12});""".format(
            gameData.year,
            gameData.date,
            gameData.league,
            gameData.roundNumber,
            homeTeamId,
            awayTeamId,
            gameData.homeScore,
            gameData.awayScore,
            homeCaptainId,
            awayCaptainId,
            homeLeaderId,
            awayLeaderId,
            gameData.attendance,
            gameData.gameId)
    elif homeCaptainId is None and awayCaptainId is not None:
        insertQuery = """INSERT INTO game (id, year, date, league, roundNumber, homeTeamId, awayTeamId, 
        homeScore, awayScore, awayCaptainId, homeLeaderId, awayLeaderId, attendance)
        VALUES ({12}, {0}, '{1}', '{2}', {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11});""".format(
            gameData.year,
            gameData.date,
            gameData.league,
            gameData.roundNumber,
            homeTeamId,
            awayTeamId,
            gameData.homeScore,
            gameData.awayScore,
            awayCaptainId,
            homeLeaderId,
            awayLeaderId,
            gameData.attendance,
            gameData.gameId)
    elif awayCaptainId is None and homeCaptainId is not None:
        insertQuery = """INSERT INTO game (id, year, date, league, roundNumber, homeTeamId, awayTeamId, 
        homeScore, awayScore, homeCaptainId, homeLeaderId, awayLeaderId, attendance)
        VALUES ({12}, {0}, '{1}', '{2}', {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11});""".format(
            gameData.year,
            gameData.date,
            gameData.league,
            gameData.roundNumber,
            homeTeamId,
            awayTeamId,
            gameData.homeScore,
            gameData.awayScore,
            homeCaptainId,
            homeLeaderId,
            awayLeaderId,
            gameData.attendance,
            gameData.gameId)
    cursor.execute(insertQuery)
    connection.commit()

def insertHeatData(connection, cursor, gameId, heatNumber, driverId, teamId, points, status, lane, hood):
    if points is None:
         insertQuery = """INSERT INTO heat (gameId, heatNumber, driverId, teamId, status, points, lane, hood)
            VALUES ({0}, {1}, {2}, {3}, '{4}', NULL, {5}, '{6}');""".format(
                gameId, heatNumber, driverId, teamId, status, lane, hood)
    elif status is None:
        insertQuery = """INSERT INTO heat (gameId, heatNumber, driverId, teamId, points, lane, hood)
            VALUES ({0}, {1}, {2}, {3}, {4}, {5}, '{6}');""".format(
                gameId, heatNumber, driverId, teamId, points, lane, hood)
    else:
        insertQuery = """INSERT INTO heat (gameId, heatNumber, driverId, teamId, status, points, lane, hood)
            VALUES ({0}, {1}, {2}, {3}, {4}, '{5}', {6}, '{7}');""".format(
                gameId, heatNumber, driverId, teamId, points, lane, hood)
    cursor.execute(insertQuery)
    connection.commit()

def populateHeats(connection, cursor, gameData, homeTeamId, awayTeamId, drivers):
    driverResults = gameData.driverResults
    for driverResult in driverResults:

        if driverResult.driverName not in drivers:
            driverId = insertDriver(connection, cursor, driverResult.driverName)
            drivers[driverResult.driverName] = driverId
        else:
            driverId = drivers[driverResult.driverName]

        if driverResult.team == "HOME":
            teamId = homeTeamId
        if driverResult.team == "AWAY":
            teamId = awayTeamId
        
        for heat in driverResult.heats:
            insertHeatData(connection, cursor, gameData.gameId, heat.heatNumber, driverId, teamId, heat.score, heat.status, heat.lane, heat.hoodColor)

def populateBestHeat(connection, cursor, gameId, heatTimes):
    query = """SELECT id, gameId, points FROM heat WHERE points = 3 AND GameId = {} ORDER BY heatNumber;""".format(gameId)
    cursor.execute(query)
    res = cursor.fetchall()

    if(len(res) != len(heatTimes)):
        print("~~~~HEAT TIME MISMATCH!!!~~~~, {} != {}", len(res), len(heatTime))

    for i in range(len(res)):
        heatId, gameId, points = res[i]
        heatTime = heatTimes[i]
        insertQuery = """INSERT INTO heat_time (heatId, heatTime) VALUES ({0}, {1})""".format(heatId, heatTime)
        cursor.execute(insertQuery)
    connection.commit()
    

def populateHeatTimes(connection, cursor, gameData):
    pass

def populateDb():
    alc_connection = create_connection("speedway")
    connection = connect_to_db("speedway")
    cursor = connection.cursor(buffered=True)

    gamePaths = getGameFilePaths()
    directory = "games/"
    suffix = ".html"

    drivers = {}
    leaders = {}
    teams = getTeams(alc_connection)

    for gamePath in gamePaths:
        gameId = gamePath.replace(directory, "").replace(suffix, "")
        soup = parser.readFile(gamePath)
        gameData = parser.parseResult(soup, gameId)

        homeLeaderId = None
        if gameData.homeLeader not in leaders:
            homeLeaderId = insertLeader(connection, cursor, gameData.homeLeader)
            leaders[gameData.homeLeader] = homeLeaderId
        else:
            homeLeaderId = leaders[gameData.homeLeader]

        awayLeaderId = None
        if gameData.awayLeader not in leaders:
            awayLeaderId = insertLeader(connection, cursor, gameData.awayLeader)
            leaders[gameData.awayLeader] = awayLeaderId
        else:
            awayLeaderId = leaders[gameData.awayLeader]
        

        homeCaptainId = None
        if gameData.homeCaptain is not None and gameData.homeCaptain not in drivers:
            homeCaptainId = insertDriver(connection, cursor, gameData.homeCaptain)
            drivers[gameData.homeCaptain] = homeCaptainId
        elif gameData.homeCaptain is not None:
            homeCaptainId = drivers[gameData.homeCaptain]


        awayCaptainId = None
        if gameData.awayCaptain is not None and gameData.awayCaptain not in drivers:
            awayCaptainId = insertDriver(connection, cursor, gameData.awayCaptain)
            drivers[gameData.awayCaptain] = awayCaptainId
        elif gameData.awayCaptain is not None:
            awayCaptainId = drivers[gameData.awayCaptain]


        homeTeamId = teams[gameData.homeTeam]
        awayTeamId = teams[gameData.awayTeam]

        insertGameMetaData(connection, cursor, gameData, homeTeamId, awayTeamId, homeLeaderId, awayLeaderId, homeCaptainId, awayCaptainId)
        populateHeats(connection, cursor, gameData, homeTeamId, awayTeamId, drivers)
        populateBestHeat(connection, cursor, gameData.gameId, gameData.heatTimes)

    #for gamePath in gamePaths:
    #    gameId = gamePath.replace(directory, "").replace(suffix, "")
    #    soup = parser.readFile(gamePath)
    #    gameData = parser.parseResult(soup, gameId)
    #    print("~~~HEAT GameID {}~~~~~".format(gameId))
    #    populateHeats(connection, cursor, gameData, homeTeamId, awayTeamId, drivers)
    #    populateBestHeat(connection, cursor, gameData.gameId, gameData.heatTimes)




def dropTables():
    connection = connect_to_db("speedway")
    cursor = connection.cursor(buffered=True)
    tables = ["heat", "game", "heat_time", "driver_team","driver", "leader", "team", "gameview", "heatview"]
    for table in tables:
        cursor.execute(""" 
            DROP TABLE IF EXISTS {0}""".format(table))
    connection.commit()




if __name__ == "__main__":
    alc_connection = create_connection("speedway")
    connection = connect_to_db("speedway")
    cursor = connection.cursor(buffered=True)
    #res = insertDriver(connection, cursor, "TEST")
    #print(res)

    # populateTeams()
    # print(populateDb())

    dropTables()
    createDb.createAllTables()
    populateTeams()

    populateDb()
