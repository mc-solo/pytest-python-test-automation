"""Shared fixtures for the pytest API + unit test suite.

The API tests run against the public JSONPlaceholder fake API
(see ``config/settings.py`` for the base URL). It does not persist
writes, so POST/PUT/PATCH/DELETE return simulated responses.

Config (``config/``) holds the base URL and timeout; test data
(``test-data/*.json``) holds payloads and expected values. This
file only wires the two together into fixtures. It contains no
hard-coded URL, timeout, payload, or expected value of its own.
"""

import json
import sys
from pathlib import Path

import pytest
import requests

# Make the project root importable so tests can do `from src.utils import ...`
# and `from config import ...`.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import get_settings  # noqa: E402

ROOT = Path(__file__).resolve().parent
TEST_DATA_DIR = ROOT / "test-data"


def load_test_data(name):
    """Load a JSON file from ``test-data/`` (``name`` without extension)."""
    path = TEST_DATA_DIR / f"{name}.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


class _TimeoutSession(requests.Session):
    """A requests Session that applies the configured timeout by default.

    ``requests`` has no session-level timeout, so every call made
    through this session uses ``settings.request_timeout`` unless
    the caller passes an explicit ``timeout=``.
    """

    def __init__(self, timeout):
        super().__init__()
        self._default_timeout = timeout

    def request(self, *args, **kwargs):
        kwargs.setdefault("timeout", self._default_timeout)
        return super().request(*args, **kwargs)


@pytest.fixture(scope="session")
def settings():
    """Resolved runtime settings from ``config/settings.py``."""
    return get_settings()


@pytest.fixture(scope="session")
def base_url(settings):
    """Base URL of the API under test (from config, not hard-coded)."""
    return settings.api_base_url


@pytest.fixture(scope="session")
def api_session(base_url, settings):
    """A shared requests Session with the base URL attached.

    Every request through this session uses the configured timeout.
    """
    session = _TimeoutSession(settings.request_timeout)
    session.headers.update({"Accept": "application/json"})
    session.base_url = base_url
    yield session
    session.close()


@pytest.fixture(scope="session")
def posts_data():
    """Expected posts data from ``test-data/posts.json``."""
    return load_test_data("posts")


@pytest.fixture(scope="session")
def users_data():
    """Expected users data from ``test-data/users.json``."""
    return load_test_data("users")


@pytest.fixture
def sample_post_payload(posts_data):
    """A valid payload for creating a post (from test-data/posts.json)."""
    return dict(posts_data["sample_post_payload"])


@pytest.fixture
def sample_post_update(posts_data):
    """A payload for updating an existing post (from test-data/posts.json)."""
    return dict(posts_data["sample_post_update"])
