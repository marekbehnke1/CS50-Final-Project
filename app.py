import os

import gviz_api

import datetime

from helpers import login_required, retrieve_iex, sort_data, retrieve_history, dict_factory

from flask import Flask, render_template, session, request, redirect, flash, jsonify
from flask_session import Session

import sqlite3 

import requests

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Make initial API call and save data in variable
#IEXdata = retrieve_iex()

# global userinfo
userInfo = []

#test data
IEXdata = [
    {"ticker": "AAPL",
     "mid": 200,
     "open": 100,
     "volume": 1000,
     "timestamp": 567,
     "high": 999,
     "low": 333,
     "tngoLast": 444},
     {"ticker": "NVDA",
      "mid": 300,
      "open": 500,
      "volume": 100000,
      "timestamp": 567,
      "high": 999,
      "low": 333,
      "tngoLast": 444},
      {"ticker": "TSLA",
      "mid": 370,
      "open": 120,
      "volume": 4540,
      "timestamp": 567,
      "high": 999,
      "low": 333,
      "tngoLast": 444},
      {"ticker": "META",
      "mid": 254,
      "open": 1230,
      "volume": 3423,
      "timestamp": 567,
      "high": 999,
      "low": 333,
      "tngoLast": 444},
      {"ticker": "COKE",
      "mid": 8245,
      "open": 3458,
      "volume": 45674,
      "timestamp": 567,
      "high": 999,
      "low": 333,
      "tngoLast": 444},
      {"ticker": "ORLY",
      "mid": 765,
      "open": 325,
      "volume": 5678,
      "timestamp": 567,
      "high": 999,
      "low": 333,
      "tngoLast": 444},
      {"ticker": "SEB",
      "mid": 34577,
      "open": 3457,
      "volume": 87656,
      "timestamp": 567,
      "high": 999,
      "low": 333,
      "tngoLast": 444},
      {"ticker": "COST",
      "mid": 3456,
      "open": 6657,
      "volume": 334536,
      "timestamp": 567,
      "high": 999,
      "low": 333,
      "tngoLast": 444},
      {"ticker": "BLK",
      "mid": 2343,
      "open": 5645,
      "volume": 3453453,
      "timestamp": 567,
      "high": 999,
      "low": 333,
      "tngoLast": 444},
      {"ticker": "INTU",
      "mid": 2340,
      "open": 2452,
      "volume": 780,
      "timestamp": 567,
      "high": 999,
      "low": 333,
      "tngoLast": 444}]

#### Routes #####
@app.route("/")
@login_required
def index():
    user_id = session["user_id"]

    # set the data to sort
    volumeData = {}
    for item in IEXdata:
        volumeData[item["ticker"]] = item["volume"]

    volumeDataSorted = sort_data("volume", 15, volumeData)

    # set data to sort
    differenceData = {}
    # check if fields are empty & set to 0
    for item in IEXdata:
        if item["tngoLast"] == None:
            last = 0
        else:
            last = item["tngoLast"]
        if item["open"] == None:
            open = 0
        else:
            open = item["open"]

        differenceData[item["ticker"]] = open - last

    differenceDataSorted = sort_data("difference", 20, differenceData)
    differenceDataReverse = sort_data("difference", 20, differenceData, False)

    # retrieve favourites
    db = sqlite3.connect("database.db")

    #convert to list of dict
    db.row_factory = dict_factory
    favouritesList = []
    for row in db.execute("SELECT ticker FROM favourites where userid = ?", (user_id,)):
        favouritesList.append(row)

    db.close()

    if user_id:
        return render_template("index.html", volumeData = volumeDataSorted, differenceData = differenceDataSorted, differenceDataReverse = differenceDataReverse, favouritesList = favouritesList)
    else:
        redirect("/login")

@app.route("/stock")
@login_required
def info_page():

    # because the code is being sent via GET, the info is accesible via the below statement
    query = request.args.get("q")
    if query:
        # this is a generator expression
        # it is looping through IEXdata for a dict where dict["ticker"] == the query
        # and returning the dict as json
        result = next((item for item in IEXdata if item["ticker"] == query), None)
    else:
        result = []
    return jsonify(result)

@app.route("/search")
@login_required
def search():

    query = request.args.get("q")
    db = sqlite3.connect("database.db")
    curs = db.cursor()

    if query:
        # have limited to 20 with sql query
        result = curs.execute("SELECT * FROM stocks WHERE ticker LIKE ? LIMIT 20", (query + "%",)).fetchall()
    else:
        result = ()
    db.close()

    return jsonify(result)

@app.route("/chart")
@login_required
def chart():
    # get query for the ticker code
    query = request.args.get("q")

    dateFrom = request.args.get("from")
    dateTo = request.args.get("to")

    #include a default date range if date is not set
    if not dateFrom and not dateTo:
        # set to -7 days ago
        dateFromInit = datetime.date.today() - datetime.timedelta(days=28)
        dateFrom = dateFromInit.strftime('%Y-%m-%d')

        # set to todays date
        dateToInit = datetime.date.today() 
        dateTo = dateToInit.strftime('%Y-%m-%d')

    else:
        dateFrom = request.args.get("from")
        dateTo = request.args.get("to")


    data = []
    #Retrive historical date for given dates
    for row in retrieve_history(query, dateFrom, dateTo):
        data.append({
            "date" : row["date"][:10],
            "low" : (row["low"], str(row["low"])),
            "open" : (row["open"], str(row["open"])),
            "close" : (row["close"], str(row["close"])),
            "high" : (row["high"], str(row["high"]))
        })

    ## set schema for data table
    description = {"date" : ("string", "Date"),
                   "low" : ("number", "Low"),
                   "open" : ("number", "Open"),
                   "close" : ("number", "Close"),
                   "high" : ("number", "High")}

    ## initialise datatable
    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)
