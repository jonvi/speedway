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
            PRIMARY KEY ( id )
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

def populateDatabase():
    connection = connect_to_db("speedway")
    cursor = connection.cursor(buffered=True)

if __name__ == "__main__":
    createAllTables()



