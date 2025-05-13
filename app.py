import os

import gviz_api

import datetime

from helpers import login_required, retrieve_iex, sort_data, retrieve_history, dict_factory, retrieve_metadata, retrieve_news, retrieve_stock_data

from flask import Flask, render_template, session, request, redirect, flash, jsonify
from flask_session import Session

import sqlite3 

import requests

from werkzeug.security import generate_password_hash, check_password_hash

import re

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Make initial API call and save data in variable
IEXdata = retrieve_iex()

# global userinfo
userInfo = []

##test data
#IEXdata = [
#    {"ticker": "AAPL",
#     "mid": 200,
#     "open": 100,
#     "volume": 1000,
#     "timestamp": 567,
#     "high": 999,
#     "low": 333,
#     "tngoLast": 444},
#     {"ticker": "NVDA",
#      "mid": 300,
#      "open": 500,
#      "volume": 100000,
#      "timestamp": 567,
#      "high": 999,
#      "low": 333,
#      "tngoLast": 600},
#      {"ticker": "TSLA",
#      "mid": 370,
#      "open": 120,
#      "volume": 4540,
#      "timestamp": 567,
#      "high": 999,
#      "low": 333,
#      "tngoLast": 444},
#      {"ticker": "META",
#      "mid": 254,
#      "open": 1230,
#      "volume": 3423,
#      "timestamp": 567,
#      "high": 999,
#      "low": 333,
#      "tngoLast": 444},
#      {"ticker": "COKE",
#      "mid": 8245,
#      "open": 3458,
#      "volume": 45674,
#      "timestamp": 567,
#      "high": 999,
#      "low": 333,
#      "tngoLast": 444},
#      {"ticker": "ORLY",
#      "mid": 765,
#      "open": 325,
#      "volume": 5678,
#      "timestamp": 567,
#      "high": 999,
#      "low": 333,
#      "tngoLast": 444},
#      {"ticker": "SEB",
#      "mid": 34577,
#      "open": 3457,
#      "volume": 87656,
#      "timestamp": 567,
#      "high": 999,
#      "low": 333,
#      "tngoLast": 444},
#      {"ticker": "COST",
#      "mid": 3456,
#      "open": 6657,
#      "volume": 334536,
#      "timestamp": 567,
#      "high": 999,
#      "low": 333,
#      "tngoLast": 444},
#      {"ticker": "BLK",
#      "mid": 2343,
#      "open": 5645,
#      "volume": 3453453,
#      "timestamp": 567,
#      "high": 999,
#      "low": 333,
#      "tngoLast": 444},
#      {"ticker": "BBW",
#      "mid": 58,
#      "open": 41,
#      "volume": 3456,
#      "timestamp": 543,
#      "high": 112,
#      "low": 41,
#      "tngoLast": 83},
#      {"ticker": "X",
#      "mid": 46,
#      "open": 67,
#      "volume": 32345,
#      "timestamp": 23,
#      "high": 1245,
#      "low": 41,
#      "tngoLast": 658},
#      {"ticker": "INTU",
#      "mid": 2340,
#      "open": 2452,
#      "volume": 780,
#      "timestamp": 567,
#      "high": 999,
#      "low": 333,
#      "tngoLast": 444}]

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
    for row in db.execute("SELECT ticker, change FROM favourites where userid = ?", (user_id,)):
        favouritesList.append(row)

    db.close()

    # update saved change values - once per day
    # gain or loss for favourites
    dateFromInit = datetime.date.today() - datetime.timedelta(days=7)
    dateFrom = dateFromInit.strftime('%Y-%m-%d')

    # set to todays date
    dateToInit = datetime.date.today() 
    dateTo = dateToInit.strftime('%Y-%m-%d')
    
    #redeclaring this for clarity
    todayDate = dateTo

    ## updating the favourites values once per day ##
    db = sqlite3.connect("database.db")
    curs = db.cursor()
    userLastUpdate = curs.execute("SELECT lastUpdate FROM users WHERE userid = ?", (user_id,)).fetchone()[0]

    if userLastUpdate != todayDate:
        # set the update date to today

        # update favourites with current data
        for item in favouritesList:
            lastWeekData = retrieve_history(item["ticker"], dateFrom, dateTo)
            # in case of api calls being reached
            try:
                change = lastWeekData[len(lastWeekData) - 1]["close"] - lastWeekData[0]["open"]
                changePercent = round((change / lastWeekData[0]["open"]) * 100, 3)
                # Check to see if the API data is different to the saved data. Updates saved data if so
                # item["change"] is saved as a % 
                if item["change"] != changePercent:

                    curs.execute("UPDATE favourites SET change = ? WHERE userid = ? AND ticker = ?", (changePercent, user_id, item["ticker"],))
                    db.commit()
                    item["change"] = changePercent
            except:
                flash("API limit reached")
                db.close()
                return redirect("/index.html")

        curs.execute("UPDATE users SET lastUpdate = ? WHERE userid = ?", (dateTo, user_id,))
        db.commit()
        db.close()
               
    else:
        db.close()

    if user_id:
        return render_template("index.html", volumeData = volumeDataSorted, differenceData = differenceDataSorted, differenceDataReverse = differenceDataReverse, favouritesList = favouritesList)
    else:
        redirect("/login")

