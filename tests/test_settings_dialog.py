import pytest
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
)

from undead_idler.settings_dialog import IntervalSettingsDialog


@pytest.fixture
def qapp():
    return QApplication.instance() or QApplication([])


def test_settings_dialog_initializes_current_interval(qapp):
    dialog = IntervalSettingsDialog(7)

    assert dialog.interval_input.text() == "7"
    assert dialog.findChild(QLineEdit, "interval_input") is dialog.interval_input
    assert dialog.findChild(QLabel, "interval_range_label") is not None


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
