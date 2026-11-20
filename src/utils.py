"""Small local helpers, with no network calls.

These are the helpers under test in tests/test_utils.py.
"""

import re

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def build_post_payload(title, body, user_id=1):
    """Build a post payload dict for the JSONPlaceholder /posts endpoint."""
    return {
        "title": title,
        "body": body,
        "userId": user_id,
    }


def is_valid_email(email):
    """Return True for a basic well-formed email address, else False."""
    if not isinstance(email, str):
        return False
    return bool(_EMAIL_RE.match(email.strip()))


def format_user_name(name, username):
    """Format a display name as 'Name (@username)'.

    Falls back to just the username when the name is blank.
    """
    name = (name or "").strip()
    username = (username or "").strip()
    if not name:
        return f"@{username}" if username else ""
    if not username:
        return name
    return f"{name} (@{username})"
