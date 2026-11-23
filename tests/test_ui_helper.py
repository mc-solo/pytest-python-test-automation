"""Unit tests for the UI helpers in src/ui_helper.py. No network.

Every input/expected pair comes from ``test-data/ui.json``,
loaded once at module level. This file holds test logic only:
no hard-coded title, text, name, or expected value.
"""

import json
from pathlib import Path

import pytest

from src.ui_helper import (
    build_user_badge,
    format_post_title,
    render_post_summary,
    truncate_text,
)

pytestmark = pytest.mark.utils

_DATA = json.loads((Path(__file__).resolve().parent.parent / "test-data" / "ui.json").read_text(encoding="utf-8"))


class TestFormatPostTitle:
    @pytest.mark.parametrize(
        "input, max_length, expected",
        [
            (case["input"], case["max_length"], case["expected"])
            for case in _DATA["format_post_title"]["cases"]
        ],
        ids=["fits", "long-title-shortened", "padding-stripped"],
    )
    def test_format_post_title(self, input, max_length, expected):
        assert format_post_title(input, max_length) == expected


class TestTruncateText:
    @pytest.mark.parametrize(
        "input, max_length, expected",
        [
            (case["input"], case["max_length"], case["expected"])
            for case in _DATA["truncate_text"]["cases"]
        ],
        ids=["fits", "cut-with-ellipsis", "tiny-limit", "empty-input"],
    )
    def test_truncate_text(self, input, max_length, expected):
        assert truncate_text(input, max_length) == expected


class TestRenderPostSummary:
    @pytest.mark.parametrize(
        "post, max_length, expected",
        [
            (case["post"], case["max_length"], case["expected"])
            for case in _DATA["render_post_summary"]["cases"]
        ],
        ids=["short-title", "long-title-shortened", "missing-title"],
    )
    def test_render_post_summary(self, post, max_length, expected):
        assert render_post_summary(post, max_length) == expected


class TestBuildUserBadge:
    @pytest.mark.parametrize(
        "name, username, expected",
        [
            (case["name"], case["username"], case["expected"])
            for case in _DATA["build_user_badge"]["cases"]
        ],
        ids=["name-and-username", "blank-name", "blank-username"],
    )
    def test_build_user_badge(self, name, username, expected):
        assert build_user_badge(name, username) == expected
