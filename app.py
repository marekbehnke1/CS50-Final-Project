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

#### Routes #####
@app.route("/")
@login_required
def index():
    user_id = session["user_id"]

    # set data to sort
    differenceData = {}
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

        
    db = sqlite3.connect("database.db")
    curs = db.cursor()

    differenceDataSorted = sort_data("difference", 9, differenceData)
    for item in differenceDataSorted:
        company_name = curs.execute("SELECT name FROM stocks WHERE ticker = ?", (item["ticker"],)).fetchall()[0][0]
        if not company_name:
            company_name = retrieve_metadata(item["ticker"])["name"]
            curs.execute("UPDATE stocks SET name = ? WHERE ticker = ?", (company_name, item["ticker"]))
            db.commit()
        item.update({"name" : company_name})

    differenceDataReverse = sort_data("difference", 9, differenceData, False)
    for item in differenceDataReverse:
        company_name = curs.execute("SELECT name FROM stocks WHERE ticker = ?", (item["ticker"],)).fetchall()[0][0]
        if not company_name:
            company_name = retrieve_metadata(item["ticker"])["name"]
            curs.execute("UPDATE stocks SET name = ? WHERE ticker = ?", (company_name, item["ticker"]))
            db.commit()
        item.update({"name" : company_name})

    # retrieve favourites
    db = sqlite3.connect("database.db")

    #convert to list of dict
    db.row_factory = dict_factory
    favouritesList = []
    for row in db.execute("SELECT DISTINCT favourites.ticker, change, name FROM favourites INNER JOIN stocks on favourites.ticker = stocks.ticker WHERE userid = ?", (user_id,)):
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
        return render_template("index.html", differenceData = differenceDataSorted, differenceDataReverse = differenceDataReverse, favouritesList = favouritesList)
    else:
        redirect("/login")

@app.route("/differencepanel")
@login_required
def diff_panel():

    differenceData = {}
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

    list_type = request.args.get("q")
    db = sqlite3.connect("database.db")
    curs = db.cursor()

    if list_type == "winners":

        differenceDataSorted = sort_data("difference", 9, differenceData)
        for item in differenceDataSorted:
            company_name = curs.execute("SELECT name FROM stocks WHERE ticker = ?", (item["ticker"],)).fetchall()[0][0]
            if not company_name:
                company_name = retrieve_metadata(item["ticker"])["name"]
                curs.execute("UPDATE stocks SET name = ? WHERE ticker = ?", (company_name, item["ticker"]))
                db.commit()
            item.update({"name" : company_name})

        db.close()
        return differenceDataSorted


    elif list_type == "losers":

        differenceDataReverse = sort_data("difference", 9, differenceData, False)
        for item in differenceDataReverse:
            company_name = curs.execute("SELECT name FROM stocks WHERE ticker = ?", (item["ticker"],)).fetchall()[0][0]
            if not company_name:
                company_name = retrieve_metadata(item["ticker"])["name"]
                curs.execute("UPDATE stocks SET name = ? WHERE ticker = ?", (company_name, item["ticker"]))
                db.commit()
            item.update({"name" : company_name})

        db.close()
        return differenceDataReverse
        

