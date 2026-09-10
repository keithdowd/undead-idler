import pytest

from undead_idler.activity_controller import (
    ActivityController,
    InvalidActivityTransition,
)
from undead_idler.models import ActivityState


def test_controller_starts_stopped():
    controller = ActivityController()

    assert controller.state is ActivityState.STOPPED


def test_state_changes_emit_once_and_repeated_start_is_idempotent():
    controller = ActivityController()
    changes = []
    controller.state_changed.connect(changes.append)

    assert controller.start() is True
    assert controller.start() is False

    assert controller.state is ActivityState.RUNNING
    assert changes == [ActivityState.RUNNING]


def test_running_activity_can_stop_or_fail_and_error_can_retry():
    controller = ActivityController()

    controller.start()
    assert controller.fail() is True
    assert controller.state is ActivityState.ERROR
    assert controller.start() is True
    assert controller.state is ActivityState.RUNNING
    assert controller.stop() is True
    assert controller.state is ActivityState.STOPPED


def test_invalid_transition_is_rejected():
    controller = ActivityController()

    with pytest.raises(InvalidActivityTransition):
        controller.fail()

