from unittest.mock import patch, Mock

import pytest

from optimizer.api.yahoo import get_contests, get_players


class TestGetContests:

    @patch("optimizer.api.yahoo.requests.get")
    def test_returns_parsed_json(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {"contests": [{"id": "123"}]}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = get_contests("nba")

        assert result == {"contests": [{"id": "123"}]}
        mock_get.assert_called_once_with(
            "https://dfyql-ro.sports.yahoo.com/v2/contestsFilteredWeb?sport=nba"
        )

    @patch("optimizer.api.yahoo.requests.get")
    def test_normalizes_sport_to_lowercase(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        get_contests("NBA")

        mock_get.assert_called_once_with(
            "https://dfyql-ro.sports.yahoo.com/v2/contestsFilteredWeb?sport=nba"
        )

    def test_raises_on_unsupported_sport(self):
        with pytest.raises(ValueError, match="Sport not available: mlb"):
            get_contests("mlb")

    @patch("optimizer.api.yahoo.requests.get")
    def test_raises_on_http_error(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("404")
        mock_get.return_value = mock_response

        with pytest.raises(Exception, match="404"):
            get_contests("nba")


class TestGetPlayers:

    @patch("optimizer.api.yahoo.requests.get")
    def test_returns_player_list(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "players": {"result": [{"firstName": "LeBron"}]}
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = get_players("12345")

        assert result == [{"firstName": "LeBron"}]
        mock_get.assert_called_once_with(
            "https://dfyql-ro.sports.yahoo.com/v2/contestPlayers?contestId=12345"
        )

    @patch("optimizer.api.yahoo.requests.get")
    def test_raises_on_http_error(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("500")
        mock_get.return_value = mock_response

        with pytest.raises(Exception, match="500"):
            get_players("12345")
