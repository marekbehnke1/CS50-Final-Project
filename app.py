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
        uname = request.form.get("username")
        if not uname:
            flash("Please enter a username")
            return render_template("login.html")
        password = request.form.get("password")
        if not password:
            flash("Please enter a password")
            return render_template("login.html")
        
        # Query database for username
        db = sqlite3.connect("database.db")
        cur = db.cursor()

        try:
            # this is a horrible way of expressing this - need it to return a list or something
            userid = cur.execute("SELECT userid FROM users WHERE username = ?", (uname,)).fetchone()[0]
        except TypeError:
            db.close()
            flash("Username does not exist")
            return render_template("login.html")
        else:
            #if username exists, attempt to match against password
            hash = cur.execute("SELECT hash FROM users WHERE userid = ?", (userid,)).fetchone()[0] 
            db.close()
            
            if not check_password_hash(hash, password):
                flash("Incorrect password")
                return render_template("login.html")
            
            # if login details ok - set session id
            session["user_id"] = userid
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