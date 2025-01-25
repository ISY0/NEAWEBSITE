from flask import Flask, render_template, request, redirect , jsonify
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import numpy as np
import plotly.graph_objs as go
import plotly
import json
from prophet import Prophet
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

app = Flask(__name__, template_folder="./templates", static_folder="./static")

Usersandpasswords = [('Admin1','Password')]

teamlogos = {
    'NYK' : 'logos/Knicks.png',
    'ATL' : 'logos/AtlantaHawks.png',
    'BOS' : 'logos/Celtics.png',
    'BKN' : 'logos/Nets.png',
    'CHA' : 'logos/Hornets.png',
    'CHH' : 'logos/Hornets.png',
    'CHI' : 'logos/Bulls.png',
    'CLE' : 'logos/Cavs.png',
    'DAL' : 'logos/Mavericks.png',
    'DEN' : 'logos/denver.png',
    'DET' : 'logos/Pistons.png',
    'GSW' : 'logos/Warriors.png',
    'HOU' : 'logos/Rockets.png',
    'IND' : 'logos/Pacers.png',
    'LAC' : 'logos/Clippers.png',
    'LAL' : 'logos/Lakers.png',
    'MEM' : 'logos/Grizzlies.png',
    'MIA' : 'logos/Heat.png',
    'MIL' : 'logos/Bucks.png',
    'MIN' : 'logos/Timberwolves.png',
    'NOP' : 'logos/Pelicans.png',
    'OKC' : 'logos/OKC.png',
    'ORL' : 'logos/Magic.png',
    'PHI' : 'logos/Philadelphia.png',
    'PHX' : 'logos/Suns.png',
    'POR' : 'logos/Trailblazers.png',
    'SAC' : 'logos/Kings.png',
    'SAS' : 'logos/Spurs.png',
    'TOR' : 'logos/Raptors.png',
    'UTA' : 'logos/Jazz.png',
    'WAS' : 'logos/Wizards.png',
    'SEA' : 'logos/Sonics.png',
    'SAN' : 'logos/Spurs.png',
    'NJN' : 'logos/NJN.png',
    'NOK' : 'logos/Pelicans.png',
    'NOH' : 'logos/Pelicans.png',
    'UTH' : 'logos/Jazz.png',
    'GOS' : 'logos/Warriors.png',
    'KCK' : 'logos/KCK.png',
    'WSB' : 'logos/Wizards.png',
    'PHL' : 'logos/Philadelphia.png',
    'SDC' : 'logos/Clippers.png',
}

def connection():
    conn = psycopg2.connect(
        dbname="bwkv4mjzmrnekdcjycl3",
        user="ukjbdjhtvlnzqsu9tnyi",
        password="9L1o8zMjcLcL1p5ouHWlNKLuhebLwi",
        host="bwkv4mjzmrnekdcjycl3-postgresql.services.clever-cloud.com",
        port="50013"
    )
    return conn

def sort(data, sortingby, recentyear,Completedataset=False):
    conn = connection()
    cursor = conn.cursor()
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
        seasonstuple.append(tuples)

    mergeSort(seasonstuple)
    idlist = []
    for x in range(0,len(seasonstuple)):
        idlist.append(seasonstuple[x][0])
    if Completedataset == True:
        idlist = idlist[:150]
    else:
        idlist = idlist[0:5]
    datalist = []
    for player in idlist:
        cursor.execute("""
            SELECT Season.*, Player.Firstname, Player.Lastname 
            FROM Season
            INNER JOIN Player ON Player.playerid = Season.playerid 
            WHERE Season.playerid = %s AND Season.Season = %s
            """, (player,recentyear,))
        datalist.append(cursor.fetchall())
    cursor.close()
    conn.close()
    return datalist

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
    conn.close()
    cursor.close()
    SortedPoints= sort(allseasoninstances, 'points', recentyear)
    SortedAssists = sort(allseasoninstances, 'asts', recentyear)
    SortedRebounds = sort(allseasoninstances, 'rebs', recentyear)
    Leaders = SortedPoints , SortedRebounds , SortedAssists 
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
        top5assists.append(AssistsSorted[x])#
    return top5points , top5rebounds , top5assists

