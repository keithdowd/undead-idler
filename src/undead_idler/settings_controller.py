"""Runtime-only application settings."""

from __future__ import annotations

from .models import SimulatedKey


class InvalidInterval(ValueError):
    """Raised when an activity interval is outside the supported range."""


class InvalidKey(ValueError):
    """Raised when a simulated key is not supported."""


class RuntimeSettings:
    """Hold validated settings for one application session."""

    DEFAULT_INTERVAL_MINUTES = 5
    DEFAULT_KEY = SimulatedKey.F15
    MIN_INTERVAL_MINUTES = 1
    MAX_INTERVAL_MINUTES = 10

    def __init__(self) -> None:
        self._interval_minutes = self.DEFAULT_INTERVAL_MINUTES
        self._key = self.DEFAULT_KEY

    @property
    def interval_minutes(self) -> int:
        """Return the current in-memory interval."""
        return self._interval_minutes

    @property
    def key(self) -> SimulatedKey:
        """Return the selected key for this application session."""
        return self._key

    def set_interval(self, interval_minutes: int) -> None:
        """Validate and update the interval for the current session."""
        if isinstance(interval_minutes, bool) or not isinstance(interval_minutes, int):
            raise InvalidInterval("interval must be a whole number of minutes")

        if not self.MIN_INTERVAL_MINUTES <= interval_minutes <= self.MAX_INTERVAL_MINUTES:
            raise InvalidInterval("interval must be between 1 and 10 minutes")

        self._interval_minutes = interval_minutes

    def set_key(self, key: SimulatedKey) -> None:
        """Validate and update the selected key for this session."""
        if not isinstance(key, SimulatedKey):
            raise InvalidKey("key must be F15 or Scroll Lock")
        self._key = key

    def set_settings(self, interval_minutes: int, key: SimulatedKey) -> None:
        """Validate both settings before applying either one."""
        if isinstance(interval_minutes, bool) or not isinstance(interval_minutes, int):
            raise InvalidInterval("interval must be a whole number of minutes")
        if not self.MIN_INTERVAL_MINUTES <= interval_minutes <= self.MAX_INTERVAL_MINUTES:
            raise InvalidInterval("interval must be between 1 and 10 minutes")
        if not isinstance(key, SimulatedKey):
            raise InvalidKey("key must be F15 or Scroll Lock")
        self._interval_minutes = interval_minutes
        self._key = key
