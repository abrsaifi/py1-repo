"""Shared datetime helpers for UTC-safe application code."""
from datetime import datetime, timezone


def utc_now():
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


def utc_now_naive():
    """Return a naive UTC timestamp for legacy DateTime columns stored as UTC."""
    return utc_now().replace(tzinfo=None)