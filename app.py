from flask import Flask, render_template
app = Flask(__name__)

message = "hello?"

@app.route("/")
def main():

    return message