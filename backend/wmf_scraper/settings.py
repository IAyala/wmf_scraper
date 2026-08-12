"""Single place where environment configuration is read."""

import os
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version
from pathlib import Path

DEVELOPMENT_ENVIRONMENTS = frozenset({"dev", "development", "local"})


def get_version() -> str:
    try:
        return package_version("wmf-scraper")
    except PackageNotFoundError:  # pragma: no cover - only when running from a raw checkout
        return "0.0.0"


def is_development_mode() -> bool:
    return os.getenv("ENVIRONMENT", "production").lower() in DEVELOPMENT_ENVIRONMENTS


def get_database_path() -> str:
    return os.getenv("DATABASE_PATH", "data/wmf_scraper.db")


def get_static_dir() -> Path | None:
    """Directory holding the built frontend, or None when it is not present."""
    static_dir = Path(os.getenv("STATIC_DIR", "static"))
    return static_dir if (static_dir / "index.html").is_file() else None


def get_api_key() -> str | None:
    """Machine-to-machine API key. Optional: only enables bearer-token access."""
    return os.getenv("API_KEY") or None


def get_session_secret() -> str | None:
    return os.getenv("SESSION_SECRET") or None


def get_credentials() -> dict:
    """Map of username -> role, built from the configured admin credentials.

    Returned as {username: (password, role)}. Roles missing from the environment
    are simply absent, so a deployment can configure only one of them.
    """
    result = {}
    for role in ("admin", "superadmin"):
        username = os.getenv(f"{role.upper()}_USERNAME")
        password = os.getenv(f"{role.upper()}_PASSWORD")
        if username and password:
            result[username] = (password, role)
    return result