def model(first,last):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Points_per_game , Season 
        FROM Season INNER JOIN Player
        ON Player.playerid = Season.playerid
        WHERE Player.Firstname = %s AND Player.Lastname = %s""",(first,last))
    playerseasons = cursor.fetchall()
    cursor.close()
    conn.close()
    pointlist = []
    seasonlist = []
    for season in playerseasons:
        points,seasons = season
        pointlist.append(points)
        seasonlist.append(seasons)
    
    graph = go.Figure(data=[go.Scatter(x=seasonlist,y=pointlist, mode='lines+markers') ])
    graph.update_layout(title=f"{first} {last}'s Points Per game" , xaxis_title="Season", yaxis_title="Points per game")
    graph.update_layout(xaxis=dict(tickmode='linear',dtick=1))
    jsongraph = json.dumps(graph ,cls=plotly.utils.PlotlyJSONEncoder)
    return jsongraph

def gradingsystem(first,last,recentseason=2022):
    playerseasons = nametostats(first,last,recentseason)
    playerseason = playerseasons[0]
    if playerseason[2] > 25:
        pointsgrade = "A+"
    elif playerseason[2] > 18 and playerseason[2] <= 25:
        pointsgrade = "A"
    elif playerseason[2] > 14 and playerseason[2] <= 18:
        pointsgrade = "B"
    elif playerseason[2] > 10 and playerseason[2] <= 14:
        pointsgrade = "C"
    elif playerseason[2] > 7 and playerseason[2] <= 10 :
        pointsgrade = "D"
    elif playerseason[2] <= 7:
        pointsgrade = "E"

    if playerseason[3] > 14:
        reboundsgrade = "A+"
    elif playerseason[3] > 10 and playerseason[3] <= 14:
        reboundsgrade = "A"
    elif playerseason[3] > 7 and playerseason[3] <= 10:
        reboundsgrade = "B"
    elif playerseason[3] > 4 and playerseason[3] <= 17:
        reboundsgrade = "C"
    elif playerseason[3] > 2 and playerseason[3] <= 4 :
        reboundsgrade = "D"
    elif playerseason[3] <= 2:
        reboundsgrade = "E"
        
    if playerseason[4] > 11:
        assistsgrade = "A+"
    elif playerseason[4] > 8 and playerseason[4] <= 11:
        assistsgrade = "A"
    elif playerseason[4] > 4 and playerseason[4] <= 8:
        assistsgrade = "B"
    elif playerseason[4] > 2.5 and playerseason[4] <= 4:
        assistsgrade = "C"
    elif playerseason[4] > 1.5 and playerseason[4] <= 2.5:
        assistsgrade = "D"
    elif playerseason[4] <= 1.5:
        assistsgrade = "E"

    if playerseason[5] > 60:
        fggrade = "A+"
    elif playerseason[5] > 50 and playerseason[5] <= 60:
        fggrade = "A"
    elif playerseason[5] > 45 and playerseason[5] <= 50:
        fggrade = "B"
    elif playerseason[5] > 40 and playerseason[5] <= 45:
        fggrade = "C"
    elif playerseason[5] > 35 and playerseason[5] <= 40 :
        fggrade = "D"
    elif playerseason[5] <= 35:
        fggrade = "E"
        
    if playerseason[6] > 42:
        percent3grade = "A+"
    elif playerseason[6] > 38 and playerseason[6] <= 42:
        percent3grade = "A"
    elif playerseason[6] > 36 and playerseason[6] <= 38:
        percent3grade = "B"
    elif playerseason[6] > 33 and playerseason[6] <= 36:
        percent3grade = "C"
    elif playerseason[6] > 25 and playerseason[6] <= 33:
        percent3grade = "D"
    elif playerseason[6] <= 25:
        percent3grade = "E"
    
    if playerseason[7] > 3:
        stealgrade = "A+"
    elif playerseason[7] > 1.8 and playerseason[7] <= 3:
        stealgrade = "A"
    elif playerseason[7] > 1 and playerseason[7] <= 1.8:
        stealgrade = "B"
    elif playerseason[7] > 0.6 and playerseason[7] <= 1:
        stealgrade = "C"
    elif playerseason[7] > 0.3 and playerseason[7] <= 0.6:
        stealgrade = "D"
    elif playerseason[7] <= 0.3:
        stealgrade = "E"

    if playerseason[8] > 4:
        blockgrade = "A+"
    elif playerseason[8] > 2 and playerseason[8] <= 4:
        blockgrade = "A"
    elif playerseason[8] > 1.3 and playerseason[8] <= 2:
        blockgrade = "B"
    elif playerseason[8] > 0.8 and playerseason[8] <= 1.3:
        blockgrade = "C"
    elif playerseason[8] > 0.4 and playerseason[8] <= 0.8:
        blockgrade = "D"
    elif playerseason[8] <= 0.4:
        blockgrade = "E"

    grades = [pointsgrade,reboundsgrade,assistsgrade,fggrade,percent3grade,stealgrade,blockgrade]
    return playerseason , grades

def nametostats(First,Last,season=2022):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM Season INNER JOIN Player
        ON Player.playerid = Season.playerid
        WHERE Player.Firstname = %s AND Player.Lastname = %s AND Season = %s""",(First,Last,season,))
    playerseasons = cursor.fetchall()
    conn.close()
    cursor.close()
    return playerseasons

