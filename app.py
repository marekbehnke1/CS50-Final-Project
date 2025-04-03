import os

from helpers import login_required

from flask import Flask, render_template, session, request, redirect, flash
from flask_session import Session

from sqlalchemy import create_engine
import sqlite3 

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

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

@app.route("/logout")
def logout():

    this = "is for testing"
    session.clear()
    return redirect("/")