@app.route("/stock")
@login_required
def info_page():
    #
    # this will work properly when we use the full iexdata set
    #

    query = request.args.get("q")
    if query:
        # this is a generator expression
        # it is looping through IEXdata for a dict where dict["ticker"] == the query
        # and returning the dict
        result = next((item for item in IEXdata if item["ticker"] == query), None)
        if not result:
            result = {}
            result["info"] = "No information was available for this stock"
            return jsonify(result)

        # check database to see if meta data text exists
        # if it does not, api call and update entry
        db = sqlite3.connect("database.db")
        curs = db.cursor()

        # these wont load while using test data
        infoText = curs.execute("SELECT info FROM stocks WHERE ticker = ?", (query,)).fetchone()[0]
        company_name = curs.execute("SELECT name FROM stocks WHERE ticker = ?", (query,)).fetchone()[0]

        # check if info text exists in db
        if not infoText or not company_name: 

            metadata = retrieve_metadata(query)
            
            infoText = metadata["description"]
            company_name = metadata["name"]
            # check if API info text exists and provide default
            if not infoText:
                infoText = "No information was available for this stock"
            if not company_name:
                company_name = "No information available for this stock"


            #if ticker exists in db, add metadata to it
            if curs.execute("SELECT * FROM stocks WHERE ticker = ?", (query,)).fetchone()[0]:

                curs.execute("UPDATE stocks SET info = ?, name = ? WHERE ticker = ?", (infoText, company_name, query,))
                db.commit()
                db.close()

            #if ticker is not in the db, create a record for it
            else:
                curs.execute("INSERT INTO stocks (ticker, exchange, type, currency, info, name) VALUES (?, ?, ?, ?, ?)", (query, metadata["exchangeCode"], 'Stock', 'USD', infoText, company_name))
                db.commit()
                db.close()

        # add metadata to result
        result.update({'info' : infoText,
                       'name' : company_name})

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

@app.route("/retrieveFavourite")
@login_required
def retrieve_favourite():

    user_id = session["user_id"]
    db = sqlite3.connect("database.db")

    #convert query results to dict
    db.row_factory = dict_factory
    user_favourites = []
    for row in db.execute("SELECT ticker, change FROM favourites where userid = ?", (user_id,)):
        user_favourites.append(row)
    db.close()

    return jsonify(user_favourites)

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
        if qType == "rm" and qCode:
            curs.execute("DELETE FROM favourites WHERE userid = ? AND ticker = ?", (user_id, qCode,))
            db.commit()            

        elif qType == "ad" and qCode:
        # if item is not in favourites, add to list & update change
            if not (curs.execute("SELECT * FROM favourites where userid = ? AND ticker = ?", (user_id, qCode,)).fetchall()):

                dateFromInit = datetime.date.today() - datetime.timedelta(days=7)
                dateFrom = dateFromInit.strftime('%Y-%m-%d')
            
                # set to todays date
                dateToInit = datetime.date.today() 
                dateTo = dateToInit.strftime('%Y-%m-%d')
                
                
                lastWeekData = retrieve_history(qCode, dateFrom, dateTo)
                try:
                    change = lastWeekData[len(lastWeekData) - 1]["close"] - lastWeekData[0]["open"]
                    changePercent = round((change / lastWeekData[0]["open"]) * 100, 3)
                except:
                    changePercent = 0

                curs.execute("INSERT INTO favourites (userid, ticker, change) VALUES (?, ?, ?)", (user_id, qCode, changePercent,))
                db.commit()   
                db.close()
                
    return redirect("/")

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
            
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', new_user["email"]):
            flash ("Please enter a valid email", "error")
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

    return render_template("info.html", userInfo = session["user_info"])

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

