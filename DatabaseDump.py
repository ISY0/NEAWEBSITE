from sqlalchemy import create_engine, text
import sqlite3
import psycopg2

sqlite_conn = sqlite3.connect('mydb.db')  
sqlite_cursor = sqlite_conn.cursor()

# Connecting to the online database
Online = psycopg2.connect(
    dbname="bwkv4mjzmrnekdcjycl3",
    user="ukjbdjhtvlnzqsu9tnyi",
    password="9L1o8zMjcLcL1p5ouHWlNKLuhebLwi",
    host="bwkv4mjzmrnekdcjycl3-postgresql.services.clever-cloud.com",
    port="50013"
)
cursor = Online.cursor()

# Running queries to create the tables in Postgress
cursor.execute("""
CREATE TABLE IF NOT EXISTS Player (
    playerid SERIAL PRIMARY KEY,  -- SERIAL instead of AUTOINCREMENT
    Firstname VARCHAR(255),
    Lastname VARCHAR(255)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Season (
    Season INTEGER NOT NULL,
    playerid INTEGER NOT NULL,
    Points_per_game FLOAT,
    rebounds FLOAT,
    assists FLOAT,
    fgper FLOAT,
    percent3p FLOAT,
    steals FLOAT,
    blocks FLOAT,
    TOs FLOAT,
    team VARCHAR(255),
    PRIMARY KEY (playerid, Season),
    FOREIGN KEY (playerid) REFERENCES Player (playerid) ON DELETE CASCADE
);
""")

sqlite_cursor.execute("SELECT * FROM Player")
players_data = sqlite_cursor.fetchall() # Fetching all of the data from the table Player

cursor.executemany(
    """
    INSERT INTO Player (Firstname, Lastname) VALUES (%s, %s)
    """,
    [(row[1], row[2]) for row in players_data]  
)
# inserting all of the rows from player

#Now fetching all the data from the table Season 
sqlite_cursor.execute("SELECT * FROM Season")
seasons_data = sqlite_cursor.fetchall()
cursor.executemany(
    """
    INSERT INTO Season (Season, playerid, Points_per_game, rebounds, assists, fgper, percent3p, steals, blocks, TOs, team)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """,
    seasons_data
)
cursor.execute("SELECT * FROM Player")

Online.commit()
sqlite_conn.close()
Online.close()