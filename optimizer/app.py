from flask import Flask, Response

from pydfs_lineup_optimizer import Site, Sport
from api.yahoo import YahooApi
from optimizer import DfsDorkOptimizer


SPORT = "nba"
app = Flask(__name__)


@app.route("/contests")
def get_constests():
    try:
        return YahooApi.get_contests(sport=SPORT).json()
    except:
        return Response(response="Unable to get contests", status=500)


@app.route("/<contest_id>/players")
def get_players(contest_id):
    try:
        return YahooApi.get_players(contest_id=contest_id).json()["players"]["result"]
    except:
        return Response(response=f"Unable to get players for contest {contest_id}", status=500)


@app.route("/optimize")
def get_optimized_lineups(yahoo_player_pool, lineups=1, load_external_projections=False):
    try:
        optimizer = DfsDorkOptimizer(site=Site.YAHOO, sport=Sport.BASKETBALL)
        optimizer.load_yahoo_players(yahoo_player_pool)

        if load_external_projections:
            optimizer.load_external_projections()

        return optimizer.get_optimized_lineups(lineups)
    except:
        return Response(response=f"Unable to optimize lineups", status=500) 


if __name__ == "__main__":
    # contests = YahooApi.get_contests(sport="nba")
    TEST_CONTEST = "13364370"

    optimizer = DfsDorkOptimizer(site=Site.YAHOO, sport=Sport.BASKETBALL)
    contest_players = YahooApi.get_players(contest_id=TEST_CONTEST).json()["players"]["result"]
    optimizer.load_yahoo_players(contest_players)
    optimizer.load_external_projections()

    optimized_lineups = optimizer.get_optimized_lineups(1)
    for lineup in optimized_lineups:
        print(lineup)
