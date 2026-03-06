from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from pydfs_lineup_optimizer import Site, Sport

from optimizer.api.yahoo import YahooApi
from optimizer.optimizer import DfsDorkOptimizer


SPORT = "nba"
app = Flask(__name__)
CORS(app)


@app.route("/api/contests")
def get_contests():
    try:
        return YahooApi.get_contests(sport=SPORT).json()
    except Exception as e:
        return Response(response=f"Unable to get contests: {e}", status=500)


@app.route("/api/<contest_id>/players")
def get_players(contest_id):
    try:
        return YahooApi.get_players(contest_id=contest_id).json()["players"]["result"]
    except Exception as e:
        return Response(response=f"Unable to get players for contest {contest_id}: {e}", status=500)


@app.route("/api/optimized_lineup", methods=["POST"])
def get_optimized_lineups():
    try:
        body = request.get_json()
        yahoo_player_pool = body["player_pool"]
        lineups = body.get("lineups", 1)
        load_external_projections = body.get("load_external_projections", False)
        excluded_players = body.get("excluded_players", [])
        locked_players = body.get("locked_players", [])

        optimizer = DfsDorkOptimizer(site=Site.YAHOO, sport=Sport.BASKETBALL)
        optimizer.load_yahoo_players(yahoo_player_pool)

        if load_external_projections:
            optimizer.load_external_projections()

        for player_name in excluded_players:
            optimizer.lineup_optimizer.player_pool.remove_player(player_name)

        for player_name in locked_players:
            optimizer.lineup_optimizer.player_pool.lock_player(player_name)

        results = list(optimizer.get_optimized_lineups(lineups))
        return jsonify([str(lineup) for lineup in results])
    except Exception as e:
        return Response(response=f"Unable to optimize lineups: {e}", status=500)


if __name__ == "__main__":
    app.run(debug=True, port=8080)
