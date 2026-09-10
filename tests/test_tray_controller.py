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


def test_icon_directory_is_not_tied_to_development_machine_path():
    assert isinstance(icon_directory(), Path)
    assert icon_directory().name == "icons"