@app.route("/accdetails", methods = ["GET", "POST"])
@login_required
def details():

    if request.method == "POST":

        fname = request.form.get("fname")
        lname = request.form.get("lname")
        email = request.form.get("email")
        password = request.form.get("password")

        if not fname:
            fname = session["user_info"][0]["fname"]
        if not lname:
            lname = session["user_info"][0]["lname"]
        if not email:
            fname = session["user_info"][0]["email"]
        if not password:
            flash("Please enter your password", "error")
            return render_template("/accdetails.html", userInfo = session["user_info"])
        
        # email regex
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            flash ("Please enter a valid email", "error")
            return render_template("/accdetails.html", userInfo = session["user_info"])
        
        db = sqlite3.connect("database.db")
        curs = db.cursor()

        hash = curs.execute("SELECT hash FROM users WHERE userid = ?", (session["user_id"],)).fetchone()[0]
        if not check_password_hash(hash, password):
            flash("Incorrect Password", "error")
            return render_template("/accdetails.html", userInfo = session["user_info"])
        
        curs.execute("UPDATE users SET fname = ?, lname = ?, email = ? WHERE userid = ?", (fname, lname, email, session["user_id"],))
        db.commit()
                
        db.close()

        flash("Details updated", "success")
        return render_template("/info.html", userInfo = session["user_info"])
    
    return render_template("/accdetails.html", userInfo = session["user_info"])

