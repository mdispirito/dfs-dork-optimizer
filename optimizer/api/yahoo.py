import requests


class YahooApi(object):
    endpoint = "https://dfyql-ro.sports.yahoo.com/v2"
    enabled_sports = ["nba"]

    def __init__(self):
        pass

    @classmethod
    def get_contests(cls, sport: str) -> requests.Response:
        sport = sport.lower()
        if sport not in cls.enabled_sports:
            raise Exception(f"Sport is not available: {sport}")

        return requests.get(f"{cls.endpoint}/contestsFilteredWeb?&sport={sport}")

    @classmethod
    def get_players(cls, contest_id) -> requests.Response:
        return requests.get(f"{cls.endpoint}/contestPlayers?contestId={contest_id}")
