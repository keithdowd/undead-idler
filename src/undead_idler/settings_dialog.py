"""Interval settings dialog."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
)

from .settings_controller import RuntimeSettings


class IntervalSettingsDialog(QDialog):
    """Present the session interval setting and Save/Cancel actions."""

    def __init__(self, current_interval: int, parent: QDialog | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Undead Idler Settings")

        self.interval_input = QLineEdit(str(current_interval), self)
        self.interval_input.setObjectName("interval_input")
        self.interval_input.setPlaceholderText("Minutes")

        range_label = QLabel(
            f"Enter a whole number from {RuntimeSettings.MIN_INTERVAL_MINUTES} "
            f"to {RuntimeSettings.MAX_INTERVAL_MINUTES} minutes.",
            self,
        )
        range_label.setObjectName("interval_range_label")

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.setObjectName("settings_buttons")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QFormLayout(self)
        layout.addRow("Interval (minutes):", self.interval_input)
        layout.addRow(range_label)
        layout.addRow(buttons)

