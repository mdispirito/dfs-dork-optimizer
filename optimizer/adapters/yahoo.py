from pydfs_lineup_optimizer import Player
from util.player import generate_player_id


class YahooAdapter(object):

    def __init__(self, yahoo_player_pool):
        self.players = yahoo_player_pool

    def convert(self) -> list[Player]:
        converted_players = []

        for player in self.players:
            first_name = player.get("firstName")
            last_name = player.get("lastName")
            team = player.get("teamAbbr")
            player_id = generate_player_id(first_name, last_name, team)

            positions = player.get("eligiblePositions")
            salary = player.get("salary")
            fppg = player.get("fantasyPointsPerGame")

            converted_players.append(
                Player(
                    player_id=player_id,
                    first_name=first_name,
                    last_name=last_name,
                    positions=positions,
                    team=team,
                    salary=salary,
                    fppg=fppg
                )
            )

        return converted_players