def findrecentseason(First,Last):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT MAX(Season)
        FROM Season INNER JOIN Player
        ON Player.playerid = Season.playerid
        WHERE Player.Firstname = %s AND Player.Lastname = %s""",(First,Last,))
    recentseason = cursor.fetchall()
    return recentseason[0][0]

def Modelpredictor(first,last):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Points_per_game , Season 
        FROM Season INNER JOIN Player
        ON Player.playerid = Season.playerid
        WHERE Player.Firstname = %s AND Player.Lastname = %s""",(first,last,))
    playerseasons = cursor.fetchall()
    cursor.execute("""
                SELECT MIN(Season)
                FROM Season INNER JOIN Player
                ON Player.playerid = Season.playerid
                WHERE Player.Firstname = %s AND Player.Lastname = %s""",(first,last,) )
    firstyear = cursor.fetchall()
    if len(playerseasons) < 3:
        return "Not enough data to predict future performance"
    if len(playerseasons) > 14:
        return "Model can only predict up to players' 18th season. Modelling this player would be inaccurate"
    conn.close()
    cursor.close()
    pointlist = []
    seasonlist = []
    for season in playerseasons:
        points,seasons = season
        s = seasons - firstyear[0][0]
        pointlist.append(points)
        seasonlist.append(s)
    player_years = seasonlist
    player_points = pointlist
    def general_trend(x, peak_year=10, peak_value=30):
        return -0.15 *(x-peak_year)**2 + peak_value 
    def calculate_peak(player_points):
        if len(player_points) < 3:
            third_season_points = max(player_points)
        else:
            third_season_points = player_points[2] 
        calculated_peak = 1.5 * third_season_points
        if min(calculated_peak,30) < max(player_points):
            return max(player_points)
        else:
            return min(calculated_peak, 30)

    def scale_curve(player_years, player_points):
        peak_value = calculate_peak(player_points)
        def scaled_trend(x):
            return general_trend(x, peak_year=10, peak_value=peak_value)
        return scaled_trend

    def predict_future(player_years, player_points, future_years=5, max_years=18):
        scaled_trend = scale_curve(player_years, player_points)
        all_years = np.arange(0, max(player_years) + future_years + 1)
        predictions = scaled_trend(all_years)
        valid_years = all_years[all_years <= max_years]
        valid_predictions = predictions[:len(valid_years)]
        return valid_years, valid_predictions

    future_years, future_points = predict_future(player_years, player_points)
    next_five_years = np.arange(max(player_years) + 1, max(player_years) + 6)  # Next 5 years
    next_five_points = [np.interp(year, future_years, future_points) for year in next_five_years]

    scatter = go.Scatter(x=player_years,y=player_points,mode='markers',marker=dict(color='blue'),name="Player's Historical Data")
    line = go.Scatter(x=future_years,y=future_points,mode='lines',line=dict(color='green'),name="Predicted Future Performance")
    fig = go.Figure(data=[scatter, line])
    fig.update_layout(title=f"{first} {last}'s Points Per Game Prediction",xaxis_title="Years in NBA",yaxis_title="Points Per Game",legend=dict(title="Legend"),template="plotly_white")
    fig.add_trace(go.Scatter(x=next_five_years,y=next_five_points,mode='markers',name="Predicted Points (Next 5 Seasons)",marker=dict(color='red', size=5, symbol='cross')))
    jsongraph = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return jsongraph

