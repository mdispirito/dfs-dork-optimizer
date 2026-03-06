import requests

YAHOO_DFS_API = "https://dfyql-ro.sports.yahoo.com/v2"
ENABLED_SPORTS = {"nba"}


def get_contests(sport: str) -> dict:
    sport = sport.lower()
    if sport not in ENABLED_SPORTS:
        raise ValueError(f"Sport not available: {sport}")

    response = requests.get(f"{YAHOO_DFS_API}/contestsFilteredWeb?sport={sport}")
    response.raise_for_status()
    return response.json()


def get_players(contest_id: str) -> list[dict]:
    response = requests.get(f"{YAHOO_DFS_API}/contestPlayers?contestId={contest_id}")
    response.raise_for_status()
    return response.json()["players"]["result"]
