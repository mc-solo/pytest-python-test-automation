"""Unit tests for the local helpers in src/utils.py. No network.

Every input/expected pair comes from ``test-data/utils.json``,
loaded once at module level. This file holds test logic only:
no hard-coded email, name, payload, or expected value.
"""

import json
from pathlib import Path

import pytest

from src.utils import build_post_payload, format_user_name, is_valid_email

pytestmark = pytest.mark.unit

_DATA = json.loads((Path(__file__).resolve().parent.parent / "test-data" / "utils.json").read_text(encoding="utf-8"))


def _build_case(case):
    """build_post_payload case: (title, body, user_id, expected dict)."""
    return (case["title"], case["body"], case["user_id"], case["expected"])


class TestBuildPostPayload:
    @pytest.mark.parametrize(
        "title, body, user_id, expected",
        [_build_case(case) for case in _DATA["build_post_payload"]["cases"]],
        ids=["explicit-user-id", "default-user-id", "empty-title-kept"],
    )
    def test_builds_expected_dict(self, title, body, user_id, expected):
        if user_id is None:
            payload = build_post_payload(title, body)
        else:
            payload = build_post_payload(title, body, user_id=user_id)
        assert payload == expected


class TestIsValidEmail:
    @pytest.mark.parametrize("email", _DATA["is_valid_email"]["valid"])
    def test_valid_emails(self, email):
        assert is_valid_email(email) is True

    @pytest.mark.parametrize("email", _DATA["is_valid_email"]["invalid"])
    def test_invalid_emails(self, email):
        assert is_valid_email(email) is False


class TestFormatUserName:
    @pytest.mark.parametrize(
        "name, username, expected",
        [
            (case["name"], case["username"], case["expected"])
            for case in _DATA["format_user_name"]["cases"]
        ],
        ids=[
            "name-and-username",
            "blank-name-falls-back-to-username",
            "whitespace-name-falls-back-to-username",
            "blank-username-returns-name-only",
            "both-blank-returns-empty-string",
            "whitespace-is-stripped",
        ],
    )
    def test_format_user_name(self, name, username, expected):
        assert format_user_name(name, username) == expected
