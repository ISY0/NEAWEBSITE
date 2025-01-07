import psycopg2
# used to check the output of queries to ensure that the data recieved from a query is correctly handled
#checking the connection with the database and ensuring data is inputted correctly 
conn = psycopg2.connect(
    dbname="bwkv4mjzmrnekdcjycl3",
    user="ukjbdjhtvlnzqsu9tnyi",
    password="9L1o8zMjcLcL1p5ouHWlNKLuhebLwi",
    host="bwkv4mjzmrnekdcjycl3-postgresql.services.clever-cloud.com",
    port="50013"
)
cursor = conn.cursor()

newplayer = ["Isaac","Sesay",2024,1,1,1,1,1,1,1,1,"mem"]
cursor.execute("""
                SELECT playerid FROM Player
                WHERE Firstname = %s AND Lastname = %s""",(newplayer[0],newplayer[1],))
newplayerid = cursor.fetchall()
print(newplayerid)
if newplayerid==[]:
    cursor.execute("""
        INSERT INTO Player (Firstname, Lastname) 
        VALUES (%s, %s)""",(newplayer[0],newplayer[1],))
    cursor.execute("""
        SELECT playerid FROM Player
        WHERE Firstname = %s AND Lastname = %s""",(newplayer[0],newplayer[1],))
    newplayerid = cursor.fetchall()
    print("THere was no playerid found")
    
playerid = newplayerid[0][0]

cursor.execute("""
    INSERT INTO Season (Season, playerid, Points_per_game, rebounds, assists, fgper, percent3p, steals, blocks, TOs, team)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,(newplayer[2],playerid,newplayer[3],newplayer[4],newplayer[5],newplayer[6],newplayer[7],newplayer[8],newplayer[9],newplayer[10],newplayer[11],))
print("Inserted into season")



cursor.execute("""
        SELECT * FROM Season
        WHERE Season = 2024""")
playerid = cursor.fetchall()
print(playerid)
cursor.close()
conn.close()