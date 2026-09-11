"""UI-independent activity state management."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from PySide6.QtCore import QObject, QTimer, Signal

from .models import ActivityState, format_timestamp
from .settings_controller import RuntimeSettings
from .win_input import InputResult, send_f15_keypress_with_result


class InvalidActivityTransition(ValueError):
    """Raised when an activity state transition is not permitted."""


InputSender = Callable[[], InputResult]


class ActivityController(QObject):
    """Own the activity state and notify observers when it changes."""

    state_changed = Signal(object)
    last_successful_keypress_changed = Signal(object)
    interval_changed = Signal(int)
    error_changed = Signal(object)

    _allowed_transitions = {
        ActivityState.STOPPED: {ActivityState.RUNNING, ActivityState.ERROR},
        ActivityState.RUNNING: {ActivityState.STOPPED, ActivityState.ERROR},
        ActivityState.ERROR: {ActivityState.STOPPED, ActivityState.RUNNING},
    }

    def __init__(
        self,
        input_sender: InputSender = send_f15_keypress_with_result,
        settings: RuntimeSettings | None = None,
        timer: QTimer | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._state = ActivityState.STOPPED
        self._input_sender = input_sender
        self._settings = settings or RuntimeSettings()
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
