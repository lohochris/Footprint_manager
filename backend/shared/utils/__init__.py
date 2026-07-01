"""
Shared utility functions for Footprint Manager.

General-purpose helpers used across multiple apps.  Each function is
intentionally small, pure, and independently testable.  Framework-specific
utilities (Django ORM, DRF, Celery) belong in their respective app packages.

Usage::

    from shared.utils import slugify_safe, truncate_str, deep_merge
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

# ---------------------------------------------------------------------------
# String utilities
# ---------------------------------------------------------------------------


def slugify_safe(value: str, *, separator: str = "-", max_length: int = 255) -> str:
    """
    Convert *value* to a URL-safe lowercase slug.

    Steps:
    1. Normalise unicode to ASCII transliteration.
    2. Lowercase.
    3. Replace non-alphanumeric characters with *separator*.
    4. Collapse consecutive separators.
    5. Strip leading/trailing separators.
    6. Truncate to *max_length*.

    Args:
        value: Input string to slugify.
        separator: Character used between words (default ``"-"``).
        max_length: Maximum returned length (default 255).

    Returns:
        A URL-safe slug string, never empty (falls back to ``"item"``).
    """
    normalised = unicodedata.normalize("NFKD", value)
    ascii_str = normalised.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_str.lower()
    cleaned = re.sub(r"[^a-z0-9]+", separator, lowered)
    slug = cleaned.strip(separator)
    slug = re.sub(rf"{re.escape(separator)}+", separator, slug)
    slug = slug[:max_length].rstrip(separator)
    return slug or "item"


def truncate_str(value: str, max_length: int, *, suffix: str = "…") -> str:
    """
    Truncate *value* to *max_length* characters, appending *suffix* if cut.

    Args:
        value: The string to truncate.
        max_length: Maximum total length including the suffix.
        suffix: String appended when truncation occurs (default ``"…"``).

    Returns:
        The (possibly truncated) string.
    """
    if len(value) <= max_length:
        return value
    cut = max_length - len(suffix)
    if cut <= 0:
        return suffix[:max_length]
    return value[:cut] + suffix


def mask_sensitive(value: str, *, visible: int = 4, mask_char: str = "*") -> str:
    """
    Mask a sensitive string, keeping the first *visible* characters.

    Args:
        value: The sensitive value to mask.
        visible: Number of leading characters to expose.
        mask_char: Character used for masking (default ``"*"``).

    Returns:
        Masked string, e.g. ``"sk-a****"``.
    """
    if not value:
        return ""
    exposed = value[:visible]
    return exposed + mask_char * max(0, len(value) - visible)


def camel_to_snake(name: str) -> str:
    """
    Convert a ``CamelCase`` or ``mixedCase`` string to ``snake_case``.

    Args:
        name: CamelCase identifier.

    Returns:
        snake_case equivalent.
    """
    step1 = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    step2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", step1)
    return step2.lower()


def snake_to_camel(name: str) -> str:
    """
    Convert a ``snake_case`` string to ``camelCase``.

    Args:
        name: snake_case identifier.

    Returns:
        camelCase equivalent.
    """
    parts = name.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


# ---------------------------------------------------------------------------
# Dictionary utilities
# ---------------------------------------------------------------------------


def deep_merge(base: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    """
    Recursively merge *overrides* into *base*, returning a new dict.

    Nested dictionaries are merged recursively.  Non-dict values in
    *overrides* replace those in *base*.  Neither input dict is mutated.

    Args:
        base: The starting dictionary.
        overrides: Values to merge on top of *base*.

    Returns:
        Merged dictionary.
    """
    result: dict[str, Any] = dict(base)
    for key, value in overrides.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def omit(data: dict[str, Any], keys: set[str]) -> dict[str, Any]:
    """
    Return a copy of *data* with the specified *keys* removed.

    Args:
        data: Source dictionary.
        keys: Set of keys to exclude.

    Returns:
        New dictionary without the excluded keys.
    """
    return {k: v for k, v in data.items() if k not in keys}


def pick(data: dict[str, Any], keys: set[str]) -> dict[str, Any]:
    """
    Return a copy of *data* containing only the specified *keys*.

    Args:
        data: Source dictionary.
        keys: Set of keys to include.

    Returns:
        New dictionary with only the selected keys.
    """
    return {k: v for k, v in data.items() if k in keys}


# ---------------------------------------------------------------------------
# Numeric utilities
# ---------------------------------------------------------------------------


def clamp(value: int | float, minimum: int | float, maximum: int | float) -> int | float:
    """
    Clamp *value* between *minimum* and *maximum* (inclusive).

    Args:
        value: The number to clamp.
        minimum: Lower bound.
        maximum: Upper bound.

    Returns:
        Clamped value.
    """
    return max(minimum, min(value, maximum))


__all__ = [
    "slugify_safe",
    "truncate_str",
    "mask_sensitive",
    "camel_to_snake",
    "snake_to_camel",
    "deep_merge",
    "omit",
    "pick",
    "clamp",
]
