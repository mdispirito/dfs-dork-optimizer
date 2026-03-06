import time
from unittest.mock import patch, Mock

import pytest

from optimizer.auth import (
    get_authorization_url,
    exchange_code_for_token,
    refresh_access_token,
    is_token_expired,
    get_user_info,
)


class TestGetAuthorizationUrl:

    @patch("optimizer.auth.create_oauth_session")
    def test_returns_url_and_state(self, mock_create):
        mock_session = Mock()
        mock_session.authorization_url.return_value = ("https://yahoo.com/auth", "state123")
        mock_create.return_value = mock_session

        with patch.dict("os.environ", {"YAHOO_CLIENT_ID": "test_id"}):
            url, state = get_authorization_url()

        assert url == "https://yahoo.com/auth"
        assert state == "state123"

    def test_raises_without_client_id(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="YAHOO_CLIENT_ID"):
                get_authorization_url()


class TestExchangeCodeForToken:

    @patch("optimizer.auth.create_oauth_session")
    def test_exchanges_code(self, mock_create):
        mock_session = Mock()
        mock_session.fetch_token.return_value = {"access_token": "abc", "refresh_token": "def"}
        mock_create.return_value = mock_session

        with patch.dict("os.environ", {"YAHOO_CLIENT_ID": "test_id", "YAHOO_CLIENT_SECRET": "test_secret"}):
            token = exchange_code_for_token("code123", "state123")

        assert token["access_token"] == "abc"
        mock_session.fetch_token.assert_called_once()

    def test_raises_without_client_secret(self):
        with patch.dict("os.environ", {"YAHOO_CLIENT_ID": "test_id"}, clear=True):
            with patch("optimizer.auth.create_oauth_session"):
                with pytest.raises(ValueError, match="YAHOO_CLIENT_SECRET"):
                    exchange_code_for_token("code", "state")


class TestRefreshAccessToken:

    @patch("optimizer.auth.create_oauth_session")
    def test_refreshes_token(self, mock_create):
        mock_session = Mock()
        mock_session.refresh_token.return_value = {"access_token": "new_abc"}
        mock_create.return_value = mock_session

        with patch.dict("os.environ", {"YAHOO_CLIENT_ID": "test_id", "YAHOO_CLIENT_SECRET": "test_secret"}):
            token = refresh_access_token("old_refresh")

        assert token["access_token"] == "new_abc"


class TestIsTokenExpired:

    def test_expired_token(self):
        token = {"expires_at": time.time() - 100}
        assert is_token_expired(token) is True

    def test_valid_token(self):
        token = {"expires_at": time.time() + 3600}
        assert is_token_expired(token) is False

    def test_missing_expires_at(self):
        assert is_token_expired({}) is True


class TestGetUserInfo:

    @patch("optimizer.auth.requests.get")
    def test_returns_user_info(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {"sub": "user123", "name": "Test User"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = get_user_info("access_token_abc")

        assert result["name"] == "Test User"
        mock_get.assert_called_once_with(
            "https://api.login.yahoo.com/openid/v1/userinfo",
            headers={"Authorization": "Bearer access_token_abc"},
        )

    @patch("optimizer.auth.requests.get")
    def test_raises_on_http_error(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("401")
        mock_get.return_value = mock_response

        with pytest.raises(Exception, match="401"):
            get_user_info("bad_token")
