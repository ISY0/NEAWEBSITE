import pandas as pd
import numpy as np
from scipy.spatial import Delaunay
from sqlalchemy import create_engine, ForeignKey, Column, Integer, String , Float , PrimaryKeyConstraint 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker , relationship
import matplotlib.pyplot as plt
import sqlite3
import matplotlib.ticker as mtick
import math
Base = declarative_base()

df = pd.read_csv('NEANBADATASES1.csv', sep=',', usecols=['Season', 'PLAYER_NAME','Team','GAME_DATE','FGM','FGA','FG3A','FG3M','REB','AST','STL','BLK','TOV','PTS',])
ctr = 0 
def determineseason(row):    # we are creating a new row in the dataframe with the actual season in the form (startseason,endseason)
    month_day = row["GAME_DATE"].split()
    month = month_day[0]
    season = int(row["Season"])
    if month in ["JAN","FEB","MAR","APR","MAY"]:
        return (season-1,season)
    elif month in ["NOV", "DEC","OCT"]:
        return (season , season+1)
    elif month in ["JUL","AUG"]:
        return (2019,2020) # to account for the year of covid where the season was finished in july and august
    else:
        return ("None","None")
df["ActualSeason"] = df.apply(determineseason,axis=1)

def getnames(): #This function returns every name of the player in the dataset
    playerlist = []
    results = df["PLAYER_NAME"]
    for player in results:
        if player not in playerlist:
            playerlist.append(player)
    return playerlist

def getseasonsplayed(Playername): # This function finds every instance of a game in a season so that each player has a list of seasons that they played in 
    seasonlist = []
    result = df.loc[df['PLAYER_NAME'] == Playername]
    seasons = result["ActualSeason"]
    for season in seasons:
        if season not in seasonlist:
            seasonlist.append(season)
    return seasonlist

def getteam(Playername,season): # This finds the team that the player played for during the season 
    try:
        result = df.loc[(df['PLAYER_NAME'] == Playername) & (df['ActualSeason'] == season)].iloc[0]
        team = result["Team"]
    except:
        return "None"
    else:
        return team

def getnumberofgames(Playername,season): # Finds the number of games a player plays in a season by counting the number of records in the dataframe
    result = df.loc[(df['PLAYER_NAME'] == Playername) & (df['ActualSeason'] == season)]
    number = len(result)
    return number
    
def getppg(Playername,season): # Calculates the average points per game by dividing the total points scored in the season by the number of games the player played in   
    result = df.loc[(df['PLAYER_NAME'] == Playername) & (df['ActualSeason'] == season)]
    games_played = len(result)
    points = result["PTS"].sum()
    if games_played != 0 and points != 0:
        try:
            pointspergame = points / games_played
        except ZeroDivisionError:
            return 0
        else:
            return round(pointspergame,2)
    else:
        return 0 
def getrebpg(Playername,season): # Calculating rebounds per game 
    result = df.loc[(df['PLAYER_NAME'] == Playername) & (df['ActualSeason'] == season)]
    games_played = len(result)
    rebounds = result["REB"].sum()
    if games_played != 0 and rebounds != 0:
        try:
            reboundspergame = rebounds / games_played
        except ZeroDivisionError:
            return 0
        else:
            return round(reboundspergame,2)
    else:
        return 0 
def getastpg(Playername,season): # Calculating the assists per game
    result = df.loc[(df['PLAYER_NAME'] == Playername) & (df['ActualSeason'] == season)]
    games_played = len(result)
    assists = result["AST"].sum()
    if games_played != 0 and assists != 0:
        try:
            assistspergame = assists / games_played
        except ZeroDivisionError:
            return 0
        else:
            return round(assistspergame,2)
    else:
        return 0 
def get3ppercent(Playername,season): # Calculating the 3 point percentage by dividing the number of 3 pointers made by the number attempted and then multiplied by 100
    result = df.loc[(df['PLAYER_NAME'] == Playername) & (df['ActualSeason'] == season)]
    fg3a = result["FG3A"].sum()
    fg3m = result["FG3M"].sum()

    if fg3a != 0 and fg3m != 0:
        try:
            fg3percent = (fg3m / fg3a)*100
        except ZeroDivisionError:
            return 0
        else:
            return round(fg3percent,2)
    else:
        return 0 
def getfgpercent(Playername,season):
    result = df.loc[(df['PLAYER_NAME'] == Playername) & (df['ActualSeason'] == season)]
    fga = result["FGA"].sum()
    fgm = result["FGM"].sum()
    if fga != 0 and fgm != 0:
        try:
            fgpercent = (fgm / fga) * 100
        except ZeroDivisionError:
            return 0
        else:
            return round(fgpercent,2)
    else:
        return 0

