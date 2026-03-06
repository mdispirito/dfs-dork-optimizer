from unittest.mock import patch, Mock


class TestContestsRoute:

    @patch("optimizer.app.yahoo_api.get_contests")
    def test_returns_contests(self, mock_get_contests, client):
        mock_get_contests.return_value = {"contests": [{"id": "123"}]}

        resp = client.get("/api/contests")

        assert resp.status_code == 200
        assert resp.get_json() == {"contests": [{"id": "123"}]}

    @patch("optimizer.app.yahoo_api.get_contests")
    def test_returns_500_on_error(self, mock_get_contests, client):
        mock_get_contests.side_effect = Exception("network error")

        resp = client.get("/api/contests")

        assert resp.status_code == 500
        assert "Unable to get contests" in resp.get_data(as_text=True)


class TestPlayersRoute:

    @patch("optimizer.app.yahoo_api.get_players")
    def test_returns_players(self, mock_get_players, client):
        mock_get_players.return_value = [{"firstName": "LeBron"}]

        resp = client.get("/api/12345/players")

        assert resp.status_code == 200
        assert resp.get_json() == [{"firstName": "LeBron"}]

    @patch("optimizer.app.yahoo_api.get_players")
    def test_returns_500_on_error(self, mock_get_players, client):
        mock_get_players.side_effect = Exception("network error")

        resp = client.get("/api/12345/players")

        assert resp.status_code == 500
        assert "12345" in resp.get_data(as_text=True)


class TestOptimizeLineupsRoute:

    def test_returns_400_without_json_body(self, client):
        resp = client.post("/api/optimized_lineup")
        assert resp.status_code == 500

    @patch("optimizer.app.DfsDorkOptimizer")
    def test_returns_optimized_lineups(self, MockOptimizer, client):
        mock_instance = Mock()
        mock_instance.optimize.return_value = ["lineup1", "lineup2"]
        MockOptimizer.return_value = mock_instance

        resp = client.post("/api/optimized_lineup", json={
            "player_pool": [{"firstName": "Test"}],
            "lineups": 2,
        })

        assert resp.status_code == 200
        assert resp.get_json() == ["lineup1", "lineup2"]
        mock_instance.load_yahoo_players.assert_called_once()
        mock_instance.optimize.assert_called_once_with(2)

    @patch("optimizer.app.DfsDorkOptimizer")
    def test_calls_external_projections_when_requested(self, MockOptimizer, client):
        mock_instance = Mock()
        mock_instance.optimize.return_value = []
        MockOptimizer.return_value = mock_instance

        client.post("/api/optimized_lineup", json={
            "player_pool": [],
            "load_external_projections": True,
        })

        mock_instance.load_external_projections.assert_called_once()

    @patch("optimizer.app.DfsDorkOptimizer")
    def test_does_not_call_external_projections_by_default(self, MockOptimizer, client):
        mock_instance = Mock()
        mock_instance.optimize.return_value = []
        MockOptimizer.return_value = mock_instance

        client.post("/api/optimized_lineup", json={"player_pool": []})

        mock_instance.load_external_projections.assert_not_called()

    @patch("optimizer.app.DfsDorkOptimizer")
    def test_excludes_and_locks_players(self, MockOptimizer, client):
        mock_instance = Mock()
        mock_instance.optimize.return_value = []
        MockOptimizer.return_value = mock_instance

        client.post("/api/optimized_lineup", json={
            "player_pool": [],
            "excluded_players": ["Player A"],
            "locked_players": ["Player B"],
        })

        mock_instance.exclude_players.assert_called_once_with(["Player A"])
        mock_instance.lock_players.assert_called_once_with(["Player B"])

    @patch("optimizer.app.DfsDorkOptimizer")
    def test_defaults_to_one_lineup(self, MockOptimizer, client):
        mock_instance = Mock()
        mock_instance.optimize.return_value = []
        MockOptimizer.return_value = mock_instance

        client.post("/api/optimized_lineup", json={"player_pool": []})

        mock_instance.optimize.assert_called_once_with(1)
