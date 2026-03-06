import csv
import io
import logging
import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

DEFAULT_TTL_SECONDS = 600  # 10 minutes

_cache: list[dict] | None = None
_cache_timestamp: float = 0


def fetch_projections(force_refresh: bool = False) -> list[dict]:
    """Fetch external projections, returning cached data if still fresh.

    Args:
        force_refresh: Bypass the cache and re-fetch from source.

    Returns:
        List of projection dicts with keys like first_name, last_name, team,
        points, rebounds, assists, steals, blocks, turnovers.
    """
    global _cache, _cache_timestamp

    ttl = int(os.getenv("PROJECTIONS_TTL_SECONDS", DEFAULT_TTL_SECONDS))
    age = time.time() - _cache_timestamp

    if not force_refresh and _cache is not None and age < ttl:
        logger.info("Serving projections from cache (age: %ds, ttl: %ds)", int(age), ttl)
        return _cache

    url = os.getenv("EXTERNAL_PROJECTIONS")
    if not url:
        raise ValueError("EXTERNAL_PROJECTIONS environment variable not set")

    logger.info("Fetching projections from %s", url)
    response = requests.get(url)
    response.raise_for_status()

    rows = list(csv.DictReader(io.StringIO(response.text)))
    _cache = rows
    _cache_timestamp = time.time()

    logger.info("Cached %d projection rows", len(rows))
    return rows


def clear_cache():
    """Clear the projection cache. Useful for testing."""
    global _cache, _cache_timestamp
    _cache = None
    _cache_timestamp = 0
