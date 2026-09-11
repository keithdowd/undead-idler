from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QDialog, QLabel

from undead_idler.activity_controller import ActivityController
from undead_idler.models import ActivityState
from undead_idler.models import SimulatedKey
from undead_idler.tray_controller import (
    TrayIconController,
    format_tooltip,
    icon_directory,
)
from undead_idler.win_input import InputResult


@pytest.fixture
def qapp():
    return QApplication.instance() or QApplication([])


def make_controller():
    return ActivityController(input_sender=lambda: InputResult(True, 2, 2))


def test_tray_controller_starts_with_stopped_icon(qapp):
    controller = make_controller()
    tray = TrayIconController(controller)

    assert not tray.icon.isNull()
    assert tray.icon_path(ActivityState.STOPPED).name == "undead-idler-stopped.ico"
    assert tray.tray_icon.isVisible()


def test_tray_controller_initializes_tooltip_before_start(qapp):
    tray = TrayIconController(make_controller())

    assert tray.tray_icon.toolTip() == (
        "Status: Stopped\n"
        "Interval: 5 minutes\n"
        "Key: F15\n"
        "Last keypress: None"
    )


@pytest.mark.parametrize(
    ("state", "filename"),
    [
        (ActivityState.STOPPED, "undead-idler-stopped.ico"),
        (ActivityState.RUNNING, "undead-idler-running.ico"),
        (ActivityState.ERROR, "undead-idler-error.ico"),
    ],
)
def test_tray_controller_has_icon_for_each_state(qapp, state, filename):
    tray = TrayIconController(make_controller())

    tray.set_state(state)

    assert not tray.icon.isNull()
    assert tray.icon_path(state) == icon_directory() / filename
    assert tray.icon_path(state).is_file()


def test_activity_state_changes_update_tray_icon(qapp):
    controller = make_controller()
    tray = TrayIconController(controller)

    controller.transition_to(ActivityState.RUNNING)
    assert tray.icon_path(controller.state).name == "undead-idler-running.ico"

    controller.transition_to(ActivityState.ERROR)
    assert tray.icon_path(controller.state).name == "undead-idler-error.ico"


def test_tray_menu_contains_required_actions(qapp):
    tray = TrayIconController(make_controller())

    assert [action.text() for action in tray.menu.actions() if not action.isSeparator()] == [
        "Start",
        "Stop",
        "Settings",
        "About",
        "Exit",
    ]
    assert tray.start_action.isEnabled()
    assert not tray.stop_action.isEnabled()
    assert tray.settings_action.isEnabled()
    assert tray.about_action.isEnabled()
    assert tray.exit_action.isEnabled()


def test_start_and_stop_actions_follow_activity_state(qapp):
    controller = make_controller()
    tray = TrayIconController(controller)

    tray.start_action.trigger()
    assert controller.state is ActivityState.RUNNING
    assert not tray.start_action.isEnabled()
    assert tray.stop_action.isEnabled()

    tray.stop_action.trigger()
    assert controller.state is ActivityState.STOPPED
    assert tray.start_action.isEnabled()
    assert not tray.stop_action.isEnabled()


def test_start_is_idempotent_and_stop_is_safe_when_repeated(qapp):
    calls = []
    controller = ActivityController(
        input_sender=lambda: calls.append(True) or InputResult(True, 2, 2),
    )
    tray = TrayIconController(controller)

    tray.start_action.trigger()
    tray.start_action.trigger()
    tray.stop_action.trigger()
    tray.stop_action.trigger()

    assert calls == [True]
    assert controller.state is ActivityState.STOPPED


def test_exit_action_emits_exit_request(qapp):
    tray = TrayIconController(make_controller())
    requests = []
    tray.exit_requested.connect(lambda: requests.append(True))

    tray.exit_action.trigger()

    assert requests == [True]


def test_tooltip_shows_stopped_state_interval_and_none_timestamp(qapp):
    controller = make_controller()

    tooltip = format_tooltip(controller)

    assert "Status: Stopped" in tooltip
    assert "Interval: 5 minutes" in tooltip
    assert "Key: F15" in tooltip
    assert "Last keypress: None" in tooltip
    assert "Smart Mode" not in tooltip
    assert "Activity" not in tooltip
    assert "Error:" not in tooltip


