import requests


class YahooApi(object):
    ENDPOINT = "https://dfyql-ro.sports.yahoo.com/v2"

    def __init__(self):
        pass

    @classmethod
    def get_contests(cls, sport):
        return requests.get(f"{cls.ENDPOINT}/contestsFilteredWeb?&sport={sport}")

    @classmethod
    def get_players(cls, contest_id):
        return requests.get(f"{cls.ENDPOINT}/contestPlayers?contestId={contest_id}")