@app.route("/portfolio", methods=["GET", "POST"])
@login_required
def portfolio():
    userid = session["user_id"]

    db = sqlite3.connect("database.db")
    curs = db.cursor()

    ### Account Info ###
    balance = curs.execute("SELECT balance FROM users WHERE userid = ?", (userid,)).fetchone()[0]
    deposits = curs.execute("SELECT * FROM transactions WHERE userid = ? AND transtype = 'deposit' LIMIT 8", (userid,)).fetchall()
    transactions = curs.execute("SELECT * FROM transactions WHERE userid = ? AND NOT transtype = 'deposit'", (userid,)).fetchall()
 
    totaldepo = 0
    for item in deposits:
        totaldepo += item[2]

    ### Portfolio Info ###
    holdings = curs.execute("SELECT * FROM holdings WHERE userid = ?", (userid,)).fetchall()

    # This next for loop determines which stocks need updating by compairing their last update to the current date
    stock_list = ""
    updated_price_info = []
    for stock in holdings:
        code = stock[2]
        date_result = curs.execute("SELECT datelog FROM pricelog WHERE code = ? ORDER BY datelog desc", (code,)).fetchone()[0]

        # check which stocks havent been updated yet today
        if date_result:
            last_update = datetime.date.fromisoformat(date_result)
            if last_update < datetime.date.today():
                stock_list += code + "," 

    # list of stocks not updated today
    stock_list = stock_list.rstrip(",")

    # this next block checks to see if the stock market has opened, and will therefore have new data
    # and then requests data for the list of stocks generated above
    if stock_list:        
        nowUTC = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%S")
        target = '14:00:00'
        if nowUTC > target:
            
            #API call - returns list of dictionaries
            updated_price_info = retrieve_stock_data(stock_list)
    else:
        print("no stock needs updating")

    total_value = 0
    holdings_grid = []
    # populating data for stock holdings
    for stock in holdings:
        #just for clarity
        code = stock[2]
        quant = stock[3]

        # pull data for each item from main API call
        result = next((item for item in IEXdata if item["ticker"] == code), None)
        total_value += result["tngoLast"] * quant

        # DATA FOR GRAPH       
        # This block iterates through the updated price data from above and checks if it differs from what is already stored
        # if it is different, the stored data is updated.
        if updated_price_info:
            portfolio_item = next((item for item in updated_price_info if item['ticker'] == code), None)
            if not portfolio_item:
                # if there is no updated data in the API call, break the loop
                # This can happen if someone else has updated part of the stock from your holdings list
                continue

            prev_close = portfolio_item["prevClose"]
            last_prev_close = curs.execute("SELECT price FROM pricelog WHERE code = ? ORDER BY datelog desc", (code,)).fetchone()[0]

            if not prev_close == last_prev_close:
                curs.execute("INSERT INTO pricelog (code, price) VALUES (?, ?)", (code, prev_close))
                db.commit()

        #total invested
        total_invested = float(curs.execute("SELECT SUM(value) FROM transactions WHERE userid = ? AND transtype = 'purchase' AND item = ?", (userid, code)).fetchone()[0])
        #total profit
        curr_value = float(result["tngoLast"] * quant)
        item_profit = float(curr_value - total_invested)

       # This block determines the % gain since you first purchased that stock
        start_date = curs.execute("SELECT timelog FROM transactions WHERE item = ? AND userid = ? AND transtype = 'purchase' ORDER BY timelog LIMIT 1", (code, userid,)).fetchone()[0]
        # this is a result of having an overly complex timestamp in the transactions log..
        start_date_obj = datetime.datetime.strptime(start_date[:10], '%d-%m-%Y')

        # if the most applicable price for price_init does not exist, it should use the most recent value available
        try:
            price_init = curs.execute("SELECT price FROM pricelog WHERE code = ? AND datelog >= ? ORDER BY datelog asc LIMIT 1", (code, start_date_obj.strftime('%Y-%m-%d'))).fetchone()[0]
        except:
            price_init = curs.execute("SELECT price FROM pricelog WHERE code = ? AND datelog <= ? ORDER BY datelog asc LIMIT 1", (code, start_date_obj.strftime('%Y-%m-%d'))).fetchone()[0]

        price_end = curs.execute("SELECT price FROM pricelog WHERE code = ? ORDER BY datelog desc LIMIT 1", (code,)).fetchone()[0]
        change_perc = ((price_end / price_init)-1)*100

        # Populate the holdings grid
        holdings_grid.append({
            "code" : code,
            "quant" : stock[3],
            "unitval" : result["tngoLast"],
            "itemval" : result["tngoLast"] * quant,
            "iteminvest" : round(total_invested, 2),
            "itemprofit" : round(item_profit, 2),
            "change" : round(change_perc, 4)
        })
        
    total_profit = total_value - totaldepo
    
    account_stats = {
        "balance" : balance,
        "totaldepo" : totaldepo,
        "totalvalue" : total_value,
        "totalprofit" : total_profit
    }
        
    db.close()
    return render_template("/portfolio.html", transactions = transactions, deposits = deposits, account_stats = account_stats, holdings_grid = holdings_grid)

@app.route("/portfoliograph")
@login_required
def portfolio_graph():
    userid = session["user_id"]
    code = request.args.get("code")

    db = sqlite3.connect("database.db")
    curs = db.cursor()

    # select results starting from the timelog of the users first purchase of the stock
    #### This wont work well if a user sells all their stock and then rebuys
    start_date = curs.execute("SELECT timelog FROM transactions WHERE item = ? AND userid = ? AND transtype = 'purchase' ORDER BY timelog LIMIT 1", (code, userid,)).fetchone()[0]
    
    # this is a result of having an overly complex timestamp in the transactions log..
    start_date_obj = datetime.datetime.strptime(start_date[:10], '%d-%m-%Y')
    price_results = curs.execute("SELECT price, datelog FROM pricelog WHERE code = ? AND datelog >= ? ORDER BY datelog asc", (code, start_date_obj.strftime('%Y-%m-%d'))).fetchall()
    
    # this needs to reflect the weird error from portfolio - if a user purchases stock that hasnt been updated yet that day it wont show anything
    if not price_results:
        price_results = curs.execute("SELECT price, datelog FROM pricelog WHERE code = ? AND datelog <= ? ORDER BY datelog asc", (code, start_date_obj.strftime('%Y-%m-%d'))).fetchall()
   
    db.close()
    
    data = []
    for item in price_results:
        data.append(
            {
                "date" : item[1],
                "price" : item[0]
            }
        )

    description = {
        "date" : ("string", "Date"),
        "price" : ("number", "Price")
    }

    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)

    graph_data = data_table.ToJSon(columns_order=("date", "price"))

    return graph_data

