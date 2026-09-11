import pytest
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QComboBox,
)

from undead_idler.settings_dialog import IntervalSettingsDialog
from undead_idler.settings_dialog import apply_interval_dialog
from undead_idler.activity_controller import ActivityController
from undead_idler.models import SimulatedKey
from undead_idler.win_input import InputResult


@pytest.fixture
def qapp():
    return QApplication.instance() or QApplication([])


def test_settings_dialog_initializes_current_interval(qapp):
    dialog = IntervalSettingsDialog(7)

    assert dialog.interval_input.text() == "7"
    assert dialog.findChild(QLineEdit, "interval_input") is dialog.interval_input
    assert dialog.findChild(QLabel, "interval_range_label") is not None


def test_settings_dialog_initializes_and_saves_selected_key(qapp):
    dialog = IntervalSettingsDialog(5, current_key=SimulatedKey.SCROLL_LOCK)

    assert dialog.selected_key is SimulatedKey.SCROLL_LOCK
    assert dialog.findChild(QComboBox, "key_input") is dialog.key_input

    dialog.key_input.setCurrentIndex(dialog.key_input.findData(SimulatedKey.F15))
    dialog.findChild(QDialogButtonBox, "settings_buttons").button(
        QDialogButtonBox.StandardButton.Save
    ).click()

    assert dialog.result() == QDialog.DialogCode.Accepted
    assert dialog.selected_key is SimulatedKey.F15


def test_settings_dialog_has_save_and_cancel_actions(qapp):
    dialog = IntervalSettingsDialog(5)
    buttons = dialog.findChild(QDialogButtonBox, "settings_buttons")

    assert buttons is not None
    assert buttons.button(QDialogButtonBox.StandardButton.Save) is not None
    assert buttons.button(QDialogButtonBox.StandardButton.Cancel) is not None


@pytest.mark.parametrize("value", ["", "abc", "5.5", "0", "11"])
def test_settings_dialog_rejects_invalid_interval(qapp, value):
    dialog = IntervalSettingsDialog(5)
    dialog.interval_input.setText(value)
    dialog.findChild(QDialogButtonBox, "settings_buttons").button(
        QDialogButtonBox.StandardButton.Save
    ).click()

    assert dialog.result() == QDialog.DialogCode.Rejected
    assert dialog.interval_minutes == 5
    assert dialog.validation_message.text() == "Enter a whole number from 1 to 10 minutes."


def test_settings_dialog_accepts_valid_interval(qapp):
    dialog = IntervalSettingsDialog(5)
    dialog.interval_input.setText("7")
    dialog.findChild(QDialogButtonBox, "settings_buttons").button(
        QDialogButtonBox.StandardButton.Save
    ).click()

    assert dialog.result() == QDialog.DialogCode.Accepted
    assert dialog.interval_minutes == 7


def test_accepted_settings_apply_to_controller(qapp):
    controller = ActivityController(
        input_sender=lambda: InputResult(True, 2, 2),
    )
    dialog = IntervalSettingsDialog(controller.interval_minutes)
    dialog.interval_input.setText("7")
    dialog.findChild(QDialogButtonBox, "settings_buttons").button(
        QDialogButtonBox.StandardButton.Save
    ).click()

    assert apply_interval_dialog(controller, dialog) is True
    assert controller.interval_minutes == 7


def test_key_only_setting_change_does_not_restart_timer(qapp):
    controller = ActivityController(input_sender=lambda: InputResult(True, 2, 2))
    controller.start()
    start_count = controller._timer.timerId()
    dialog = IntervalSettingsDialog(controller.interval_minutes, current_key=SimulatedKey.SCROLL_LOCK)
    dialog.key_input.setCurrentIndex(dialog.key_input.findData(SimulatedKey.SCROLL_LOCK))
    dialog.findChild(QDialogButtonBox, "settings_buttons").button(
        QDialogButtonBox.StandardButton.Save
    ).click()

    assert apply_interval_dialog(controller, dialog) is True
    assert controller.key is SimulatedKey.SCROLL_LOCK
    assert controller._timer.timerId() == start_count


def test_canceled_settings_leave_controller_unchanged(qapp, monkeypatch):
    controller = ActivityController(
        input_sender=lambda: InputResult(True, 2, 2),
    )
    dialog = IntervalSettingsDialog(controller.interval_minutes)
    dialog.interval_input.setText("7")
    monkeypatch.setattr(
        dialog,
        "exec",
        lambda: QDialog.DialogCode.Rejected,
    )

    assert apply_interval_dialog(controller, dialog) is False
    assert controller.interval_minutes == 5
