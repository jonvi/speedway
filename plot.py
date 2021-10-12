import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
sns.set_style("white")

def create_connection(database):
    db_connection_str = 'mysql+pymysql://root:password@localhost/' + database
    connection = create_engine(db_connection_str)
    return connection

def getHeatArenaInfo():
    connection = create_connection("speedway")
    query = """SELECT
        h.gameId,
        t.city,
        h.heatNumber,
        h.driver,
        h.team,
        h.arena,
        h.lane,
        h.hood,
        h.heatTime
    FROM
        heatview h
    INNER JOIN game g
        ON g.id = h.gameId
    INNER JOIN team t
        ON t.id = g.homeTeamId
    WHERE
        heatTime IS NOT NULL
        AND
        heatTime > 0 
    ORDER BY
        heatTime DESC"""

    df = pd.read_sql(query, con=connection)
    return df

def plotArenaTimes(year):
    df = getHeatArenaInfo()
    cities = df['city'].unique()

    sns.displot(data=df, x="heatTime", hue="city", kind='kde')
    plt.title("Banors snabbaste heat-tider\n{}".format(year))
    plt.ylabel("Densitet")
    plt.xlabel("Heat-tid")
    plt.xlim(50,73)
    plt.legend()
    plt.show()

def getHeatLaneInfo():
    connection = create_connection("speedway")
    query = """SELECT
        h.gameId,
        t.city,
        h.heatNumber,
        h.driver,
        h.team,
        h.arena,
        h.points,
        h.lane,
        h.hood,
        h.heatTime
    FROM
        heatview h
    INNER JOIN game g
        ON g.id = h.gameId
    INNER JOIN team t
        ON t.id = g.homeTeamId
    ORDER BY
        gameId, heatNumber DESC"""

    df = pd.read_sql(query, con=connection)
    return df

def plotLanePoints(year):
    df = getHeatLaneInfo()

    sns.countplot(data=df, x="lane", hue="points")
    plt.xlabel("Bana")
    plt.ylabel("Antal")
    plt.ylim(0, 60)
    plt.legend(title='Poäng', loc='upper left', labels=['0', '1', '2', '3'])
    plt.title("Antal 3-, 2-, 1- och 0-poängare per bana på alla arenor\n{}".format(year))
    plt.show()

def plotLanePointsPerArena(year):
    fig, ax = plt.subplots(3, 3, sharex=True, figsize=(16,8), sharey=True)
    axes = ax.flatten()
    fig.legend(labels=['1','2','3','4'], loc='upper right', bbox_to_anchor=(1,-0.1), ncol=len(['1','2','3','4']), bbox_transform=fig.transFigure)
    fig.suptitle('Antal 3-, 2-, 1- och 0-poängare per bana per arena\nBlekaste grön (0 poäng) till Mörkaste grön (3 poäng)\n{}'.format(year))

    palette = sns.light_palette("green", n_colors=4)
    df = getHeatLaneInfo()
    cities = sorted(df['city'].unique())

    i = 0
    for city in cities:
        dfCity = df[df.city == city]
        sns.countplot(ax=axes[i], data=dfCity, x="lane", hue="points", palette=palette)
        axes[i].set_title(city)
        axes[i].set_ylim([0, 75])
        if i%3 == 0:
            axes[i].set_ylabel("Antal")
            axes[i].set_xticks([1,2,3,4])
        else:
            axes[i].set_ylabel("")
        if i >= 6:
            axes[i].set_xlabel("Bana")
        else:
            axes[i].set_xlabel("")
            
        axes[i].get_legend().remove()
        i += 1
    plt.show()

if __name__ == '__main__':
    year = 2021
    # plotLanePoints()
    # 
    plotArenaTimes(year)
    plotLanePoints(year)
    plotLanePointsPerArena(year)