def playeridtoname(Playerid):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT Firstname, Lastname FROM Player WHERE playerid = %s""",(Playerid,))
    name = cursor.fetchall()
    return name

def teamlist(first,last):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Team FROM Season INNER JOIN Player
        ON Player.playerid = Season.playerid
        WHERE Player.Firstname = %s AND Player.Lastname = %s""",(first,last,))
    teams = cursor.fetchall()
    cursor.close()
    teamlist = []
    numberlist = []
    for team in teams:
        if len(teamlist) != 0:
            if team[0] == teamlist[-1]:
                numberlist[-1] += 1
            else:
                teamlist.append(team[0])
                numberlist.append(1)
        else:
            teamlist.append(team[0])
            numberlist.append(1)
    

    return teamlist , numberlist
    

@app.route('/', methods=['POST', 'GET'])
def index():
    Stats = False
    conn = connection()
    cursor = conn.cursor()
    Leaders = calculateleaders(2022)
    PointsLeaders = Leaders[0]
    ReboundsLeaders = Leaders[1]
    AssistsLeaders = Leaders[2]
    Points = []
    for x in range(0,5):
        Points.append(PointsLeaders[x])
    Rebounds = []
    for x in range(0,5):
        Rebounds.append(ReboundsLeaders[x])
    Assists = []
    for x in range(0,5):
        Assists.append(AssistsLeaders[x])
    cursor.close()
    conn.close()
    prediction = Modelpredictor("Joel","Embiid")

    if request.method == 'POST':
        name = request.form['playersearch']
        first , last = name.split(" ")
        Stats = True
        prediction = Modelpredictor(first,last)
        if prediction == "Not enough data to predict future performance" or prediction == "Model can only predict up to players' 18th season. Modelling this player would be inaccurate":
            comment = prediction
            return render_template("index.html", Points=Points ,Rebounds=Rebounds , Assists=Assists ,prediction=prediction,Stats=Stats,PlayerStatsValid=False,comment=comment)
        return render_template("index.html", Points=Points ,Rebounds=Rebounds , Assists=Assists ,prediction=prediction,Stats=Stats,PlayerStatsValid=True)

    return render_template("index.html", Points=Points ,Rebounds=Rebounds , Assists=Assists ,prediction=prediction,Stats=Stats,PlayerStatsValid=True)

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
    global Searched
    outputstatement = ""
    Playerfound = False
    form_type = request.args.get('form')
    if form_type == 'PlayerUpload':
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
        return render_template('Admin.html', addedplayers=addedplayers,outputstatement=outputstatement) # addedplayers is a list defined in the method which holds all recently created instances
    elif form_type == 'Search':
        Searched = []
        conn = connection()
        cursor = conn.cursor()
        SearchedPlayer = request.form['SearchedPlayer']

        if " " in SearchedPlayer:
            firstname , lastname = SearchedPlayer.split(" ")
            if firstname[0].islower() or lastname[0].islower():
                firstname = firstname[0].upper() + firstname[1:]
                lastname = lastname[0].upper() + lastname[1:]
            cursor.execute("""
                    SELECT * FROM Player
                    WHERE Firstname = %s and Lastname =%s """,(firstname,lastname))
            Searched = cursor.fetchall()
            conn.close()
            cursor.close()
            if Searched == [] :
                outputstatement = "There is No player in the database with this name. Please Check spelling and try again."
            else:
                outputstatement = f"Player {Searched[0][1]} {Searched[0][2]} will be deleted. Are you sure you would like to continue"
                Playerfound = True


            return render_template('Admin.html',addedplayers=addedplayers,outputstatement=outputstatement , Playerfound=Playerfound)
        
        elif " " not in SearchedPlayer:
            outputstatement = "Please check spelling and try again"
            return render_template('Admin.html',addedplayers=addedplayers,outputstatement=outputstatement, Playerfound=Playerfound)
            
    elif form_type == 'ConfirmButton':
        Confirm = request.form.get('action')
        if Confirm == 'Yes':
            conn = connection()
            cursor = conn.cursor()
            firstname , lastname = Searched[0][1],Searched[0][2]
            cursor.execute("""
                DELETE FROM Player
                WHERE Firstname = %s AND Lastname = %s""",(Searched[0][1],Searched[0][2]))
            outputstatement = "Player has been succesfully deleted from the database"
            for player in addedplayers:
                if player[0] == firstname and player[1] == lastname:
                    addedplayers.remove(player)

            conn.commit()
            conn.close()
            cursor.close()

            return render_template('Admin.html',addedplayers=addedplayers,outputstatement=outputstatement, Playerfound=Playerfound)

        elif Confirm == 'No':
            return render_template('Admin.html',addedplayers=addedplayers,outputstatement=outputstatement, Playerfound=Playerfound)

        else:
            raise ValueError
    else:
        return render_template('Admin.html',addedplayers=addedplayers,outputstatement=outputstatement, Playerfound=Playerfound)