def test_tooltip_shows_timestamp_after_successful_start(qapp):
    controller = make_controller()
    controller.start()

    tooltip = format_tooltip(controller)

    assert "Status: Running" in tooltip
    assert "Last keypress: None" not in tooltip


def test_tooltip_shows_automatic_stop_message_in_error_state(qapp):
    controller = make_controller()
    controller.start()
    controller._consecutive_failures = 3
    controller._error_message = "input blocked"
    controller.transition_to(ActivityState.ERROR)

    tooltip = format_tooltip(controller)

    assert "Status: Error" in tooltip
    assert "Error: Activity stopped after 3 consecutive failures." in tooltip
    assert "Details: input blocked" in tooltip


def test_tooltip_shows_initial_start_error_without_three_failure_claim(qapp):
    controller = ActivityController(
        input_sender=lambda: InputResult(False, 2, 0, error_message="input blocked")
    )
    controller.start()

    tooltip = format_tooltip(controller)

    assert "Status: Error" in tooltip
    assert "Error: Activity could not start." in tooltip
    assert "three consecutive" not in tooltip
    assert "Details: input blocked" in tooltip


def test_tooltip_shows_warning_for_running_failure(qapp):
    results = iter(
        [
            InputResult(True, 2, 2),
            InputResult(False, 2, 0, error_message="input blocked"),
        ]
    )
    controller = ActivityController(input_sender=lambda: next(results))
    controller.start()
    controller._on_timer_timeout()

    tooltip = format_tooltip(controller)

    assert "Status: Running" in tooltip
    assert "Warning: Input failed (1 of 3 consecutive attempts)." in tooltip
    assert "Details: input blocked" in tooltip


def test_tray_tooltip_refreshes_when_interval_changes(qapp):
    controller = make_controller()
    tray = TrayIconController(controller)

    controller.set_interval(8)

    assert "Interval: 8 minutes" in tray.tray_icon.toolTip()


def test_tray_tooltip_refreshes_when_key_changes(qapp):
    controller = make_controller()
    tray = TrayIconController(controller)

    controller.set_key(SimulatedKey.SCROLL_LOCK)

    assert "Key: Scroll Lock" in tray.tray_icon.toolTip()


def test_about_action_shows_version_and_description_without_changing_activity(qapp):
    controller = make_controller()
    tray = TrayIconController(controller)
    tray.about_action.trigger()

    dialog = tray._about_dialog
    assert dialog is not None
    assert dialog.isVisible()
    assert dialog.findChild(QLabel, "about_version").text() == "Version 0.2.0"
    assert "F15 or paired Scroll Lock" in dialog.findChild(
        QLabel, "about_description"
    ).text()
    assert controller.state is ActivityState.STOPPED

    tray.about_action.trigger()
    assert tray._about_dialog is dialog
    dialog.accept()
    assert dialog.result() == QDialog.DialogCode.Accepted


def test_shutdown_stops_activity_hides_icon_and_detaches_menu(qapp, monkeypatch):
    controller = make_controller()
    tray = TrayIconController(controller)
    tray.start_action.trigger()
    quit_calls = []
    monkeypatch.setattr(qapp, "quit", lambda: quit_calls.append(True))

    tray.shutdown()

    assert controller.state is ActivityState.STOPPED
    assert not tray.tray_icon.isVisible()
    assert tray.tray_icon.contextMenu() is None
    assert quit_calls == [True]


def test_shutdown_is_idempotent(qapp, monkeypatch):
    controller = make_controller()
    tray = TrayIconController(controller)
    quit_calls = []
    monkeypatch.setattr(qapp, "quit", lambda: quit_calls.append(True))

    tray.shutdown()
    tray.shutdown()

    assert quit_calls == [True]


def test_icon_directory_is_not_tied_to_development_machine_path():
    assert isinstance(icon_directory(), Path)
    assert icon_directory().name == "icons"
