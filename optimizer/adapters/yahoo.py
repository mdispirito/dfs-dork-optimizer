from pydfs_lineup_optimizer import Player

from optimizer.util.player import generate_player_id


def convert_yahoo_players(yahoo_player_pool: list[dict]) -> list[Player]:
    """Convert Yahoo DFS player data to pydfs-lineup-optimizer Player objects."""
    return [
        Player(
            player_id=generate_player_id(p["firstName"], p["lastName"], p["teamAbbr"]),
            first_name=p["firstName"],
            last_name=p["lastName"],
            positions=p["eligiblePositions"],
            team=p["teamAbbr"],
            salary=p["salary"],
            fppg=p["fantasyPointsPerGame"],
        )
        for p in yahoo_player_pool
    ]
