import time
from unittest.mock import patch, Mock

import pytest

from optimizer.projections import fetch_projections, clear_cache


FAKE_CSV = (
    "first_name,last_name,team,points,rebounds,assists,steals,blocks,turnovers\n"
    "LeBron,James,LAL,27.0,7.0,7.0,1.2,0.8,3.5\n"
)


@pytest.fixture(autouse=True)
def reset_cache():
    clear_cache()
    yield
    clear_cache()


class TestFetchProjections:

    @patch("optimizer.projections.requests.get")
    def test_fetches_and_parses_csv(self, mock_get):
        mock_response = Mock()
        mock_response.text = FAKE_CSV
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        with patch.dict("os.environ", {"EXTERNAL_PROJECTIONS": "http://example.com/proj.csv"}):
            rows = fetch_projections()

        assert len(rows) == 1
        assert rows[0]["first_name"] == "LeBron"
        assert rows[0]["points"] == "27.0"

    @patch("optimizer.projections.requests.get")
    def test_returns_cached_data_on_second_call(self, mock_get):
        mock_response = Mock()
        mock_response.text = FAKE_CSV
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        with patch.dict("os.environ", {"EXTERNAL_PROJECTIONS": "http://example.com/proj.csv"}):
            first = fetch_projections()
            second = fetch_projections()

        assert first is second
        assert mock_get.call_count == 1

    @patch("optimizer.projections.requests.get")
    def test_force_refresh_bypasses_cache(self, mock_get):
        mock_response = Mock()
        mock_response.text = FAKE_CSV
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        with patch.dict("os.environ", {"EXTERNAL_PROJECTIONS": "http://example.com/proj.csv"}):
            fetch_projections()
            fetch_projections(force_refresh=True)

        assert mock_get.call_count == 2

    @patch("optimizer.projections.requests.get")
    @patch("optimizer.projections._ttl", 1)
    def test_refetches_after_ttl_expires(self, mock_get):
        mock_response = Mock()
        mock_response.text = FAKE_CSV
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        with patch.dict("os.environ", {"EXTERNAL_PROJECTIONS": "http://example.com/proj.csv"}):
            fetch_projections()
            time.sleep(1.1)
            fetch_projections()

        assert mock_get.call_count == 2

    def test_raises_without_env_var(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="EXTERNAL_PROJECTIONS"):
                fetch_projections()

    @patch("optimizer.projections.requests.get")
    def test_raises_on_http_error(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("503")
        mock_get.return_value = mock_response

        with patch.dict("os.environ", {"EXTERNAL_PROJECTIONS": "http://example.com/proj.csv"}):
            with pytest.raises(Exception, match="503"):
                fetch_projections()


class TestClearCache:

    @patch("optimizer.projections.requests.get")
    def test_clear_cache_forces_refetch(self, mock_get):
        mock_response = Mock()
        mock_response.text = FAKE_CSV
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        with patch.dict("os.environ", {"EXTERNAL_PROJECTIONS": "http://example.com/proj.csv"}):
            fetch_projections()
            clear_cache()
            fetch_projections()

        assert mock_get.call_count == 2