def getsteals(Playername,season):
    result = df.loc[(df['PLAYER_NAME'] == Playername) & (df['ActualSeason'] == season)]
    games_played = len(result)
    steals = result["STL"].sum()
    if games_played != 0 and steals != 0:
        try:
            stealspergame = steals / games_played
        except ZeroDivisionError:
            return 0
        else:
            return round(stealspergame,2)
    else:
        return 0 
def getblocks(Playername,season):
    result = df.loc[(df['PLAYER_NAME'] == Playername) & (df['ActualSeason'] == season)]
    games_played = len(result)
    blocks = result["BLK"].sum()
    if games_played != 0 and blocks != 0:
        try:
            blockspergame = blocks / games_played
        except ZeroDivisionError:
            return 0
        else:
            return round(blockspergame,2)
    else:
        return 0 

def getTOs(Playername,season):
    result = df.loc[(df['PLAYER_NAME'] == Playername) & (df['ActualSeason'] == season)]
    games_played = len(result)
    TOs = result["TOV"].sum()#
    if games_played != 0 and TOs != 0:
        try:
            TOspergame = TOs / games_played
        except ZeroDivisionError:
            return 0
        else:
            return round(TOspergame,2)
    else:
        return 0 
    
def getboxscore(Playername): # This function returns a 2d array where each cell contains the statistics for the player in a single NBA season
    seasonlist = getseasonsplayed(Playername)
    boxscorelist = [] 
    for x in seasonlist:  #Looping over every season a player played in the NBA
        points = getppg(Playername,x)
        rebs = getrebpg(Playername,x)
        asts = getastpg(Playername,x)
        fgper = getfgpercent(Playername,x)
        percent3p = get3ppercent(Playername,x)
        steals = getsteals(Playername,x)
        blocks = getblocks(Playername,x)
        TOs = getTOs(Playername,x)
        team = getteam(Playername,x)
        year = x
        boxscorelist.append([float(points),float(rebs),float(asts),float(fgper),float(percent3p),float(steals),float(blocks),float(TOs),team,year[0]])
        # year[0] makes it so all of the seasons are appended to the first year that it started e.g 1999-2000 season is saved as 1999 because the database does not support a tuple
    return boxscorelist
#initialising the engine and creating the tables and database
class Player(Base):
    __tablename__ = "Player"
    playerid = Column("playerid",Integer,primary_key=True)
    Firstname = Column("Firstname", String)
    Lastname = Column("Lastname", String)

    def __init__(self,playerid,Firstname, Lastname):
        self.playerid = playerid
        self.Firstname = Firstname
        self.Lastname = Lastname
    def __repr__(self):
        return f"{self.playerid} , {self.Firstname} , {self.Lastname}"
    seasons = relationship('Season', back_populates='player',cascade="all, delete, delete-orphan") #creates relationship between the two classes where the delete method is cascade
    def getpointsperyear(self,session,Playerfname,Playersname):
        pointlist = [] #creates a list of the players points per game to be put in the model() function
        results = session.query(Player,Season).join(Season, Player.playerid == Season.playerid).filter(Player.Firstname==Playerfname, Player.Lastname == Playersname).all()
        for player, season in results:
            pointlist.append([player.Firstname, player.Lastname, season.Points_per_game , season.Season])
        return pointlist
    def getrebs(self,session,Playerfname,Playersname):
        results = session.query(Player,Season).join(Season, Player.playerid == Season.playerid).filter(Player.Firstname==Playerfname, Player.Lastname == Playersname).all()
        for player, season in results:
            print(f"{player.Firstname} {player.Lastname} averaged {season.rebounds} rebounds in {season.Season}")
    def getasts(self,session,Playerfname,Playersname):
        results = session.query(Player,Season).join(Season, Player.playerid == Season.playerid).filter(Player.Firstname==Playerfname, Player.Lastname == Playersname).all()
        for player, season in results:
            print(f"{player.Firstname} {player.Lastname} averaged {season.assists} assists in {season.Season}")
    def getfgper(self,session,Playerfname,Playersname):
        results = session.query(Player,Season).join(Season, Player.playerid == Season.playerid).filter(Player.Firstname==Playerfname, Player.Lastname == Playersname).all()
        for player, season in results:
            print(f"{player.Firstname} {player.Lastname} averaged {season.fgper} FG% in {season.Season}")
    def get3ppercent(self,session,Playerfname,Playersname):
        results = session.query(Player,Season).join(Season, Player.playerid == Season.playerid).filter(Player.Firstname==Playerfname, Player.Lastname == Playersname).all()
        for player, season in results:
            print(f"{player.Firstname} {player.Lastname} averaged {season.percent3p} 3P% in {season.Season}")
    def getsteals(self,session,Playerfname,Playersname):
        results = session.query(Player,Season).join(Season, Player.playerid == Season.playerid).filter(Player.Firstname==Playerfname, Player.Lastname == Playersname).all()
        for player, season in results:
            print(f"{player.Firstname} {player.Lastname} averaged {season.steals} steals in {season.Season}")
    def getblocks(self,session,Playerfname,Playersname):
        results = session.query(Player,Season).join(Season, Player.playerid == Season.playerid).filter(Player.Firstname==Playerfname, Player.Lastname == Playersname).all()
        for player, season in results:
            print(f"{player.Firstname} {player.Lastname} averaged {season.blocks} blocks in {season.Season}")
    def getTOs(self,session,Playerfname,Playersname):
        results = session.query(Player,Season).join(Season, Player.playerid == Season.playerid).filter(Player.Firstname==Playerfname, Player.Lastname == Playersname).all()
        for player, season in results:
            print(f"{player.Firstname} {player.Lastname} averaged {season.TOs} Turnovers in {season.Season}")
    def getseasons(self,session,Playerfname,Playersname):
        seasonlist = []
        results = session.query(Player,Season).join(Season, Player.playerid == Season.playerid).filter(Player.Firstname==Playerfname, Player.Lastname == Playersname).all()
        for player, season in results:
            seasonlist.append(season.Season)
        return seasonlist
    

