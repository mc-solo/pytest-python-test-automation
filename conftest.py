"""Shared fixtures for the pytest API + unit test suite.

The API tests run against the public JSONPlaceholder fake API
(https://jsonplaceholder.typicode.com). It does not persist writes,
so POST/PUT/PATCH/DELETE return simulated responses.
"""

import sys
from pathlib import Path

import pytest
import requests

# Make the project root importable so tests can do `from src.utils import ...`.
sys.path.insert(0, str(Path(__file__).resolve().parent))

BASE_URL = "https://jsonplaceholder.typicode.com"


@pytest.fixture(scope="session")
def base_url():
    """Base URL of the API under test."""
    return BASE_URL


@pytest.fixture(scope="session")
def api_session(base_url):
    """A shared requests Session with the base URL attached."""
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    session.base_url = base_url
    yield session
    session.close()


@pytest.fixture
def sample_post_payload():
    """A valid payload for creating a post."""
    return {
        "title": "pytest sample post",
        "body": "Created by the pytest-python-test-automation suite.",
        "userId": 1,
    }


@pytest.fixture
def sample_post_update():
    """A payload for updating an existing post."""
    return {
        "title": "updated title",
        "body": "Updated body.",
        "userId": 1,
    }
