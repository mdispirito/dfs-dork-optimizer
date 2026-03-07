import os

from flask import Flask, Response, jsonify, redirect, request, session
from flask_cors import CORS
from pydfs_lineup_optimizer import Site, Sport

from optimizer.api import yahoo as yahoo_api
from optimizer.auth import (
    exchange_code_for_token,
    get_authorization_url,
    get_user_info,
    is_token_expired,
    refresh_access_token,
)
from optimizer.config import require_env
from optimizer.optimizer import DfsDorkOptimizer

app = Flask(__name__)
app.secret_key = require_env("FLASK_SECRET_KEY")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
CORS(app, supports_credentials=True, origins=[FRONTEND_URL])


# --- Auth routes ---


@app.route("/auth/yahoo")
def auth_yahoo():
    try:
        url, state = get_authorization_url()
        session["oauth_state"] = state
        return redirect(url)
    except Exception as e:
        return Response(response=f"Unable to start auth flow: {e}", status=500)


@app.route("/auth/yahoo/callback")
def auth_yahoo_callback():
    try:
        code = request.args.get("code")
        state = session.pop("oauth_state", None)

        if not code or not state:
            return Response(response="Missing code or state", status=400)

        token = exchange_code_for_token(code, state)
        session["yahoo_token"] = token

        try:
            user_info = get_user_info(token["access_token"])
            session["yahoo_user"] = user_info
        except Exception:
            pass

        return redirect(FRONTEND_URL)
    except Exception as e:
        return Response(response=f"Auth callback failed: {e}", status=500)


@app.route("/auth/status")
def auth_status():
    token = session.get("yahoo_token")

    if not token:
        return jsonify({"authenticated": False})

    if is_token_expired(token):
        refresh = token.get("refresh_token")
        if not refresh:
            session.pop("yahoo_token", None)
            session.pop("yahoo_user", None)
            return jsonify({"authenticated": False})

        try:
            token = refresh_access_token(refresh)
            session["yahoo_token"] = token
        except Exception:
            session.pop("yahoo_token", None)
            session.pop("yahoo_user", None)
            return jsonify({"authenticated": False})

    user_info = session.get("yahoo_user")
    return jsonify({"authenticated": True, "user": user_info})


@app.route("/auth/logout", methods=["POST"])
def auth_logout():
    session.pop("yahoo_token", None)
    session.pop("yahoo_user", None)
    return jsonify({"logged_out": True})


# --- API routes ---


@app.route("/api/contests")
def get_contests():
    try:
        return yahoo_api.get_contests(sport="nba")
    except Exception as e:
        return Response(response=f"Unable to get contests: {e}", status=500)


@app.route("/api/<contest_id>/players")
def get_players(contest_id):
    try:
        return yahoo_api.get_players(contest_id=contest_id)
    except Exception as e:
        return Response(response=f"Unable to get players for contest {contest_id}: {e}", status=500)


@app.route("/api/optimized_lineup", methods=["POST"])
def optimize_lineups():
    try:
        body = request.get_json()

        optimizer = DfsDorkOptimizer(site=Site.YAHOO, sport=Sport.BASKETBALL)
        optimizer.load_yahoo_players(body["player_pool"])

        if body.get("load_external_projections"):
            force_refresh = body.get("force_refresh_projections", False)
            optimizer.load_external_projections(force_refresh=force_refresh)

        optimizer.exclude_players(body.get("excluded_players", []))
        optimizer.lock_players(body.get("locked_players", []))

        lineups = optimizer.optimize(body.get("lineups", 1))
        return jsonify([str(lineup) for lineup in lineups])
    except Exception as e:
        return Response(response=f"Unable to optimize lineups: {e}", status=500)


if __name__ == "__main__":
    app.run(debug=True, port=8080, ssl_context="adhoc")
