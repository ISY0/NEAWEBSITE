from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import psycopg2

app = Flask(__name__, template_folder="./templates", static_folder="./static")

Usersandpasswords = [('Isaac','Sesay')]


def connection():
    conn = psycopg2.connect(
        dbname="bwkv4mjzmrnekdcjycl3",
        user="ukjbdjhtvlnzqsu9tnyi",
        password="9L1o8zMjcLcL1p5ouHWlNKLuhebLwi",
        host="bwkv4mjzmrnekdcjycl3-postgresql.services.clever-cloud.com",
        port="50013"
    )
    return conn

def sort(data, sortingby, recentyear):
    playerlist = []

    for player in range(len(data)):
        playerlist.append(data[player])

    seasonstuple = []
    for x in range(len(playerlist)):
        if sortingby == 'points':
            tuples = (playerlist[x][1], playerlist[x][2])  
        elif sortingby == 'rebs':
            tuples = (playerlist[x][1], playerlist[x][3])  
        elif sortingby == 'asts':
            tuples = (playerlist[x][1], playerlist[x][4])  
        elif sortingby == 'names':
            tuples = ()
        seasonstuple.append(tuples)

    mergeSort(seasonstuple)
    idlist = []
    for x in range(0,len(seasonstuple)):
        idlist.append(seasonstuple[x][0])
    return idlist

def mergeSort(seasonstuple):
    if len(seasonstuple) > 1:
        mid = len(seasonstuple) // 2
        lefthalf = seasonstuple[:mid]
        righthalf = seasonstuple[mid:]

        mergeSort(lefthalf)
        mergeSort(righthalf)

        lefthalfpointer = 0
        righthalfpointer = 0
        pointer = 0

        while lefthalfpointer < len(lefthalf) and righthalfpointer < len(righthalf):
            if lefthalf[lefthalfpointer][1] > righthalf[righthalfpointer][1]:
                seasonstuple[pointer] = lefthalf[lefthalfpointer]
                lefthalfpointer += 1
            else:
                seasonstuple[pointer] = righthalf[righthalfpointer]
                righthalfpointer += 1
            pointer += 1

        while lefthalfpointer < len(lefthalf):
            seasonstuple[pointer] = lefthalf[lefthalfpointer]
            lefthalfpointer += 1
            pointer += 1

        while righthalfpointer < len(righthalf):
            seasonstuple[pointer] = righthalf[righthalfpointer]
            righthalfpointer += 1
            pointer += 1

