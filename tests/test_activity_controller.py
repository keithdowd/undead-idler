import pytest

from undead_idler.activity_controller import (
    ActivityController,
    InvalidActivityTransition,
)
from undead_idler.models import ActivityState
from undead_idler.win_input import InputResult


def successful_input():
    return InputResult(success=True, requested_events=2, submitted_events=2)


def failed_input():
    return InputResult(
        success=False,
        requested_events=2,
        submitted_events=0,
        error_message="input blocked",
    )


def test_controller_starts_stopped():
    controller = ActivityController()

    assert controller.state is ActivityState.STOPPED


def test_state_changes_emit_once_and_repeated_start_is_idempotent():
    calls = []
    controller = ActivityController(input_sender=lambda: calls.append(True) or successful_input())
    changes = []
    controller.state_changed.connect(changes.append)

    assert controller.start() is True
    assert controller.start() is False

    assert controller.state is ActivityState.RUNNING
    assert changes == [ActivityState.RUNNING]
    assert calls == [True]


def test_running_activity_can_stop_or_fail_and_error_can_retry():
    controller = ActivityController(input_sender=successful_input)

    controller.start()
    assert controller.fail() is True
    assert controller.state is ActivityState.ERROR
    assert controller.start() is True
    assert controller.state is ActivityState.RUNNING
    assert controller.stop() is True
    assert controller.state is ActivityState.STOPPED


def test_invalid_transition_is_rejected():
    controller = ActivityController(input_sender=successful_input)

    with pytest.raises(InvalidActivityTransition):
        controller.fail()


def test_start_sends_immediately_and_records_success_timestamp():
    calls = []
    controller = ActivityController(input_sender=lambda: calls.append(True) or successful_input())

    assert controller.start() is True
    assert calls == [True]
    assert controller.state is ActivityState.RUNNING
    assert controller.last_input_result.success is True
    assert controller.last_successful_keypress is not None


def test_failed_initial_keypress_does_not_start_or_record_timestamp():
    controller = ActivityController(input_sender=failed_input)

    assert controller.start() is False
    assert controller.state is ActivityState.STOPPED
    assert controller.last_input_result.error_message == "input blocked"
    assert controller.last_successful_keypress is None
