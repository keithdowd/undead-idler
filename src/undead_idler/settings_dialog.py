"""Runtime interval and simulated-key settings dialog."""

from __future__ import annotations

from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QWidget,
)

from .models import SimulatedKey
from .settings_controller import InvalidInterval, RuntimeSettings


class IntervalSettingsDialog(QDialog):
    """Present session interval/key settings and Save/Cancel actions."""

    def __init__(
        self,
        current_interval: int,
        parent: QDialog | None = None,
        current_key: SimulatedKey = SimulatedKey.F15,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Undead Idler Settings")
        self._saved_interval = current_interval
        self._saved_key = current_key

        self.interval_input = QLineEdit(str(current_interval), self)
        self.interval_input.setObjectName("interval_input")
        self.interval_input.setPlaceholderText("Minutes")
        self.interval_input.setValidator(
            QIntValidator(
                RuntimeSettings.MIN_INTERVAL_MINUTES,
                RuntimeSettings.MAX_INTERVAL_MINUTES,
                self.interval_input,
            )
        )

        self.key_input = QComboBox(self)
        self.key_input.setObjectName("key_input")
        for key in SimulatedKey:
            self.key_input.addItem(key.value, key)
        self.key_input.setCurrentIndex(self.key_input.findData(current_key))

        range_label = QLabel(
            f"Enter a whole number from {RuntimeSettings.MIN_INTERVAL_MINUTES} "
            f"to {RuntimeSettings.MAX_INTERVAL_MINUTES} minutes.",
            self,
        )
        range_label.setObjectName("interval_range_label")

        self.validation_message = QLabel(self)
        self.validation_message.setObjectName("validation_message")
        self.validation_message.setStyleSheet("color: #b00020;")
        self.validation_message.hide()

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.setObjectName("settings_buttons")
        buttons.accepted.connect(self._handle_save)
        buttons.rejected.connect(self.reject)

        layout = QFormLayout(self)
        layout.addRow("Interval (minutes):", self.interval_input)
        layout.addRow(range_label)
        layout.addRow("Key:", self.key_input)
        layout.addRow(self.validation_message)
        layout.addRow(buttons)

    @property
    def interval_minutes(self) -> int:
        """Return the interval most recently accepted by the dialog."""
        return self._saved_interval

    @property
    def selected_key(self) -> SimulatedKey:
        """Return the key most recently accepted by the dialog."""
        return self._saved_key

    def _handle_save(self) -> None:
        """Validate the input before accepting the dialog."""
        text = self.interval_input.text().strip()
        try:
            interval = int(text)
            RuntimeSettings().set_interval(interval)
        except (InvalidInterval, ValueError):
            self.validation_message.setText(
                "Enter a whole number from 1 to 10 minutes."
            )
            self.validation_message.show()
            return

        self._saved_interval = interval
        self._saved_key = self.key_input.currentData()
        self.accept()


def apply_interval_dialog(activity_controller, dialog: IntervalSettingsDialog) -> bool:
    """Apply an accepted dialog value and return whether it was saved."""
    result = dialog.result()
    if result == 0:
        result = dialog.exec()
    if result != QDialog.DialogCode.Accepted:
        return False

    activity_controller.apply_settings(dialog.interval_minutes, dialog.selected_key)
    return True


def open_interval_settings(activity_controller, parent: QWidget | None = None) -> bool:
    """Open interval settings and apply the value when the user saves it."""
    dialog = IntervalSettingsDialog(
        activity_controller.interval_minutes,
        parent,
        activity_controller.key,
    )
    return apply_interval_dialog(activity_controller, dialog)
