import os
import time

import requests
from requests_oauthlib import OAuth2Session

from optimizer.config import require_env

YAHOO_AUTH_URL = "https://api.login.yahoo.com/oauth2/request_auth"
YAHOO_TOKEN_URL = "https://api.login.yahoo.com/oauth2/get_token"
YAHOO_USERINFO_URL = "https://api.login.yahoo.com/openid/v1/userinfo"

REDIRECT_URI = os.getenv("YAHOO_REDIRECT_URI", "https://localhost:8080/auth/yahoo/callback")

_client_id = require_env("YAHOO_CLIENT_ID")
_client_secret = require_env("YAHOO_CLIENT_SECRET")


def create_oauth_session(state: str | None = None) -> OAuth2Session:
    return OAuth2Session(_client_id, redirect_uri=REDIRECT_URI, state=state)


def get_authorization_url() -> tuple[str, str]:
    """Generate Yahoo authorization URL and state token."""
    oauth = create_oauth_session()
    url, state = oauth.authorization_url(YAHOO_AUTH_URL)
    return url, state


def exchange_code_for_token(code: str, state: str) -> dict:
    """Exchange authorization code for access/refresh tokens."""
    oauth = create_oauth_session(state=state)
    token = oauth.fetch_token(
        YAHOO_TOKEN_URL,
        code=code,
        client_secret=_client_secret,
    )
    return token


def refresh_access_token(refresh_token: str) -> dict:
    """Use a refresh token to get a new access token."""
    oauth = create_oauth_session()
    token = oauth.refresh_token(
        YAHOO_TOKEN_URL,
        refresh_token=refresh_token,
        client_id=_client_id,
        client_secret=_client_secret,
    )
    return token


def is_token_expired(token: dict) -> bool:
    """Check if the access token has expired."""
    expires_at = token.get("expires_at", 0)
    return time.time() >= expires_at


def get_user_info(access_token: str) -> dict:
    """Fetch the authenticated user's profile from Yahoo."""
    response = requests.get(
        YAHOO_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    response.raise_for_status()
    return response.json()
