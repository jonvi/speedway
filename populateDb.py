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
    print("\tAppending teams")
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
    print(homeTeamId, awayTeamId, homeLeaderId, awayLeaderId, homeCaptainId, awayCaptainId)
    # print(gameData.year,
    #    gameData.date,
    #    gameData.league,
    #    gameData.roundNumber,
    #    gameData.homeScore,
    #    gameData.awayScore,
    #    gameData.attendance
    #    )

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

def dropTables():
    connection = connect_to_db("speedway")
    cursor = connection.cursor(buffered=True)
    tables = ["heat", "game", "heat_time", "driver_team","driver", "leader", "team"]
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
