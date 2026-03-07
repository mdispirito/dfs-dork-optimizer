import os

from dotenv import load_dotenv

load_dotenv()


def require_env(name: str) -> str:
    """Get a required environment variable or raise with a clear message."""
    value = os.getenv(name)
    if not value:
        raise ValueError(f"{name} environment variable not set")
    return value
