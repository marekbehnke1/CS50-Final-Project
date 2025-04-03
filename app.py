import os

from helpers import login_required

from flask import Flask, render_template, session, request, redirect, flash
from flask_session import Session

import sqlite3 

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Database connection


@app.route("/")
@login_required
def index():

    if session["user_id"]:
        return render_template("layout.html")
    else:
        redirect("/login")


@app.route("/login" , methods=["GET", "POST"])
def login():

    #clear any session info
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            flash("Please enter a username")
            return render_template("login.html")
        
        if not request.form.get("password"):
            flash("Please enter a password")
            return render_template("login.html")
        
        # Query database for username

            #if username exists, attempt to match against password
        
        # if login details ok - set session id
        session["user_id"] = 1 #db query userid
        return redirect("/")
    else:
        return render_template("login.html")
    
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        # username check
        uname = request.form.get("username")
        if not uname:
            flash("Please enter a username")
            return render_template("register.html")

        # fname check
        fname = request.form.get("fname")
        if not fname:
            flash("Please enter a name")
            return render_template("register.html")
        
        # lname check
        lname = request.form.get("lname")
        if not lname:
            flash("Please enter your last name")
            return render_template("register.html")
        
        # email check
        email = request.form.get("email")
        if not email:
            flash("Please enter email")
            return render_template("register.html")
        
        # Password Check
        hash = generate_password_hash(request.form.get("password"))
        if not hash:
            flash("Please enter a password")
            return render_template("register.html")
        
        if request.form.get("password") == request.form.get("password_check"):

            db = sqlite3.connect("database.db")
            curs = db.cursor()

            # check if any error occured on db entry
            try:
                curs.execute("INSERT INTO users (username, fname, lname, email, hash) VALUES (?, ?, ?, ?, ?)", (uname, fname, lname, email, hash))
            except:
                db.close()
                flash("Username already exists")
                return render_template("register.html")
            else:
                db.commit()
                db.close
                return redirect("/login")
        
        else:
            flash("Passwords did not match")
            return render_template("register.html")

    else:
         return render_template("register.html")

@app.route("/logout")
def logout():

    session.clear()
    return redirect("/")