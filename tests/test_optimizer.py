import csv
import io
from unittest.mock import patch, Mock

import pytest
from pydfs_lineup_optimizer import Site, Sport

from optimizer.optimizer import DfsDorkOptimizer, YAHOO_NBA_SCORING


def _csv_to_rows(csv_text: str) -> list[dict]:
    return list(csv.DictReader(io.StringIO(csv_text)))


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

    @patch("optimizer.optimizer.fetch_projections")
    def test_load_external_projections(self, mock_fetch, sample_yahoo_players, sample_projections_csv):
        mock_fetch.return_value = _csv_to_rows(sample_projections_csv)

        opt = DfsDorkOptimizer(site=Site.YAHOO, sport=Sport.BASKETBALL)
        opt.load_yahoo_players(sample_yahoo_players)
        opt.load_external_projections()

        pool = opt.lineup_optimizer.player_pool
        lebron = pool.get_player_by_id("leb_james_lal")

        # 27*1 + 7*1.2 + 7*1.5 + 1.2*3 + 0.8*3 + 3.5*-1 = 48.4
        assert lebron.fppg == pytest.approx(48.4)
        mock_fetch.assert_called_once_with(force_refresh=False)

    @patch("optimizer.optimizer.fetch_projections")
    def test_load_external_projections_force_refresh(self, mock_fetch, sample_yahoo_players, sample_projections_csv):
        mock_fetch.return_value = _csv_to_rows(sample_projections_csv)

        opt = DfsDorkOptimizer(site=Site.YAHOO, sport=Sport.BASKETBALL)
        opt.load_yahoo_players(sample_yahoo_players)
        opt.load_external_projections(force_refresh=True)

        mock_fetch.assert_called_once_with(force_refresh=True)

    @patch("optimizer.optimizer.fetch_projections")
    def test_load_external_projections_raises_on_error(self, mock_fetch):
        mock_fetch.side_effect = ValueError("EXTERNAL_PROJECTIONS environment variable not set")

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
