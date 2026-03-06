from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from pydfs_lineup_optimizer import Site, Sport

from optimizer.api import yahoo as yahoo_api
from optimizer.optimizer import DfsDorkOptimizer

app = Flask(__name__)
CORS(app)


@app.route("/api/contests")
def get_contests():
    try:
        return yahoo_api.get_contests(sport="nba")
    except Exception as e:
        return Response(response=f"Unable to get contests: {e}", status=500)


@app.route("/api/<contest_id>/players")
def get_players(contest_id):
    try:
        return yahoo_api.get_players(contest_id=contest_id)
    except Exception as e:
        return Response(response=f"Unable to get players for contest {contest_id}: {e}", status=500)


@app.route("/api/optimized_lineup", methods=["POST"])
def optimize_lineups():
    try:
        body = request.get_json()

        optimizer = DfsDorkOptimizer(site=Site.YAHOO, sport=Sport.BASKETBALL)
        optimizer.load_yahoo_players(body["player_pool"])

        if body.get("load_external_projections"):
            optimizer.load_external_projections()

        optimizer.exclude_players(body.get("excluded_players", []))
        optimizer.lock_players(body.get("locked_players", []))

        lineups = optimizer.optimize(body.get("lineups", 1))
        return jsonify([str(lineup) for lineup in lineups])
    except Exception as e:
        return Response(response=f"Unable to optimize lineups: {e}", status=500)


if __name__ == "__main__":
    app.run(debug=True, port=8080)
