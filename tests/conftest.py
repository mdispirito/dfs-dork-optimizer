import pytest

from optimizer.app import app as flask_app


SAMPLE_YAHOO_PLAYERS = [
    {
        "firstName": "LeBron",
        "lastName": "James",
        "teamAbbr": "LAL",
        "eligiblePositions": ["SF", "PF"],
        "salary": 45,
        "fantasyPointsPerGame": 50.0,
    },
    {
        "firstName": "Stephen",
        "lastName": "Curry",
        "teamAbbr": "GSW",
        "eligiblePositions": ["PG", "SG"],
        "salary": 42,
        "fantasyPointsPerGame": 47.5,
    },
    {
        "firstName": "Jaren",
        "lastName": "Jackson Jr.",
        "teamAbbr": "MEM",
        "eligiblePositions": ["PF", "C"],
        "salary": 35,
        "fantasyPointsPerGame": 38.0,
    },
]

SAMPLE_PROJECTIONS_CSV = (
    "first_name,last_name,team,points,rebounds,assists,steals,blocks,turnovers\n"
    "LeBron,James,LAL,27.0,7.0,7.0,1.2,0.8,3.5\n"
    "Stephen,Curry,GSW,29.0,5.0,6.0,1.0,0.3,3.0\n"
)


@pytest.fixture
def app():
    flask_app.config["TESTING"] = True
    flask_app.config["SECRET_KEY"] = "test-secret"
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_yahoo_players():
    return [p.copy() for p in SAMPLE_YAHOO_PLAYERS]


@pytest.fixture
def sample_projections_csv():
    return SAMPLE_PROJECTIONS_CSV
