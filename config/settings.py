"""Runtime settings for the pytest-python-test-automation suite.

Single source of truth for every environment-dependent value:
the API base URL and the request timeout. Values come from
environment variables, with an optional ``.env`` file in the
project root as a fallback (see ``.env.example``). No URL,
timeout, or credential is hard-coded anywhere else in the repo:
``conftest.py`` and the tests import from here.

Environment variables
---------------------
API_BASE_URL     Base URL of the API under test.
                 Default: https://jsonplaceholder.typicode.com
REQUEST_TIMEOUT  Per-request timeout in seconds.
                 Default: 10
"""

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_API_BASE_URL = "https://jsonplaceholder.typicode.com"
DEFAULT_REQUEST_TIMEOUT = 10.0


def _load_dotenv(path=None):
    """Load ``KEY=VALUE`` pairs from a ``.env`` file into the environment.

    Minimal loader (no third-party dependency). Only sets variables
    that are not already present in the real environment, so an
    exported variable or CI secret always wins over ``.env``.
    Lines starting with ``#`` and blank lines are ignored.
    """
    dotenv_path = Path(path) if path else Path(__file__).resolve().parent.parent / ".env"
    if not dotenv_path.is_file():
        return
    for line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


# Read .env (if present) before any setting is resolved.
_load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Resolved, immutable runtime settings."""

    api_base_url: str = DEFAULT_API_BASE_URL
    request_timeout: float = DEFAULT_REQUEST_TIMEOUT


def get_settings():
    """Build Settings from the environment (with safe defaults)."""
    timeout_raw = os.environ.get("REQUEST_TIMEOUT", "")
    try:
        timeout = float(timeout_raw) if timeout_raw else DEFAULT_REQUEST_TIMEOUT
    except ValueError:
        timeout = DEFAULT_REQUEST_TIMEOUT
    return Settings(
        api_base_url=os.environ.get("API_BASE_URL", DEFAULT_API_BASE_URL).rstrip("/"),
        request_timeout=timeout,
    )


# Convenience singleton; prefer ``get_settings()`` in new code so
# tests can override env vars and re-resolve settings cleanly.
settings = get_settings()
