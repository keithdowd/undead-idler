"""Shared application models."""

from datetime import datetime
from enum import Enum


LAST_KEYPRESS_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


class ActivityState(Enum):
    """High-level activity states exposed by the application."""

    STOPPED = "stopped"
    RUNNING = "running"
    ERROR = "error"


def format_timestamp(timestamp: datetime | None) -> str:
    """Format a local activity timestamp for user-facing display."""
    if timestamp is None:
        return "None"
    return timestamp.strftime(LAST_KEYPRESS_TIMESTAMP_FORMAT)