@app.route("/stock")
@login_required
def info_page():

    query = request.args.get("q")
    if query:

        # loop through IEXdata for a dict where dict["ticker"] == the query
        result = next((item for item in IEXdata if item["ticker"] == query), None)
        if not result:
            result = {}
            result["info"] = "No information was available for this stock"
            return jsonify(result)

        # check database to see if meta data text exists
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
    for row in db.execute("SELECT DISTINCT favourites.ticker, change, name FROM favourites INNER JOIN stocks on favourites.ticker = stocks.ticker WHERE userid = ?", (user_id,)):
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
        
        db = sqlite3.connect("database.db")
        cur = db.cursor()

        try:
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
        db = sqlite3.connect("database.db")
        curs = db.cursor()

        # check if any error occured on db entry
        try:
            curs.execute("INSERT INTO users (username, fname, lname, email, hash, balance) VALUES (?, ?, ?, ?, ?, 10000)",
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

@app.route("/emailupdate", methods = ["GET", "POST"])
@login_required
def email():

    if request.method == "POST":

        email = request.form.get("newEmail")
        password = request.form.get("password")

        if not email:
            flash("Please enter a new email", "error")
            return render_template("/emailupdate.html", userInfo = session["user_info"])
                    
        if not password:
            flash("Please enter your password", "error")
            return render_template("/emailupdate.html", userInfo = session["user_info"])
        
        # email regex
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            flash ("Please enter a valid email", "error")
            return render_template("/emailupdate.html", userInfo = session["user_info"])
        
        db = sqlite3.connect("database.db")
        curs = db.cursor()

        hash = curs.execute("SELECT hash FROM users WHERE userid = ?", (session["user_id"],)).fetchone()[0]
        if not check_password_hash(hash, password):
            flash("Incorrect Password", "error")
            return render_template("/emailupdate.html", userInfo = session["user_info"])
        
        curs.execute("UPDATE users SET email = ? WHERE userid = ?", (email, session["user_id"],))
        db.commit()
                
        db.close()

        flash("Email updated", "success")
        return redirect("/account")
    
    return render_template("/emailupdate.html", userInfo = session["user_info"])

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

    # determines which stocks need updating by comparing their last update to the current date
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

        # iterate through the updated price data from above and checks if it differs from what is already stored
        # if it is different, update
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
        start_date_obj = datetime.datetime.strptime(start_date[:10], '%d-%m-%Y')

        # if the most applicable price for price_init does not exist, it should use the most recent value available
        try:
            price_init = curs.execute("SELECT price FROM pricelog WHERE code = ? AND datelog >= ? ORDER BY datelog asc LIMIT 1", (code, start_date_obj.strftime('%Y-%m-%d'))).fetchone()[0]
        except:
            price_init = curs.execute("SELECT price FROM pricelog WHERE code = ? AND datelog <= ? ORDER BY datelog desc LIMIT 1", (code, start_date_obj.strftime('%Y-%m-%d'))).fetchone()[0]

        price_end = curs.execute("SELECT price FROM pricelog WHERE code = ? ORDER BY datelog desc LIMIT 1", (code,)).fetchone()[0]
        change_perc = ((price_end / price_init)-1)*100

        # Populate the holdings grid
        holdings_grid.append({
            "code" : code,
            "quant" : stock[3],
            "unitval" : result["tngoLast"],
            "itemval" : round(result["tngoLast"] * quant, 2),
            "iteminvest" : round(total_invested, 2),
            "itemprofit" : round(item_profit, 2),
            "change" : round(change_perc, 4)
        })

    dbleaderboard = curs.execute("SELECT username, balance FROM users ORDER by balance desc LIMIT 20").fetchall()
    leaderboard = []
    for item in dbleaderboard:
        leaderboard.append(
            [dbleaderboard.index(item)+1,item[0], item[1]]
        )

    uname = curs.execute("SELECT username from users where userid = ?", (userid,)).fetchone()[0]

    for item in leaderboard:
        if item[1] == uname:
            rank = item[0]
            break

    total_profit = total_value - totaldepo
    
    account_stats = {
        "balance" : balance,
        "totaldepo" : totaldepo,
        "totalvalue" : total_value,
        "totalprofit" : total_profit,
        "leaderboard" : rank
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
    #### Todo: This wont work well if a user sells all their stock and then rebuys
    start_date = curs.execute("SELECT timelog FROM transactions WHERE item = ? AND userid = ? AND transtype = 'purchase' ORDER BY timelog LIMIT 1", (code, userid,)).fetchone()[0]
    
    start_date_obj = datetime.datetime.strptime(start_date[:10], '%d-%m-%Y')
    price_results = curs.execute("SELECT price, datelog FROM pricelog WHERE code = ? AND datelog >= ? ORDER BY datelog asc", (code, start_date_obj.strftime('%Y-%m-%d'))).fetchall()
    
    if not price_results:
        price_results = curs.execute("SELECT price, datelog FROM pricelog WHERE code = ? AND datelog <= ? ORDER BY datelog desc", (code, start_date_obj.strftime('%Y-%m-%d'))).fetchall()
   
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

@app.route("/buy", methods=["POST", "GET"])
@login_required
def buy():
    userid = session["user_id"]

    code = request.form.get("code").upper()
    quant = request.form.get("buy_quant")
    trans_type = request.form.get("type")

    print(type("shares"))
    if not code:
        flash("Please enter a code to purchase", "error")
        return redirect("/")
    if not quant:
        flash("Please enter a quantity", "error")
        return redirect("/")
    if not trans_type or trans_type not in ("value", "shares"):
        flash("Please select a transaction type", "error")
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
    
    if trans_type == "value":

        # the amount to spend is entered in the quant field
        totalprice = float(quant)

        num_shares = totalprice/result["tngoLast"]

        # Check if the number of shares is > 1 and a whole number
        if num_shares > 0 and num_shares % 1 == 0:
            quant = num_shares
            totalprice = int(quant) * float(result["tngoLast"])
        else:
            flash("Cannot purchase a fraction of a share", "error")
            db.close()
            return redirect("/")

    if trans_type == "shares":
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
    trans_type = request.form.get("type")

    if not code:
        flash("Please enter a code to sell", "error")
        return redirect("/")
    if not quant:
        flash("Please enter a quantity", "error")
        return redirect("/")
    if not trans_type or trans_type not in ("value", "shares"):
        flash("Please select a transaction type", "error")
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
    
    # get last trade price from iexdata
    result = next((item for item in IEXdata if item["ticker"] == code), None)

    if trans_type == "shares":
        totalprice = int(quant) * float(result["tngoLast"])

    if trans_type == "value":
        # the amount to spend is entered in the quant field
        totalprice = float(quant)

        num_shares = totalprice/result["tngoLast"]

        # Check if the number of shares is > 1 and a whole number
        if num_shares > 0 and num_shares % 1 == 0:
            quant = num_shares
            totalprice = int(quant) * float(result["tngoLast"])
        else:
            flash("Cannot purchase a fraction of a share", "error")
            db.close()
            return redirect("/")
        
    held_quant = curs.execute("SELECT quantity FROM holdings WHERE stock = ? AND userid = ?", (code, userid,)).fetchone()[0]

    # check quant
    if int(quant) > held_quant:
        flash("You do not hold enough stock to sell this amount", "error")
        db.close()
        return redirect("/")

    # remove stock from holdings - deleting entry if quant is 0
    new_held_quant = held_quant - int(quant)
    if new_held_quant == 0:
        curs.execute("DELETE FROM holdings WHERE userid = ? AND stock = ?", (userid, code,))
    else:
        curs.execute("UPDATE holdings SET quantity = ? WHERE userid = ? AND stock = ?", (new_held_quant, userid, code,))
    
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

@app.route("/preview")
@login_required
def price_preview():

    code = request.args.get("code").upper()
    trans_type = request.args.get("type")
    quant = request.args.get("quant")

    result = ""

    if not code or not trans_type or not quant:
        result = "Invalid Data"
        return jsonify(result)        
    
    if not quant.isnumeric():
        result = "Invalid Data"
        return jsonify(result)        

    stock_item = next((item for item in IEXdata if item["ticker"] == code), None)
    try:
        last_price = stock_item["tngoLast"]
    except:
        result = "Cannot find stock"
        return jsonify(result)
    else:
        if trans_type == "shares":

            result = "£" + str(float(quant) * float(last_price))

        if trans_type == "value":

            result = float(quant)/float(last_price)

            if not result % 1 == 0:
                result = "Cannot trade fractional shares"
                return jsonify(result)

            result = str(round(result,3)) + " shares"

        return jsonify(result)

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

@app.route("/leaderboard")
@login_required
def leaderboard():
    
    db = sqlite3.connect("database.db")
    curs = db.cursor()

    dbleaderboard = curs.execute("SELECT username, balance FROM users ORDER by balance desc LIMIT 20").fetchall()
    leaderboard = []
    for item in dbleaderboard:
        leaderboard.append(
            [dbleaderboard.index(item)+1,item[0], item[1]]
        )
    return render_template("/leaderboard.html", leaderboard = leaderboard)

@app.route("/logout")
def logout():

    session.clear()
    return redirect("/")
