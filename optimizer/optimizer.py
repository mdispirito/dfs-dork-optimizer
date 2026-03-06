import csv
import io
import os

import requests
from dotenv import load_dotenv
from pydfs_lineup_optimizer import Site, Sport, get_optimizer

from optimizer.adapters.yahoo import convert_yahoo_players
from optimizer.util.player import generate_player_id

load_dotenv()

# Yahoo DFS fantasy point scoring weights
YAHOO_NBA_SCORING = {
    "points": 1,
    "rebounds": 1.2,
    "assists": 1.5,
    "steals": 3,
    "blocks": 3,
    "turnovers": -1,
}


class DfsDorkOptimizer:

    def __init__(self, site: Site, sport: Sport):
        self.lineup_optimizer = get_optimizer(site, sport)

    def load_yahoo_players(self, yahoo_player_pool: list[dict]):
        players = convert_yahoo_players(yahoo_player_pool)
        self.lineup_optimizer.player_pool.load_players(players)

    def load_external_projections(self):
        """Replace each player's FPPG with projected fantasy points from an external source."""
        url = os.getenv("EXTERNAL_PROJECTIONS")
        if not url:
            raise ValueError("EXTERNAL_PROJECTIONS environment variable not set")

        response = requests.get(url)
        response.raise_for_status()
        reader = csv.DictReader(io.StringIO(response.text))

        for row in reader:
            player_id = generate_player_id(row["first_name"], row["last_name"], row["team"])
            player = self.lineup_optimizer.player_pool.get_player_by_id(player_id)

            if player:
                player.fppg = sum(
                    float(row[stat]) * weight
                    for stat, weight in YAHOO_NBA_SCORING.items()
                )

    def exclude_players(self, player_names: list[str]):
        for name in player_names:
            self.lineup_optimizer.player_pool.remove_player(name)

    def lock_players(self, player_names: list[str]):
        for name in player_names:
            self.lineup_optimizer.player_pool.lock_player(name)

    def optimize(self, num_lineups: int = 1):
        return list(self.lineup_optimizer.optimize(num_lineups))
