import mysql.connector
from mysql.connector import Error
from sqlalchemy import create_engine

# mysql -u "root" -p

def create_connection(database):
    db_connection_str = 'mysql+pymysql://root:password@localhost/' + database
    connection = create_engine(db_connection_str)
    return connection

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

def createDriverTable(connection, cursor):
    print("Creating driver table...")
    query = """CREATE TABLE driver (
            id INT NOT NULL AUTO_INCREMENT,
            name VARCHAR(250) NOT NULL UNIQUE,
            PRIMARY KEY ( id )
        )"""
    cursor.execute(query)
    connection.commit()

def createLeaderTable(connection, cursor):
    print("Creating leader table...")
    query = """CREATE TABLE leader (
            id INT NOT NULL AUTO_INCREMENT,
            name VARCHAR(250) NOT NULL UNIQUE,
            PRIMARY KEY ( id )
        );"""
    cursor.execute(query)
    connection.commit()

def createTeamTable(connection, cursor):
    print("Creating team table...")
    query = """CREATE TABLE team (
            id INT AUTO_INCREMENT,
            name VARCHAR(250) NOT NULL UNIQUE,
            city VARCHAR(250) NOT NULL,
            PRIMARY KEY ( id )
        );"""
    cursor.execute(query)
    connection.commit()

def createHeatTimeTable(connection, cursor):
    print("Creating heat times table...")
    query = """CREATE TABLE heat_time (
            id INT AUTO_INCREMENT,
            heatId INT,
            heatTime DOUBLE,
            PRIMARY KEY ( id ),
            CONSTRAINT FK_HeatId FOREIGN KEY ( heatId ) REFERENCES heat(id)
        );"""
    cursor.execute(query)
    connection.commit()

def createHeatScoreTable(connection, cursor):
    print("Creating heat scores table...")
    query = """CREATE TABLE heat_score (
            id INT AUTO_INCREMENT,
            heatId INT,
            homeScore INT,
            awayScore INT,
            PRIMARY KEY ( id ),
            CONSTRAINT FK_HeatScoreId FOREIGN KEY ( heatId ) REFERENCES heat(id)
        );"""
    cursor.execute(query)
    connection.commit()

def createDriverTeamTable(connection, cursor):
    print("Creating driverTeam table...")
    query = """CREATE TABLE driver_team (
            driverId INT,
            teamId INT,
            year INT NOT NULL,

            CONSTRAINT FK_driverId FOREIGN KEY ( driverId ) REFERENCES driver(id),
            CONSTRAINT FK_teamId FOREIGN KEY (teamId) REFERENCES team(id)
        );"""
    cursor.execute(query)
    connection.commit()

def createGameTable(connection, cursor):
    print("Creating game table...")
    query = """CREATE TABLE game (
            id INT,
            year INT NOT NULL,
            date DATE,
            league VARCHAR(250),
            roundNumber INT,
            attendance INT,
            homeTeamId INT,
            awayTeamId INT,
            homeScore INT,
            awayScore INT,
            homeCaptainId INT,
            awayCaptainId INT,
            homeLeaderId INT,
            awayLeaderId INT,

            PRIMARY KEY ( id ),
            CONSTRAINT FK_homeTeamId FOREIGN KEY ( homeTeamId ) REFERENCES team(id),
            CONSTRAINT FK_awayTeamId FOREIGN KEY ( awayTeamId ) REFERENCES team(id),
            CONSTRAINT FK_homeCaptainId FOREIGN KEY ( homeCaptainId ) REFERENCES driver(id),
            CONSTRAINT FK_awayCaptainId FOREIGN KEY ( awayCaptainId ) REFERENCES driver(id),
            CONSTRAINT FK_homeLeaderId FOREIGN KEY ( homeLeaderId ) REFERENCES leader(id),
            CONSTRAINT FK_awayLeaderId FOREIGN KEY ( awayLeaderId ) REFERENCES leader(id)
        );"""
    cursor.execute(query)
    connection.commit()

