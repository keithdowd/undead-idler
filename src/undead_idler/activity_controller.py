"""UI-independent activity state management."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from .models import ActivityState


class InvalidActivityTransition(ValueError):
    """Raised when an activity state transition is not permitted."""


class ActivityController(QObject):
    """Own the activity state and notify observers when it changes."""

    state_changed = Signal(object)

    _allowed_transitions = {
        ActivityState.STOPPED: {ActivityState.RUNNING},
        ActivityState.RUNNING: {ActivityState.STOPPED, ActivityState.ERROR},
        ActivityState.ERROR: {ActivityState.STOPPED, ActivityState.RUNNING},
    }

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._state = ActivityState.STOPPED

    @property
    def state(self) -> ActivityState:
        """Return the current activity state."""
        return self._state

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
        """Transition to the running state."""
        return self.transition_to(ActivityState.RUNNING)

    def stop(self) -> bool:
        """Transition to the stopped state."""
        return self.transition_to(ActivityState.STOPPED)

    def fail(self) -> bool:
        """Transition to the error state."""
        return self.transition_to(ActivityState.ERROR)