@app.route("/deposit", methods=["GET", "POST"])
@login_required
def deposit():
    userid = session["user_id"]

    if request.method == "POST":
        db = sqlite3.connect("database.db")
        curs = db.cursor()
        password = request.form.get("password")

        deposit = request.form.get("amount")
        if not deposit.isnumeric():
            db.close()
            flash("Please enter a valid amount to deposit", "error")
            return redirect("/portfolio")
        
        hash = curs.execute("SELECT hash FROM users WHERE userid = ?", (userid,)).fetchone()[0]

        if not check_password_hash(hash, password):
            db.close()
            flash("Incorrect Password", "error")
            return redirect("/portfolio")

        # If transaction not recorded succesfully
        if not curs.execute("INSERT INTO transactions (userid, value, transtype) VALUES (?, ?, ?)", (userid, deposit, "deposit",)):
            db.close()
            flash("Transaction could not be processed", "error")
            return redirect("/portfolio")
            
        # update balance
        balance = curs.execute("SELECT balance FROM users WHERE userid = ?", (userid,)).fetchone()[0]

        if not balance:
            balance = 0
        updated_balance = balance + int(deposit)

        # limit on balance to not upset sql
        if updated_balance > 10e20:
            db.close()
            flash("Transaction could not be processed", "error")
            return redirect("/portfolio")

        curs.execute("UPDATE users SET balance = ? WHERE userid = ?", (updated_balance, userid,))
        db.commit()
        db.close()
                
    return redirect("/portfolio")

@app.route("/buy", methods=["POST", "GET"])
@login_required
def buy():
    userid = session["user_id"]

    code = request.form.get("code").upper()
    quant = request.form.get("buy_quant")

    if not code:
        flash("Please enter a code to purchase", "error")
        return redirect("/")
    if not quant:
        flash("Please enter a quantity", "error")
        return redirect("/")
    
    # check if quant has any non numeric characters
    if not quant.isnumeric():
        flash("Please enter a valid quantity", "error")
        return redirect("/")
    
    if quant == "0":
        flash("You cant buy nothing!", "error")
        return redirect("/")
    
    db = sqlite3.connect("database.db")
    curs = db.cursor()

    code_list = curs.execute("SELECT ticker FROM stocks WHERE ticker LIKE ?", (code + "%",)).fetchall()

    # check if ticker code exists in db
    if not code_list or not code in code_list[0]:
        flash("Please enter a valid code", "error")
        db.close()
        return redirect("/")
    
    
    # get last trade price from iexdata
    result = next((item for item in IEXdata if item["ticker"] == code), None)

    # if the stock price cannot be retrieved
    if not result:
        flash("This stock could not be found", "error")
        return redirect("/")
    
    totalprice = int(quant) * float(result["tngoLast"])
    balance = curs.execute("SELECT balance FROM users WHERE userid = ?", (userid,)).fetchone()[0]

    # check balance
    if not totalprice <= balance:
        flash("Insufficient Funds", "error")
        db.close()
        return redirect("/")
    
    updated_balance = balance - totalprice
    
    #submit changes to db
    try:
        curs.execute("UPDATE users SET balance = ? WHERE userid = ?", (updated_balance, userid,))
        curs.execute("INSERT INTO transactions (userid, value, transtype, item, quantity) VALUES (?, ?,'purchase', ?, ?)", (userid, totalprice, code, quant,))
    except:
        flash("Something went wrong with the purchase", "error")
        db.close()
        return redirect("/")
    db.commit()

    #update users holdings table
    holdings = curs.execute("SELECT * FROM holdings WHERE userid = ?", (userid,)).fetchall()
    
    # if user has no holdings
    if len(holdings) == 0:
        curs.execute("INSERT INTO holdings (userid, stock, quantity) VALUES(?, ?, ?)", (userid, code, quant))        
        db.commit()

    # if user has holdings
    else:
        for item in holdings:
            # Update held stock quant if user already has stock
            if code == item[2]:
                held_stock = curs.execute("SELECT quantity FROM holdings WHERE stock = ? AND userid = ?", (code, userid,)).fetchone()[0]
                new_quant = held_stock + int(quant)

                curs.execute("UPDATE holdings SET quantity = ? WHERE stock = ? AND userid = ?", (new_quant, code, userid))
                db.commit()
                break
        # Update held stock quant if user does not aleady have that stock
        else:
            curs.execute("INSERT INTO holdings (userid, stock, quantity) VALUES(?, ?, ?)", (userid, code, quant))
            db.commit()

    ## first entry into pricelog table ##

    pricelog = curs.execute("SELECT * FROM pricelog WHERE code = ?", (code,)).fetchall()  

    # if stock is not in pricelog table, create and log first price
    if not pricelog:
        stock_data = retrieve_stock_data(code)
        pricelog_price = stock_data[0]["prevClose"]

        curs.execute("INSERT INTO pricelog (code, price) VALUES(?, ?)", (code, pricelog_price))
        db.commit()

    db.close()
    flash("Purchase Succesful", "success")
    
    return redirect("/")

