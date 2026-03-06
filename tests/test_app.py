import time
from unittest.mock import patch, Mock


class TestAuthYahooRoute:

    @patch("optimizer.app.get_authorization_url")
    def test_redirects_to_yahoo(self, mock_auth_url, client):
        mock_auth_url.return_value = ("https://yahoo.com/auth?client_id=x", "state123")

        resp = client.get("/auth/yahoo")

        assert resp.status_code == 302
        assert "yahoo.com/auth" in resp.headers["Location"]

    @patch("optimizer.app.get_authorization_url")
    def test_returns_500_on_error(self, mock_auth_url, client):
        mock_auth_url.side_effect = ValueError("YAHOO_CLIENT_ID not set")

        resp = client.get("/auth/yahoo")

        assert resp.status_code == 500


class TestAuthCallbackRoute:

    @patch("optimizer.app.exchange_code_for_token")
    def test_exchanges_code_and_redirects(self, mock_exchange, client):
        mock_exchange.return_value = {"access_token": "abc", "refresh_token": "def"}

        with client.session_transaction() as sess:
            sess["oauth_state"] = "state123"

        resp = client.get("/auth/yahoo/callback?code=code123&state=state123")

        assert resp.status_code == 302
        assert "localhost:5173" in resp.headers["Location"]

    def test_returns_400_without_code(self, client):
        resp = client.get("/auth/yahoo/callback")
        assert resp.status_code == 400


class TestAuthStatusRoute:

    def test_returns_unauthenticated_without_token(self, client):
        resp = client.get("/auth/status")
        data = resp.get_json()

        assert data["authenticated"] is False

    def test_returns_authenticated_with_valid_token(self, client):
        with client.session_transaction() as sess:
            sess["yahoo_token"] = {
                "access_token": "abc",
                "expires_at": time.time() + 3600,
            }

        with patch("optimizer.app.get_user_info") as mock_user:
            mock_user.return_value = {"name": "Test User"}
            resp = client.get("/auth/status")

        data = resp.get_json()
        assert data["authenticated"] is True
        assert data["user"]["name"] == "Test User"

    @patch("optimizer.app.refresh_access_token")
    def test_refreshes_expired_token(self, mock_refresh, client):
        mock_refresh.return_value = {
            "access_token": "new_abc",
            "expires_at": time.time() + 3600,
        }

        with client.session_transaction() as sess:
            sess["yahoo_token"] = {
                "access_token": "old",
                "refresh_token": "refresh_abc",
                "expires_at": time.time() - 100,
            }

        with patch("optimizer.app.get_user_info") as mock_user:
            mock_user.return_value = {"name": "Test User"}
            resp = client.get("/auth/status")

        data = resp.get_json()
        assert data["authenticated"] is True
        mock_refresh.assert_called_once_with("refresh_abc")

    def test_returns_unauthenticated_when_expired_no_refresh(self, client):
        with client.session_transaction() as sess:
            sess["yahoo_token"] = {
                "access_token": "old",
                "expires_at": time.time() - 100,
            }

        resp = client.get("/auth/status")
        data = resp.get_json()
        assert data["authenticated"] is False


class TestAuthLogoutRoute:

    def test_clears_session(self, client):
        with client.session_transaction() as sess:
            sess["yahoo_token"] = {"access_token": "abc"}

        resp = client.post("/auth/logout")

        assert resp.get_json() == {"logged_out": True}

        with client.session_transaction() as sess:
            assert "yahoo_token" not in sess


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

        mock_instance.load_external_projections.assert_called_once_with(force_refresh=False)

    @patch("optimizer.app.DfsDorkOptimizer")
    def test_passes_force_refresh_to_projections(self, MockOptimizer, client):
        mock_instance = Mock()
        mock_instance.optimize.return_value = []
        MockOptimizer.return_value = mock_instance

        client.post("/api/optimized_lineup", json={
            "player_pool": [],
            "load_external_projections": True,
            "force_refresh_projections": True,
        })

        mock_instance.load_external_projections.assert_called_once_with(force_refresh=True)

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