@app.route('/PlayerStats', methods=['GET'])
def cell_click(): 
    cell_content = request.args.get('content', None)
    if not cell_content:
        first,last = request.args.get("PlayerSearch").split(" ")
        if not first or not last:
            raise ValueError
        cell_content = first + " " + last
    else:
        first , last = cell_content.split(" ")
    recentseason = findrecentseason(first,last)
    graph = model(first,last)
    statsandgrades = gradingsystem(first,last,recentseason)
    stats , grades = statsandgrades
    teams , years= teamlist(first,last)
    return render_template('playerstats.html', cell_content=cell_content , graph_json=graph,stats=stats,grades=grades,teams=teams,teamlogos=teamlogos,years=years,first=first,last=last)

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

@app.route('/Table', methods=['GET','POST'])
def table():
    Table = True
    Season=2022
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM Season INNER JOIN Player 
                       ON PLayer.playerid = Season.playerid
                       WHERE Season.Season = %s""", (Season,))  
    data = cursor.fetchall()
    sorteddata = sort(data, 'points', 2022,True) 
    if request.method == 'POST':
        Season = request.form['Seasonsearch']
        if int(Season) < 1979:
            output = "Season not found please try again"
            Table = False
            return render_template('Table.html', data=sorteddata,teamlogos=teamlogos,output=output,Table=Table,Season=int(Season))
        elif int(Season) > 2022:
            output = "Season not found please try again"
            Table = False
            return render_template('Table.html', data=sorteddata,teamlogos=teamlogos,output=output,Table=Table,Season=int(Season))
        cursor.execute("""SELECT * FROM Season INNER JOIN Player 
                       ON PLayer.playerid = Season.playerid
                       WHERE Season.Season = %s""", (Season,))
        data = cursor.fetchall()
        sorteddata = sort(data, 'points', Season,True)
        conn.close()
        cursor.close()
        return render_template('Table.html', data=sorteddata,teamlogos=teamlogos,Table=Table,Season=int(Season))
    conn.close()
    cursor.close()
    return render_template('Table.html', data=sorteddata , teamlogos=teamlogos,Table=Table,Season=int(Season))


if __name__ == '__main__':
    app.run(debug=True)
