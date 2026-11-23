"""Small UI helpers for rendering API data, with no network calls.

These are the helpers under test in tests/test_ui_helper.py.
They only format data that the API tests already fetch (posts and
users); they never call the API themselves. Limits (max title and
summary length) come from test-data/ui.json via the tests, not
from hard-coded values here — the defaults below are fallbacks
only, used when a caller passes no limit.
"""

from src.utils import format_user_name

DEFAULT_MAX_TITLE_LENGTH = 30
DEFAULT_MAX_SUMMARY_LENGTH = 80


def format_post_title(title, max_length=DEFAULT_MAX_TITLE_LENGTH):
    """Clean up a post title for display: strip it, and shorten it
    with an ellipsis when it is longer than max_length."""
    title = (title or "").strip()
    if len(title) <= max_length:
        return title
    return title[: max_length - 3].rstrip() + "..."


def truncate_text(text, max_length):
    """Shorten text to max_length characters, adding '...' when cut.
    Text that already fits is returned unchanged."""
    text = "" if text is None else str(text)
    if len(text) <= max_length:
        return text
    if max_length <= 3:
        return "." * max_length
    return text[: max_length - 3].rstrip() + "..."


def render_post_summary(post, max_length=DEFAULT_MAX_SUMMARY_LENGTH):
    """One-line summary for a post dict: 'title (user N)'.

    The title is shortened with truncate_text; a missing title
    becomes the placeholder from the caller, never a crash.
    """
    title = format_post_title(post.get("title") or "", max_length)
    return f"{title} (user {post.get('userId')})"


def build_user_badge(name, username):
    """A display badge for a user, reusing format_user_name."""
    return format_user_name(name, username)
