import pytest

from undead_idler.activity_controller import (
    ActivityController,
    InvalidActivityTransition,
)
from undead_idler.models import ActivityState, format_timestamp
from undead_idler.settings_controller import RuntimeSettings
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


class FakeSignal:
    def __init__(self):
        self._callbacks = []

    def connect(self, callback):
        self._callbacks.append(callback)

    def emit(self):
        for callback in self._callbacks:
            callback()


class FakeTimer:
    def __init__(self):
        self.timeout = FakeSignal()
        self._interval = 0
        self._active = False

    def setInterval(self, interval):
        self._interval = interval

    def interval(self):
        return self._interval

    def start(self):
        self._active = True

    def stop(self):
        self._active = False

    def isActive(self):
        return self._active


def make_controller(input_sender=successful_input, settings=None, timer=None):
    return ActivityController(
        input_sender=input_sender,
        settings=settings,
        timer=timer or FakeTimer(),
    )


def test_controller_starts_stopped():
    controller = make_controller()

    assert controller.state is ActivityState.STOPPED


def test_state_changes_emit_once_and_repeated_start_is_idempotent():
    calls = []
    controller = make_controller(
        input_sender=lambda: calls.append(True) or successful_input()
    )
    changes = []
    controller.state_changed.connect(changes.append)

    assert controller.start() is True
    assert controller.start() is False

    assert controller.state is ActivityState.RUNNING
    assert changes == [ActivityState.RUNNING]
    assert calls == [True]


def test_running_activity_can_stop_or_fail_and_error_can_retry():
    controller = make_controller(input_sender=successful_input)

    controller.start()
    assert controller.fail() is True
    assert controller.state is ActivityState.ERROR
    assert controller.start() is True
    assert controller.state is ActivityState.RUNNING
    assert controller.stop() is True
    assert controller.state is ActivityState.STOPPED


def test_invalid_transition_is_rejected():
    controller = make_controller(input_sender=successful_input)

    with pytest.raises(InvalidActivityTransition):
        controller.fail()


def test_start_sends_immediately_and_records_success_timestamp():
    calls = []
    controller = make_controller(
        input_sender=lambda: calls.append(True) or successful_input()
    )

    assert controller.start() is True
    assert calls == [True]
    assert controller.state is ActivityState.RUNNING
    assert controller.last_input_result.success is True
    assert controller.last_successful_keypress is not None
    assert controller.last_successful_keypress_text != "None"


def test_failed_initial_keypress_does_not_start_or_record_timestamp():
    controller = make_controller(input_sender=failed_input)

    assert controller.start() is False
    assert controller.state is ActivityState.STOPPED
    assert controller.last_input_result.error_message == "input blocked"
    assert controller.consecutive_failures == 1
    assert controller.error_message == "input blocked"
    assert controller.last_successful_keypress is None


def test_start_configures_and_starts_one_timer():
    timer = FakeTimer()
    settings = RuntimeSettings()
    settings.set_interval(2)
    controller = make_controller(settings=settings, timer=timer)

    assert controller.start() is True
    assert timer.interval() == 2 * 60 * 1000
    assert timer.isActive() is True


def test_timer_timeout_submits_one_repeated_keypress():
    calls = []
    timer = FakeTimer()
    controller = make_controller(
        input_sender=lambda: calls.append(True) or successful_input(),
        timer=timer,
    )

    controller.start()
    timer.timeout.emit()

    assert calls == [True, True]


def test_stop_deactivates_timer_and_ignores_later_timeout():
    calls = []
    timer = FakeTimer()
    controller = make_controller(
        input_sender=lambda: calls.append(True) or successful_input(),
        timer=timer,
    )

    controller.start()
    controller.stop()
    timer.timeout.emit()

    assert timer.isActive() is False
    assert controller.consecutive_failures == 0
    assert calls == [True]


def test_successful_timestamp_uses_required_local_display_format():
    from datetime import datetime

    timestamp = datetime(2026, 9, 9, 14, 32, 0)

    assert format_timestamp(timestamp) == "2026-09-09 14:32:00"
    assert format_timestamp(None) == "None"


def test_successful_timestamp_notification_and_failed_timeout_behavior():
    results = iter([successful_input(), failed_input()])
    timer = FakeTimer()
    controller = make_controller(input_sender=lambda: next(results), timer=timer)
    timestamps = []
    controller.last_successful_keypress_changed.connect(timestamps.append)

    controller.start()
    first_timestamp = controller.last_successful_keypress
    timer.timeout.emit()

    assert len(timestamps) == 1
    assert timestamps[0] is first_timestamp
    assert controller.last_successful_keypress is first_timestamp


def test_three_consecutive_timer_failures_stop_activity_and_expose_error():
    results = iter([successful_input(), failed_input(), failed_input(), failed_input()])
    timer = FakeTimer()
    controller = make_controller(input_sender=lambda: next(results), timer=timer)

    controller.start()
    timer.timeout.emit()
    timer.timeout.emit()
    timer.timeout.emit()

    assert controller.state is ActivityState.ERROR
    assert timer.isActive() is False
    assert controller.consecutive_failures == 3
    assert controller.error_message == "input blocked"


def test_successful_keypress_resets_failure_count_and_error_message():
    results = iter([successful_input(), failed_input(), successful_input()])
    timer = FakeTimer()
    controller = make_controller(input_sender=lambda: next(results), timer=timer)

    controller.start()
    timer.timeout.emit()
    assert controller.consecutive_failures == 1

    timer.timeout.emit()

    assert controller.state is ActivityState.RUNNING
    assert controller.consecutive_failures == 0
    assert controller.error_message is None


def test_start_retries_after_automatic_error():
    results = iter([successful_input(), failed_input(), failed_input(), failed_input(), successful_input()])
    timer = FakeTimer()
    controller = make_controller(input_sender=lambda: next(results), timer=timer)

    controller.start()
    timer.timeout.emit()
    timer.timeout.emit()
    timer.timeout.emit()
    assert controller.state is ActivityState.ERROR

    assert controller.start() is True
    assert controller.state is ActivityState.RUNNING
    assert controller.consecutive_failures == 0
    assert controller.error_message is None


def test_stop_resets_failure_state_but_preserves_successful_timestamp():
    results = iter([successful_input(), failed_input(), failed_input()])
    timer = FakeTimer()
    controller = make_controller(input_sender=lambda: next(results), timer=timer)

    controller.start()
    timestamp = controller.last_successful_keypress
    timer.timeout.emit()
    timer.timeout.emit()
    assert controller.consecutive_failures == 2

    controller.stop()

    assert controller.state is ActivityState.STOPPED
    assert controller.consecutive_failures == 0
    assert controller.error_message is None
    assert controller.last_successful_keypress is timestamp
    assert timer.isActive() is False


def test_shutdown_stops_active_timer_and_is_safe_to_repeat():
    timer = FakeTimer()
    controller = make_controller(timer=timer)

    controller.start()
    controller.shutdown()
    controller.shutdown()

    assert controller.state is ActivityState.STOPPED
    assert timer.isActive() is False
