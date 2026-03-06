# DFS Dork Optimizer

## Overview
Python/Flask backend API for optimizing Yahoo NBA daily fantasy lineups.
Uses `pydfs-lineup-optimizer` as the core optimization engine.

## Setup
- Package manager: **uv** (not Poetry)
- Python: 3.13+
- Install deps: `uv sync`
- Run dev server: `uv run python -m optimizer.app` (starts on port 8080)

## Project Structure
```
optimizer/
  app.py              # Flask app with API routes
  optimizer.py         # DfsDorkOptimizer - wraps pydfs-lineup-optimizer
  api/yahoo.py         # Yahoo DFS API client (public endpoints, no auth needed)
  adapters/yahoo.py    # Converts Yahoo player data -> pydfs Player objects
  util/player.py       # Player ID generation
```

## API Routes
- `GET /api/contests` — list available Yahoo DFS contests
- `GET /api/<contest_id>/players` — get player pool for a contest
- `POST /api/optimized_lineup` — optimize lineups (JSON body with `player_pool`, optional `lineups`, `load_external_projections`, `excluded_players`, `locked_players`)

## Key Notes
- Yahoo contest/player endpoints are public (no auth required)
- Yahoo OAuth2 is NOT implemented — needed for future features like auto-entering lineups
- External projections loaded via CSV URL in `EXTERNAL_PROJECTIONS` env var
- Player IDs are generated from name + team (format: `first3_lastname_team`)