def calculateleaders(recentyear):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM Season WHERE Season = %s""", (recentyear,))
    allseasoninstances = cursor.fetchall()
    cursor.execute("""SELECT * FROM Player""")
    allplayerinstances = cursor.fetchall()
    idlistforpoints = sort(allseasoninstances, 'points', recentyear)
    idlistforassists = sort(allseasoninstances, 'asts', recentyear)
    idlistforrebounds = sort(allseasoninstances, 'rebs', recentyear)

    Leaders = idlistforpoints , idlistforrebounds , idlistforassists 
    PointsSorted = Leaders[0]
    ReboundsSorted = Leaders[1]
    AssistsSorted = Leaders[2]
    top5points = []
    for x in range(0,5):
        top5points.append(PointsSorted[x])
    top5rebounds = []
    for x in range(0,5):
        top5rebounds.append(ReboundsSorted[x])
    top5assists = []
    for x in range(0,5):
        top5assists.append(AssistsSorted[x])

    return top5points , top5rebounds , top5assists

@app.route('/', methods=['POST', 'GET'])
def index():
    conn = connection()
    cursor = conn.cursor()
    Leaders = calculateleaders(2022)
    PointsLeaders = Leaders[0]
    ReboundsLeaders = Leaders[1]
    AssistsLeaders = Leaders[2]
    Playernames = []
    for x in range(0,5):
        cursor.execute("""
            SELECT Firstname, Lastname FROM Player 
            WHERE playerid in (%s)""",(PointsLeaders[x],))
        Playernames += cursor.fetchall()
    Points = []
    for x in range(0,5):
        cursor.execute("""
            SELECT Points_per_game , fgper , percent3p FROM Season
            WHERE playerid in (%s) AND Season = 2022""",(PointsLeaders[x],))
        Points += cursor.fetchall()
    Points += Playernames
    Playernames = []
    for x in range(0,5):
        cursor.execute("""
            SELECT Firstname, Lastname FROM Player 
            WHERE playerid in (%s)""",(ReboundsLeaders[x],))
        Playernames += cursor.fetchall()
    Rebounds = []
    for x in range(0,5):
        cursor.execute("""
            SELECT rebounds , blocks FROM Season
            WHERE playerid in (%s) AND Season = 2022""",(ReboundsLeaders[x],))
        Rebounds += cursor.fetchall()
    Rebounds += Playernames
    Playernames = []
    for x in range(0,5):
        cursor.execute("""
            SELECT Firstname, Lastname FROM Player 
            WHERE playerid in (%s)""",(AssistsLeaders[x],))
        Playernames += cursor.fetchall()
    Assists = []
    for x in range(0,5):
        cursor.execute("""
            SELECT assists , TOs FROM Season
            WHERE playerid in (%s) AND Season = 2022""",(AssistsLeaders[x],))
        Assists += cursor.fetchall()
    Assists += Playernames
    cursor.close()
    conn.close()
    return render_template("index.html", Points=Points ,Rebounds=Rebounds , Assists=Assists )



@app.route('/Login' , methods=['GET','POST'])
def Login():
    if request.method == 'POST':
        Username = request.form['Username']
        Password = request.form['Password']
        if (Username,Password) in Usersandpasswords:
            return redirect('/Admin')
        else:
            return redirect('/')
    else:
        return render_template('login.html')
    
addedplayers = []

@app.route('/Admin',methods=['GET','POST'])
def Admin():
    global addedplayers
    if request.method == 'POST':
        newplayer = []
        newplayer = [request.form['firstname'],request.form['secondname'],int(request.form['Season']),float(request.form['PPG']),float(request.form['RPG']),float(request.form['APG']),float(request.form['FG%']),float(request.form['3P%']),float(request.form['SPG']),float(request.form['BPG']),float(request.form['TOs']),request.form['Team']]
        conn = connection()
        cursor= conn.cursor()
        cursor.execute("""
                SELECT playerid FROM Player
                WHERE Firstname = %s AND Lastname = %s""",(newplayer[0],newplayer[1],))
        newplayerid = cursor.fetchall()
        if newplayerid==[]:
            cursor.execute("""
                INSERT INTO Player (Firstname, Lastname) 
                VALUES (%s, %s)""",(newplayer[0],newplayer[1],))
            conn.commit()
            cursor.execute("""
                SELECT playerid FROM Player
                WHERE Firstname = %s AND Lastname = %s""",(newplayer[0],newplayer[1],))
            newplayerid = cursor.fetchall()
            conn.commit()
            
        playerid = newplayerid[0][0]
        
        cursor.execute("""
            INSERT INTO Season (Season, playerid, Points_per_game, rebounds, assists, fgper, percent3p, steals, blocks, TOs, team)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,(newplayer[2],playerid,newplayer[3],newplayer[4],newplayer[5],newplayer[6],newplayer[7],newplayer[8],newplayer[9],newplayer[10],newplayer[11],))
        conn.commit()
        cursor.close()
        conn.close()
        newplayer.append(playerid)
        addedplayers.append(newplayer)
        if len(addedplayers) > 5:
            addedplayers = addedplayers[1:]
        return render_template('Admin.html', addedplayers=addedplayers) # addedplayers is a list defined in the method which holds all recently created instances
    else:
        return render_template('Admin.html',addedplayers=addedplayers)
    
@app.route('/delete/<int:playerid>')
def delete(playerid):
    global addedplayers
    conn = connection()
    cursor = conn.cursor()
    for player in addedplayers:
        if player[12] == playerid:
            addedplayers.remove(player)
    cursor.execute("""DELETE FROM Player WHERE playerid=%s""", (playerid,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/Admin')


if __name__ == '__main__':
    app.run(debug=True)