@app.route("/sell", methods=["POST", "GET"]) 
@login_required
def sell():
    userid = session["user_id"]

    code = request.form.get("code").upper()
    quant = request.form.get("sell_quant")

    if not code:
        flash("Please enter a code to sell", "error")
        return redirect("/")
    if not quant:
        flash("Please enter a quantity", "error")
        return redirect("/")
    
    # check if quant has any non numeric characters
    if not quant.isnumeric():
        flash("Please enter a valid quantity", "error")
        return redirect("/")
    
    if quant == "0":
        flash("You cant sell nothing!", "error")
        return redirect("/")
    
    db = sqlite3.connect("database.db")
    curs = db.cursor()

    # get list of stocks we hold
    code_list = curs.execute("SELECT stock FROM holdings WHERE userid = ?", (userid,)).fetchall()

    # check if ticker code exists in list of our holdings
    if not code_list or not code in code_list[0]:
        flash("Please enter a valid code", "error")
        db.close()
        return redirect("/")
    
    held_quant = curs.execute("SELECT quantity FROM holdings WHERE stock = ? AND userid = ?", (code, userid,)).fetchone()[0]
    
    # preview sale price?

    # check quant
    if int(quant) > held_quant:
        flash("You do not hold enough stock to sell this amount", "error")
        db.close()
        redirect("/")

    # remove stock from holdings - deleting entry if quant is 0
    new_held_quant = held_quant - int(quant)
    if new_held_quant == 0:
        curs.execute("DELETE FROM holdings WHERE userid = ? AND stock = ?", (userid, code,))
    else:
        curs.execute("UPDATE holdings SET quantity = ? WHERE userid = ? AND stock = ?", (new_held_quant, userid, code,))
        
    # get last trade price from iexdata
    result = next((item for item in IEXdata if item["ticker"] == code), None)

    totalprice = int(quant) * float(result["tngoLast"])
    
    # increase account balance
    balance = curs.execute("SELECT balance FROM users WHERE userid = ?", (userid,)).fetchone()[0]
    new_balance = balance + totalprice
    curs.execute("UPDATE users SET balance = ? WHERE userid = ?", (new_balance, userid,))

    # record in transaction log
    curs.execute("INSERT INTO transactions (userid, value, transtype, item, quantity) VALUES(?, ?, 'sell', ?, ?)", (userid, totalprice, code, quant,))
    db.commit()

    db.close()        
    flash("Sale Succesful", "success")

    return redirect("/")

@app.route("/news")
@login_required
def news():

    qCode = request.args.get("q")
    dateFrom = request.args.get("from") 
    dateTo = request.args.get("to")

    #include a default date range if date is not set
    if not dateFrom and not dateTo:
        # set to 4 weeks ago
        dateFromInit = datetime.date.today() - datetime.timedelta(days=28)
        dateFrom = dateFromInit.strftime('%Y-%m-%d')

        # set to todays date
        dateToInit = datetime.date.today() 
        dateTo = dateToInit.strftime('%Y-%m-%d')

    newstext = retrieve_news(qCode, dateFrom, dateTo)
    return newstext


@app.route("/logout")
def logout():

    session.clear()
    return redirect("/")
