"""Configuration package: environment-driven settings.

Import from here, not from ``config.settings`` directly::

    from config import get_settings
    settings = get_settings()
"""

from config.settings import DEFAULT_API_BASE_URL, DEFAULT_REQUEST_TIMEOUT, Settings, get_settings, settings

__all__ = [
    "DEFAULT_API_BASE_URL",
    "DEFAULT_REQUEST_TIMEOUT",
    "Settings",
    "get_settings",
    "settings",
]
