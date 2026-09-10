"""Runtime-only application settings."""

from __future__ import annotations


class InvalidInterval(ValueError):
    """Raised when an activity interval is outside the supported range."""


class RuntimeSettings:
    """Hold validated settings for one application session."""

    DEFAULT_INTERVAL_MINUTES = 5
    MIN_INTERVAL_MINUTES = 1
    MAX_INTERVAL_MINUTES = 10

    def __init__(self) -> None:
        self._interval_minutes = self.DEFAULT_INTERVAL_MINUTES

    @property
    def interval_minutes(self) -> int:
        """Return the current in-memory interval."""
        return self._interval_minutes

    def set_interval(self, interval_minutes: int) -> None:
        """Validate and update the interval for the current session."""
        if isinstance(interval_minutes, bool) or not isinstance(interval_minutes, int):
            raise InvalidInterval("interval must be a whole number of minutes")

        if not self.MIN_INTERVAL_MINUTES <= interval_minutes <= self.MAX_INTERVAL_MINUTES:
            raise InvalidInterval("interval must be between 1 and 10 minutes")

        self._interval_minutes = interval_minutes

