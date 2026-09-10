import pytest
from PySide6.QtWidgets import QApplication, QDialogButtonBox, QLabel, QLineEdit

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

