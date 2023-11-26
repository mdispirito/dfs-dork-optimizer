from flask import Flask

app = Flask(__name__)


@app.route("/contests")
def get_constests():
    return "contests"


@app.route("/<contest_id>/players")
def get_players():
    return "players for a given contest"
