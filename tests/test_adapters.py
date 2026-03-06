from optimizer.adapters.yahoo import convert_yahoo_players


class TestConvertYahooPlayers:

    def test_converts_single_player(self):
        players = convert_yahoo_players([{
            "firstName": "LeBron",
            "lastName": "James",
            "teamAbbr": "LAL",
            "eligiblePositions": ["SF", "PF"],
            "salary": 45,
            "fantasyPointsPerGame": 50.0,
        }])

        assert len(players) == 1
        p = players[0]
        assert p.first_name == "LeBron"
        assert p.last_name == "James"
        assert p.team == "LAL"
        assert set(p.positions) == {"SF", "PF"}
        assert p.salary == 45
        assert p.fppg == 50.0

    def test_converts_multiple_players(self, sample_yahoo_players):
        players = convert_yahoo_players(sample_yahoo_players)
        assert len(players) == 3

    def test_generates_correct_player_ids(self, sample_yahoo_players):
        players = convert_yahoo_players(sample_yahoo_players)
        ids = [p.id for p in players]
        assert "leb_james_lal" in ids
        assert "ste_curry_gsw" in ids

    def test_handles_jr_suffix_in_id(self, sample_yahoo_players):
        players = convert_yahoo_players(sample_yahoo_players)
        jr_player = [p for p in players if p.last_name == "Jackson Jr."][0]
        assert jr_player.id == "jar_jackson_mem"

    def test_empty_pool(self):
        assert convert_yahoo_players([]) == []

    def test_raises_on_missing_field(self):
        try:
            convert_yahoo_players([{"firstName": "LeBron"}])
            assert False, "Should have raised KeyError"
        except KeyError:
            pass
