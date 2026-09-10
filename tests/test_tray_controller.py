from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from undead_idler.activity_controller import ActivityController
from undead_idler.models import ActivityState
from undead_idler.tray_controller import TrayIconController, icon_directory
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
        "Exit",
    ]
    assert tray.start_action.isEnabled()
    assert not tray.stop_action.isEnabled()
    assert tray.settings_action.isEnabled()
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


def test_icon_directory_is_not_tied_to_development_machine_path():
    assert isinstance(icon_directory(), Path)
    assert icon_directory().name == "icons"