#
    ## convert the data table into a json response
    chart_data = data_table.ToJSon(columns_order=("date", "low", "open", "close", "high"))

    return chart_data

@app.route("/favourite")
@login_required
def favourite():

    user_id = session["user_id"]
    qType = request.args.get("q")
    qCode = request.args.get("ticker")

    db = sqlite3.connect("database.db")
    curs = db.cursor()

    if qType:    
        # check if query is remove or add
        if qType == "rm":
            curs.execute("DELETE FROM favourites WHERE userid = ? AND ticker = ?", (user_id, qCode,))
            db.commit()
        elif qType =="ad":
        # if item is not in favourites, add to list
            if not (curs.execute("SELECT * FROM favourites where userid = ? AND ticker = ?", (user_id, qCode,)).fetchall()):
                curs.execute("INSERT INTO favourites (userid, ticker) VALUES (?, ?)", (user_id, qCode,))
                db.commit()   
    
    #convert query results to dict
    db.row_factory = dict_factory
    user_favourites = []
    for row in db.execute("SELECT ticker FROM favourites where userid = ?", (user_id,)):
        user_favourites.append(row)

    db.close()
    return jsonify(user_favourites)

@app.route("/login" , methods=["GET", "POST"])
def login():

    #clear any session info
    session.clear()

    if request.method == "POST":
        uname = request.form.get("username")
        if not uname:
            flash("Please enter a username", "error")
            return render_template("login.html")
        password = request.form.get("password")
        if not password:
            flash("Please enter a password", "error")
            return render_template("login.html")
        
        # Query database for username
        db = sqlite3.connect("database.db")
        cur = db.cursor()

        try:
            # this is a horrible way of expressing this - need it to return a list or something
            userid = cur.execute("SELECT userid FROM users WHERE username = ?", (uname,)).fetchone()[0]
        except TypeError:
            db.close()
            flash("Username does not exist", "error")
            return render_template("login.html")
        else:
            #if username exists, attempt to match against password
            hash = cur.execute("SELECT hash FROM users WHERE userid = ?", (userid,)).fetchone()[0] 
            db.close()
            
            if not check_password_hash(hash, password):
                flash("Incorrect password", "error")
                return render_template("login.html")
            
            # if login details ok - set session id
            session["user_id"] = userid
            return redirect("/")
    else:
        return render_template("login.html")
    
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        # create new user object
        new_user = {
            "username" : request.form.get("username"),
            "first name": request.form.get("fname"),
            "last name" : request.form.get("lname"),
            "email" : request.form.get("email"),
            "password": request.form.get("password")
        }
        # check if any values in form are missing, and return appropriate error
        for key, value in new_user.items():
            if not value:
                flash("Please enter " + key, "error")
                return render_template("register.html")
            
        # check if passwords match
        if not new_user["password"] == request.form.get("password_check"):
            flash("Passwords do not match", "error")
            return render_template("register.html")
        
        hash = generate_password_hash(new_user["password"])
        # connect to database
        db = sqlite3.connect("database.db")
        curs = db.cursor()

        # check if any error occured on db entry
        try:
            curs.execute("INSERT INTO users (username, fname, lname, email, hash) VALUES (?, ?, ?, ?, ?)",
                        (new_user["username"], new_user["first name"], new_user["last name"], new_user["email"], hash))
        except:
            db.close()
            flash("Username already exists", "error")
            return render_template("register.html")
        else:
            db.commit()
            db.close
            flash("Registration Succesfull", "success")
            return render_template("login.html")

    else:
         return render_template("register.html")

@app.route("/account")
@login_required
def account():

    db = sqlite3.connect("database.db")
    db.row_factory = dict_factory

    # set userinfo to be stored in a session variable
    session["user_info"] = []
    for row in db.execute("SELECT username, fname, lname, email FROM users WHERE userid = ?", (session["user_id"],)):
        session["user_info"].append(row)

    return render_template("account.html", userInfo = session["user_info"])

@app.route("/password", methods=["GET", "POST"] )
@login_required
def change_password():

    if request.method == "POST":

        db = sqlite3.connect("database.db")
        curs = db.cursor()

        hash = curs.execute("SELECT hash FROM users WHERE userid = ?", (session["user_id"],)).fetchone()[0]
        password = request.form.get("password")
        newPassword = request.form.get("newPassword")
        newPasswordConfirm = request.form.get("newPasswordConfirm")

        # check fields are complete
        if not password or not newPassword or not newPasswordConfirm:
            flash("Please complete all fields", "error")
            db.close()
            return render_template("/password.html", userInfo = session["user_info"])

        # check password is correct
        if check_password_hash(hash, password):

            # Check new passwords match
            if newPassword == newPasswordConfirm:
                curs.execute("UPDATE users SET hash = ? WHERE userid = ?", (generate_password_hash(newPassword), session["user_id"]))
                db.commit()
                flash("Password succesfully changed", "success")
                db.close()
                return render_template("/password.html", userInfo = session["user_info"])
            else:
                flash("Passwords did not match", "error")
                db.close()
                return render_template("/password.html", userInfo = session["user_info"])

        else:
            flash("Incorrect Password", "error")
            db.close()
            return render_template("/password.html", userInfo = session["user_info"])
    
    else:
        return render_template("/password.html", userInfo = session["user_info"])


@app.route("/logout")
def logout():

    session.clear()
    return redirect("/")
