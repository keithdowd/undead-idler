"""UI-independent activity state management."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from PySide6.QtCore import QObject, QTimer, Signal

from .models import ActivityState, SimulatedKey, format_timestamp
from .settings_controller import RuntimeSettings
from .win_input import InputResult, cleanup_partial_input, send_keypress_with_result


class InvalidActivityTransition(ValueError):
    """Raised when an activity state transition is not permitted."""


InputSender = Callable[[], InputResult]
CleanupSender = Callable[[SimulatedKey, int], InputResult]


class ActivityController(QObject):
    """Own the activity state and notify observers when it changes."""

    state_changed = Signal(object)
    last_successful_keypress_changed = Signal(object)
    interval_changed = Signal(int)
    key_changed = Signal(object)
    error_changed = Signal(object)

    _allowed_transitions = {
        ActivityState.STOPPED: {ActivityState.RUNNING, ActivityState.ERROR},
        ActivityState.RUNNING: {ActivityState.STOPPED, ActivityState.ERROR},
        ActivityState.ERROR: {ActivityState.STOPPED, ActivityState.RUNNING},
    }

    def __init__(
        self,
        input_sender: InputSender | None = None,
        cleanup_sender: CleanupSender = cleanup_partial_input,
        settings: RuntimeSettings | None = None,
        timer: QTimer | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._state = ActivityState.STOPPED
        self._settings = settings or RuntimeSettings()
        self._input_sender = input_sender if input_sender is not None else (
            lambda: send_keypress_with_result(self._settings.key)
        )
        self._cleanup_sender = cleanup_sender
        self._timer = timer if timer is not None else QTimer(self)
        self._timer.timeout.connect(self._on_timer_timeout)
        self._consecutive_failures = 0
        self._error_message: str | None = None
        self._last_input_result: InputResult | None = None
        self._last_successful_keypress: datetime | None = None

    @property
    def state(self) -> ActivityState:
        """Return the current activity state."""
        return self._state

    @property
    def last_input_result(self) -> InputResult | None:
        """Return the most recent input submission result."""
        return self._last_input_result

    @property
    def consecutive_failures(self) -> int:
        """Return the number of consecutive failed submissions."""
        return self._consecutive_failures

    @property
    def error_message(self) -> str | None:
        """Return the latest local input failure description."""
        return self._error_message

    @property
    def last_successful_keypress(self) -> datetime | None:
        """Return the timestamp of the most recent successful keypress."""
        return self._last_successful_keypress

    @property
    def last_successful_keypress_text(self) -> str:
        """Return the last successful keypress in display format."""
        return format_timestamp(self._last_successful_keypress)

    @property
    def interval_minutes(self) -> int:
        """Return the current runtime interval in minutes."""
        return self._settings.interval_minutes

    @property
    def key(self) -> SimulatedKey:
        """Return the selected simulated key."""
        return self._settings.key

    def transition_to(self, state: ActivityState) -> bool:
        """Change state and notify observers; return whether it changed."""
        if state is self._state:
            return False

        if state not in self._allowed_transitions[self._state]:
            raise InvalidActivityTransition(
                f"cannot transition from {self._state.value} to {state.value}"
            )

        self._state = state
        if state is not ActivityState.RUNNING:
            self._timer.stop()
        self.state_changed.emit(state)
        return True

    def start(self) -> bool:
        """Send the initial keypress and transition to the running state."""
        if self._state is ActivityState.RUNNING:
            return False

        self._consecutive_failures = 0
        if self._error_message is not None:
            self._error_message = None
            self.error_changed.emit(None)
        result = self._input_sender()
        self._last_input_result = result
        if not result.success:
            if self._is_partial_result(result):
                self._record_partial_failure(result)
                return False
            self._record_failure(result)
            if self._state is ActivityState.STOPPED:
                self.transition_to(ActivityState.ERROR)
            return False

        self._record_successful_keypress()
        changed = self.transition_to(ActivityState.RUNNING)
        self._timer.setInterval(self._settings.interval_minutes * 60 * 1000)
        self._timer.start()
        return changed

    def stop(self) -> bool:
        """Stop activity and reset transient failure state."""
        self._timer.stop()
        self._consecutive_failures = 0
        if self._error_message is not None:
            self._error_message = None
            self.error_changed.emit(None)
        return self.transition_to(ActivityState.STOPPED)

    def set_interval(self, interval_minutes: int) -> None:
        """Validate and apply an interval change for the current session."""
        previous_interval = self._settings.interval_minutes
        self._settings.set_interval(interval_minutes)
        if (
            self._state is ActivityState.RUNNING
            and interval_minutes != previous_interval
        ):
            self._timer.stop()
            self._timer.setInterval(interval_minutes * 60 * 1000)
            self._timer.start()
        if interval_minutes != previous_interval:
            self.interval_changed.emit(interval_minutes)

    def set_key(self, key: SimulatedKey) -> None:
        """Apply a key change without resetting the current timer."""
        previous_key = self._settings.key
        self._settings.set_key(key)
        if key != previous_key:
            self.key_changed.emit(key)

    def apply_settings(self, interval_minutes: int, key: SimulatedKey) -> None:
        """Apply validated interval and key settings as one operation."""
        previous_interval = self._settings.interval_minutes
        previous_key = self._settings.key
        self._settings.set_settings(interval_minutes, key)
        if self._state is ActivityState.RUNNING and interval_minutes != previous_interval:
            self._timer.stop()
            self._timer.setInterval(interval_minutes * 60 * 1000)
            self._timer.start()
        if interval_minutes != previous_interval:
            self.interval_changed.emit(interval_minutes)
        if key != previous_key:
            self.key_changed.emit(key)

    def shutdown(self) -> None:
        """Stop activity before the owning application exits."""
        self.stop()

    def fail(self) -> bool:
        """Transition to the error state."""
        return self.transition_to(ActivityState.ERROR)

    def _on_timer_timeout(self) -> None:
        """Submit one repeated keypress while activity is running."""
        if self._state is not ActivityState.RUNNING:
            return

        result = self._input_sender()
        self._last_input_result = result
        if result.success:
            self._record_successful_keypress()
        elif self._is_partial_result(result):
            self._record_partial_failure(result)
        else:
            self._record_failure(result)

    def _record_successful_keypress(self) -> None:
        """Record and publish a successful local keypress timestamp."""
        self._consecutive_failures = 0
        if self._error_message is not None:
            self._error_message = None
            self.error_changed.emit(None)
        self._last_successful_keypress = datetime.now()
        self.last_successful_keypress_changed.emit(self._last_successful_keypress)

    def _record_failure(self, result: InputResult) -> None:
        """Record a failed submission and stop after three consecutive failures."""
        self._consecutive_failures += 1
        self._error_message = result.error_message or "Input submission failed."
        self.error_changed.emit(self._error_message)
        if self._consecutive_failures >= 3:
            self.transition_to(ActivityState.ERROR)

    @staticmethod
    def _is_partial_result(result: InputResult) -> bool:
        """Return whether Windows accepted some but not all activity events."""
        return 0 < result.submitted_events < result.requested_events

    def _record_partial_failure(self, result: InputResult) -> None:
        """Clean up a partial sequence and enter Error immediately."""
        cleanup_result = self._cleanup_sender(self.key, result.submitted_events)
        message = "Input sequence incomplete."
        if self.key is SimulatedKey.SCROLL_LOCK:
            message += " Check Scroll Lock state."
        if result.error_message:
            message += f" {result.error_message}"
        if not cleanup_result.success:
            cleanup_detail = cleanup_result.error_message or "key-release cleanup failed"
            message += f" Cleanup failed: {cleanup_detail}"
        self._error_message = message
        self.error_changed.emit(self._error_message)
        self.transition_to(ActivityState.ERROR)