def createHeatTable(connection, cursor):
    print("Creating heat table...")
    query = """CREATE TABLE heat (
            id INT AUTO_INCREMENT,
            gameId INT,
            heatNumber INT NOT NULL,
            driverId INT,
            teamId INT,
            points INT,
            status VARCHAR(3),
            lane INT NOT NULL,
            hood VARCHAR(1) NOT NULL,

            PRIMARY KEY ( id ),
            CONSTRAINT FK_gameId FOREIGN KEY ( gameId ) REFERENCES game(id),
            CONSTRAINT FK_heatDriverId FOREIGN KEY ( driverId ) REFERENCES driver(id),
            CONSTRAINT FK_heatTeamId FOREIGN KEY ( teamId ) REFERENCES team(id),
            CONSTRAINT UC_heat UNIQUE ( gameId, heatNumber, driverId)
        );"""
    cursor.execute(query)
    connection.commit()

def createGameView():
    connection = connect_to_db("speedway")
    cursor = connection.cursor(buffered=True)
    print("Creating game view...")
    query = """CREATE view gameView AS
        SELECT g.id,
            g.year,
            g.date,
            g.league,
            g.roundNumber,
            ht.city,
            g.attendance,
            ht.name homeTeam,
            g.homeScore,
            at.name awayTeam,
            g.awayScore
        FROM game g
        INNER JOIN team ht
            ON ht.id = g.homeTeamId
        INNER JOIN team at
            ON at.id = g.awayTeamId
        ORDER BY g.id
        ;"""
    cursor.execute(query)
    connection.commit()

def createHeatView():
    connection = connect_to_db("speedway")
    cursor = connection.cursor(buffered=True)
    print("Creating game view...")
    query = """CREATE view heatView AS
        SELECT h.id,
        g.year,
        h.gameId,
        h.heatNumber,
        d.name driver,
        t.name team,
        IF(h.teamId = g.homeTeamId, 'HOME', 'AWAY') AS arena,
        hs.homeScore,
        hs.awayScore,
        h.points,
        h.status,
        h.lane,
        h.hood,
        IF(h.points = 3, bht.heatTime, NULL) AS heatTime

        FROM heat h
        INNER JOIN driver d
            ON d.id = h.driverId
        INNER JOIN team t
            ON t.id = h.teamId
        INNER JOIN game g
            ON g.id = h.gameId
        INNER JOIN heat_score hs
            ON hs.heatId = h.id
        LEFT JOIN heat_time bht
            ON bht.heatId = h.id

        ORDER BY gameId, heatNumber, arena
        ;"""
    cursor.execute(query)
    connection.commit()

def createTwoHeatView():
    connection = connect_to_db("speedway")
    cursor = connection.cursor(buffered=True)
    print("Creating two heat view...")
    query = """CREATE view twoHeatView AS
        SELECT gv.id,
            gv.year,
            gv.date,
            gv.homeTeam,
            gv.awayTeam,
            gv.homeScore,
            gv.awayScore,
            hv.homeScore AS homeHeatScore,
            hv.awayScore AS awayHeatScore,
            IF(
                (
                    (gv.homeScore > gv.awayScore) AND (hv.homeScore > hv.awayScore)
                ) OR (
                    (gv.homeScore < gv.awayScore) AND (hv.homeScore < hv.awayScore)
                ) OR (
                    (gv.homeScore = gv.awayScore) AND (hv.homeScore = hv.awayScore)
                ), 1, 0
            ) AS sameAsSecondHeat
        FROM gameview gv
        INNER JOIN heatview hv
            ON gv.id = hv.gameId AND hv.heatNumber = 2
        GROUP BY 
            gv.id,
            gv.year,
            gv.date,
            gv.homeTeam,
            gv.awayTeam,
            gv.homeScore,
            gv.awayScore,
            hv.gameId,
            hv.heatNumber,
            hv.homeScore,
            hv.awayScore
        ORDER BY
            gv.id;"""
    cursor.execute(query)
    connection.commit()


def createAllTables():
    connection = connect_to_db("speedway")
    cursor = connection.cursor(buffered=True)

    createDriverTable(connection, cursor)
    createLeaderTable(connection, cursor)
    createTeamTable(connection, cursor)
    createDriverTeamTable(connection, cursor)
    createGameTable(connection, cursor)
    createHeatTable(connection, cursor)
    createHeatTimeTable(connection, cursor)
    createHeatScoreTable(connection, cursor)
    createGameView()
    createHeatView()

def populateDatabase():
    connection = connect_to_db("speedway")
    cursor = connection.cursor(buffered=True)

if __name__ == "__main__":
    # createAllTables()
    # createMasterView()
    createTwoHeatView()



