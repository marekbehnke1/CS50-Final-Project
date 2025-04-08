import os

from helpers import login_required, retrieve_iex, sort_data, format

from flask import Flask, render_template, session, request, redirect, flash
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
IEXdata = retrieve_iex()

#### Routes #####
@app.route("/")
@login_required
def index():

    # set the data to sort
    volumeData = {}
    for item in IEXdata:
        volumeData[item["ticker"]] = item["volume"]

    volumeDataSorted = sort_data("volume", 15, volumeData)

    # set data to sort
    differenceData = {}
    # check if fields are empty & set to 0
    for item in IEXdata:
        if item["mid"] == None:
            midPrice = 0
        else:
            midPrice = item["mid"]
        if item["open"] == None:
            open = 0
        else:
            open = item["open"]

        differenceData[item["ticker"]] = open - midPrice

    differenceDataSorted = sort_data("difference", 20, differenceData)
    differenceDataReverse = sort_data("difference", 20, differenceData, False)



    if session["user_id"]:
        return render_template("index.html", volumeData = volumeDataSorted, differenceData = differenceDataSorted, differenceDataReverse = differenceDataReverse)
    else:
        redirect("/login")


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
def account():

    return render_template("account.html")


@app.route("/logout")
def logout():

    session.clear()
    return redirect("/")



