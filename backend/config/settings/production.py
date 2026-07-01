"""Production settings for Footprint Manager."""

from typing import Any, cast

from .base import *  # noqa: F403

DEBUG = False

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

from core.logging.setup import configure_structlog  # noqa: E402

configure_structlog(log_level=LOG_LEVEL, json_logs=True)  # noqa: F405

LOGGING_SETTINGS = cast(dict[str, Any], LOGGING)  # noqa: F405
LOGGING_SETTINGS["handlers"]["console"]["formatter"] = "json"
