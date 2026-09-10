"""UI-independent activity state management."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from PySide6.QtCore import QObject, Signal

from .models import ActivityState
from .win_input import InputResult, send_f15_keypress_with_result


class InvalidActivityTransition(ValueError):
    """Raised when an activity state transition is not permitted."""


InputSender = Callable[[], InputResult]


class ActivityController(QObject):
    """Own the activity state and notify observers when it changes."""

    state_changed = Signal(object)

    _allowed_transitions = {
        ActivityState.STOPPED: {ActivityState.RUNNING},
        ActivityState.RUNNING: {ActivityState.STOPPED, ActivityState.ERROR},
        ActivityState.ERROR: {ActivityState.STOPPED, ActivityState.RUNNING},
    }

    def __init__(
        self,
        input_sender: InputSender = send_f15_keypress_with_result,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._state = ActivityState.STOPPED
        self._input_sender = input_sender
        self._consecutive_failures = 0
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
    def last_successful_keypress(self) -> datetime | None:
        """Return the timestamp of the most recent successful keypress."""
        return self._last_successful_keypress

    def transition_to(self, state: ActivityState) -> bool:
        """Change state and notify observers; return whether it changed."""
        if state is self._state:
            return False

        if state not in self._allowed_transitions[self._state]:
            raise InvalidActivityTransition(
                f"cannot transition from {self._state.value} to {state.value}"
            )

        self._state = state
        self.state_changed.emit(state)
        return True

    def start(self) -> bool:
        """Send the initial keypress and transition to the running state."""
        if self._state is ActivityState.RUNNING:
            return False

        self._consecutive_failures = 0
        result = self._input_sender()
        self._last_input_result = result
        if not result.success:
            return False

        self._last_successful_keypress = datetime.now()
        return self.transition_to(ActivityState.RUNNING)

    def stop(self) -> bool:
        """Transition to the stopped state."""
        return self.transition_to(ActivityState.STOPPED)

    def fail(self) -> bool:
        """Transition to the error state."""
        return self.transition_to(ActivityState.ERROR)
