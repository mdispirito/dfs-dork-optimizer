import csv
import io
import os

import requests
from dotenv import load_dotenv
from pydfs_lineup_optimizer import Site, Sport, get_optimizer

from optimizer.adapters.yahoo import YahooAdapter
from optimizer.util.player import generate_player_id

load_dotenv()


class DfsDorkOptimizer:

    def __init__(self, site: Site, sport: Sport):
        self.lineup_optimizer = get_optimizer(site, sport)

    def load_yahoo_players(self, yahoo_player_pool):
        players = YahooAdapter(yahoo_player_pool).convert()
        self.lineup_optimizer.player_pool.load_players(players)

    def load_external_projections(self):
        """
        Replace each player's FPPG with a value
        based on external stat projections.
        """
        external_projection_url = os.getenv("EXTERNAL_PROJECTIONS")
        if not external_projection_url:
            raise ValueError("EXTERNAL_PROJECTIONS environment variable not set")

        projections = requests.get(external_projection_url)
        reader = csv.DictReader(io.StringIO(projections.text))

        for row in reader:
            player_id = generate_player_id(row["first_name"], row["last_name"], row["team"])
            player = self.lineup_optimizer.player_pool.get_player_by_id(player_id)

            if player:
                points = float(row["points"])
                rebounds = float(row["rebounds"]) * 1.2
                assists = float(row["assists"]) * 1.5
                steals = float(row["steals"]) * 3
                blocks = float(row["blocks"]) * 3
                turnovers = float(row["turnovers"]) * -1
                player.fppg = points + rebounds + assists + steals + blocks + turnovers

    def get_optimized_lineups(self, number_of_lineups):
        return self.lineup_optimizer.optimize(number_of_lineups)
