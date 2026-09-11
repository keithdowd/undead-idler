from PySide6.QtCore import QObject

from undead_idler.windows_lifecycle import (
    PBT_APMSUSPEND,
    WM_ENDSESSION,
    WM_POWERBROADCAST,
    WM_QUERYENDSESSION,
    WM_WTSSESSION_CHANGE,
    WTS_SESSION_LOCK,
    WindowsLifecycleMonitor,
)
from undead_idler.activity_controller import ActivityController
from undead_idler.models import ActivityState
from undead_idler.win_input import InputResult


def test_lifecycle_messages_request_stop():
    monitor = WindowsLifecycleMonitor(QObject())
    reasons = []
    monitor.stop_requested.connect(reasons.append)

    assert monitor.handle_message(WM_WTSSESSION_CHANGE, WTS_SESSION_LOCK) is True
    assert monitor.handle_message(WM_POWERBROADCAST, PBT_APMSUSPEND) is True
    assert monitor.handle_message(WM_QUERYENDSESSION) is True
    assert monitor.handle_message(WM_ENDSESSION) is True

    assert reasons == ["session lock", "suspend", "shutdown", "shutdown"]


def test_resume_and_unrelated_messages_do_not_request_stop():
    monitor = WindowsLifecycleMonitor(QObject())
    reasons = []
    monitor.stop_requested.connect(reasons.append)

    assert monitor.handle_message(WM_WTSSESSION_CHANGE, 0x8) is False
    assert monitor.handle_message(WM_POWERBROADCAST, 0x12) is False
    assert monitor.handle_message(0x1234) is False
    assert reasons == []


def test_close_is_safe_and_idempotent():
    monitor = WindowsLifecycleMonitor(QObject())

    monitor.close()
    monitor.close()


def test_lifecycle_stop_signal_stops_running_activity():
    controller = ActivityController(input_sender=lambda: InputResult(True, 2, 2))
    controller.start()
    monitor = WindowsLifecycleMonitor(QObject())
    monitor.stop_requested.connect(lambda _reason: controller.stop())

    monitor.handle_message(WM_POWERBROADCAST, PBT_APMSUSPEND)

    assert controller.state is ActivityState.STOPPED
