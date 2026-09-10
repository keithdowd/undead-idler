"""Shared application models."""

from enum import Enum


class ActivityState(Enum):
    """High-level activity states exposed by the application."""

    STOPPED = "stopped"
    RUNNING = "running"
    ERROR = "error"