class Season(Base):
    __tablename__ = "Season"
    Season = Column("Season",Integer)
    playerid = Column(Integer, ForeignKey("Player.playerid"))
    Points_per_game = Column("Points_per_game",Float)
    rebounds = Column("Rebounds",Float)
    assists = Column("assists",Float)
    fgper = Column("fgper",Float)
    percent3p = Column("percent3p",Float)
    steals = Column("steals",Float)
    blocks = Column("blocks",Float)
    TOs = Column("TOs",Float)
    team = Column("Team",String)

    __table_args__ = (
        PrimaryKeyConstraint('Season', 'playerid'),
    ) # creates the composite primary key for the table 'Season'
    def __init__(self, Season, playerid, Points_per_game, rebounds, assists, fgper, percent3p, steals, blocks, TOs,team):
        self.Season = Season
        self.playerid = playerid
        self.Points_per_game = Points_per_game
        self.rebounds = rebounds
        self.assists = assists
        self.fgper = fgper
        self.percent3p = percent3p
        self.steals = steals
        self.blocks = blocks
        self.TOs = TOs
        self.team = team
    player = relationship('Player', back_populates='seasons')





engine = create_engine("sqlite:///mydb.db",echo=True)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()


def datainput(): # This inputs the data into the classes Player and Season, using SQLalchemy this creates a relational database
    playeridctr = 0 
    namelist = getnames() # We use the function getnames to produce a list of all players that have ever played in the NBA
    for Playername in namelist: # We then loop over every Player so that we can produce an instance of every player in the database and all of their seasons
        first_last = Playername.split(" ")
        if len(first_last)==2:
            pass
        elif len(first_last) ==1:
            first_last.append(" ")
        playeridctr += 1 
        playerinstance = Player(playeridctr,first_last[0],first_last[1])
        session.add(playerinstance)
        session.commit()
        boxscore = getboxscore(Playername)
        seasons = getseasonsplayed(Playername)
        for x in range(len(seasons)):
            seasoninstance = Season(boxscore[x][9],playeridctr,boxscore[x][0],boxscore[x][1],boxscore[x][2],boxscore[x][3],boxscore[x][4],boxscore[x][5],boxscore[x][6],boxscore[x][7],boxscore[x][8])
            session.add(seasoninstance)
        session.commit()

if not session.query(Player).first(): # This only makes sure to input data if there is no instance of anything within the database
    datainput()


def model(first,last):
    player = session.query(Player).filter_by(Firstname=first, Lastname=last).first()
    points = []
    time = []
    fetchpoints = player.getpointsperyear(session,first,last)
    for x in range(0,len(fetchpoints)):
        points.append(fetchpoints[x][2])
        time.append(fetchpoints[x][3])
    plt.plot(time,points,marker='x',markerfacecolor='blue')
    plt.xlabel("Year")
    plt.ylabel("Points per game")
    plt.gca().xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    plt.title(f"{first} {last}'s Points Per Game over time ")
    plt.show()

def finds(first,last):
    player = session.query(Player).filter_by(Firstname=first, Lastname=last).first()
    session.commit()
    points = player.getpointsperyear(session,first,last)
    for x in range(0,len(points)):
        print(points[x])


 