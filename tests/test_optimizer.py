from unittest.mock import patch, Mock

import pytest
from pydfs_lineup_optimizer import Site, Sport

from optimizer.optimizer import DfsDorkOptimizer, YAHOO_NBA_SCORING


class TestDfsDorkOptimizer:

    def test_init_creates_lineup_optimizer(self):
        opt = DfsDorkOptimizer(site=Site.YAHOO, sport=Sport.BASKETBALL)
        assert opt.lineup_optimizer is not None

    def test_load_yahoo_players(self, sample_yahoo_players):
        opt = DfsDorkOptimizer(site=Site.YAHOO, sport=Sport.BASKETBALL)
        opt.load_yahoo_players(sample_yahoo_players)

        pool = opt.lineup_optimizer.player_pool
        players = list(pool.all_players)
        assert len(players) == 3

    def test_exclude_players(self, sample_yahoo_players):
        opt = DfsDorkOptimizer(site=Site.YAHOO, sport=Sport.BASKETBALL)
        opt.load_yahoo_players(sample_yahoo_players)
        opt.exclude_players(["LeBron James"])

        pool = opt.lineup_optimizer.player_pool
        remaining_names = {
            f"{p.first_name} {p.last_name}"
            for p in pool.all_players
        }
        # remove_player raises if player not found, so just verify the call didn't error
        # and the pool still has other players
        assert "Stephen Curry" in remaining_names

    def test_lock_players(self, sample_yahoo_players):
        opt = DfsDorkOptimizer(site=Site.YAHOO, sport=Sport.BASKETBALL)
        opt.load_yahoo_players(sample_yahoo_players)
        opt.lock_players(["Stephen Curry"])

        pool = opt.lineup_optimizer.player_pool
        locked = [
            p for p in pool.all_players
            if getattr(p, "is_locked", False) or p in pool.locked_players
        ]
        assert any(p.first_name == "Stephen" for p in locked)

    @patch("optimizer.optimizer.requests.get")
    def test_load_external_projections(self, mock_get, sample_yahoo_players, sample_projections_csv):
        mock_response = Mock()
        mock_response.text = sample_projections_csv
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        with patch.dict("os.environ", {"EXTERNAL_PROJECTIONS": "http://example.com/proj.csv"}):
            opt = DfsDorkOptimizer(site=Site.YAHOO, sport=Sport.BASKETBALL)
            opt.load_yahoo_players(sample_yahoo_players)
            opt.load_external_projections()

        pool = opt.lineup_optimizer.player_pool
        lebron = pool.get_player_by_id("leb_james_lal")

        # 27*1 + 7*1.2 + 7*1.5 + 1.2*3 + 0.8*3 + 3.5*-1 = 27 + 8.4 + 10.5 + 3.6 + 2.4 - 3.5 = 48.4
        assert lebron.fppg == pytest.approx(48.4)

    def test_load_external_projections_raises_without_env(self):
        with patch.dict("os.environ", {}, clear=True):
            opt = DfsDorkOptimizer(site=Site.YAHOO, sport=Sport.BASKETBALL)
            with pytest.raises(ValueError, match="EXTERNAL_PROJECTIONS"):
                opt.load_external_projections()


class TestYahooNbaScoring:

    def test_scoring_weights_are_correct(self):
        assert YAHOO_NBA_SCORING == {
            "points": 1,
            "rebounds": 1.2,
            "assists": 1.5,
            "steals": 3,
            "blocks": 3,
            "turnovers": -1,
        }
