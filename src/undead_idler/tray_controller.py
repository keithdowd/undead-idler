"""System-tray icon state management."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from .activity_controller import ActivityController
from .about_dialog import AboutDialog
from .models import ActivityState
from .settings_dialog import open_interval_settings


def icon_directory() -> Path:
    """Return the icon directory for source and bundled application runs."""
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root is not None:
        return Path(bundle_root) / "assets" / "icons"
    return Path(__file__).resolve().parents[2] / "assets" / "icons"


def format_tooltip(activity_controller: ActivityController) -> str:
    """Format the tray tooltip from the current runtime state."""
    state = activity_controller.state.value.title()
    lines = [
        f"Status: {state}",
        f"Interval: {activity_controller.interval_minutes} minutes",
        f"Key: {activity_controller.key.value}",
        f"Last keypress: {activity_controller.last_successful_keypress_text}",
    ]
    if activity_controller.state is ActivityState.ERROR:
        if activity_controller.consecutive_failures >= 3:
            lines.append("Error: Activity stopped after 3 consecutive failures.")
        else:
            lines.append("Error: Activity could not start.")
        if activity_controller.error_message:
            lines.append(f"Details: {activity_controller.error_message}")
    elif activity_controller.consecutive_failures:
        lines.append(
            "Warning: Input failed "
            f"({activity_controller.consecutive_failures} of 3 consecutive attempts)."
        )
        if activity_controller.error_message:
            lines.append(f"Details: {activity_controller.error_message}")
    return "\n".join(lines)


class TrayIconController(QObject):
    """Display the activity controller state in the Windows notification area."""

    exit_requested = Signal()

    _icon_names = {
        ActivityState.STOPPED: "undead-idler-stopped.ico",
        ActivityState.RUNNING: "undead-idler-running.ico",
        ActivityState.ERROR: "undead-idler-error.ico",
    }

    def __init__(
        self,
        activity_controller: ActivityController,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.activity_controller = activity_controller
        self.tray_icon = QSystemTrayIcon(self)
        self.menu = QMenu()
        self.start_action = QAction("Start", self.menu)
        self.stop_action = QAction("Stop", self.menu)
        self.settings_action = QAction("Settings", self.menu)
        self.about_action = QAction("About", self.menu)
        self.exit_action = QAction("Exit", self.menu)
        self.menu.addAction(self.start_action)
        self.menu.addAction(self.stop_action)
        self.menu.addSeparator()
        self.menu.addAction(self.settings_action)
        self.menu.addSeparator()
        self.menu.addAction(self.about_action)
        self.menu.addSeparator()
        self.menu.addAction(self.exit_action)
        self.tray_icon.setContextMenu(self.menu)
        self._icons = {
            state: QIcon(str(icon_directory() / filename))
            for state, filename in self._icon_names.items()
        }
        self.activity_controller.state_changed.connect(self.set_state)
        self.activity_controller.state_changed.connect(self._refresh_tooltip)
        self.activity_controller.interval_changed.connect(self._refresh_tooltip)
        self.activity_controller.key_changed.connect(self._refresh_tooltip)
        self.activity_controller.last_successful_keypress_changed.connect(
            self._refresh_tooltip
        )
        self.activity_controller.error_changed.connect(self._refresh_tooltip)
        self.start_action.triggered.connect(self.activity_controller.start)
        self.stop_action.triggered.connect(self.activity_controller.stop)
        self.settings_action.triggered.connect(
            lambda: open_interval_settings(self.activity_controller, self.menu)
        )
        self.about_action.triggered.connect(self.show_about)
        self.exit_action.triggered.connect(self.exit_requested.emit)
        self.exit_requested.connect(self.shutdown)
        self._shutdown_complete = False
        self._about_dialog: AboutDialog | None = None
        self.set_state(ActivityState.STOPPED)
        self._refresh_tooltip()
        self.tray_icon.show()

    @property
    def icon(self) -> QIcon:
        """Return the currently displayed icon."""
        return self.tray_icon.icon()

    def set_state(self, state: ActivityState) -> None:
        """Update the tray icon to represent an activity state."""
        self.tray_icon.setIcon(self._icons[state])
        self.start_action.setEnabled(state is not ActivityState.RUNNING)
        self.stop_action.setEnabled(state is not ActivityState.STOPPED)

    def _refresh_tooltip(self, *_args) -> None:
        """Refresh the tray tooltip after a controller value changes."""
        self.tray_icon.setToolTip(format_tooltip(self.activity_controller))

    def icon_path(self, state: ActivityState) -> Path:
        """Return the asset path used for a state."""
        return icon_directory() / self._icon_names[state]

    def show_about(self) -> None:
        """Show the reusable About dialog without changing activity."""
        if self._about_dialog is None:
            self._about_dialog = AboutDialog(self.menu)
        self._about_dialog.show()
        self._about_dialog.raise_()
        self._about_dialog.activateWindow()

    def shutdown(self) -> None:
        """Stop activity, remove the tray icon, and quit the Qt application."""
        if self._shutdown_complete:
            return
        self._shutdown_complete = True
        self.activity_controller.shutdown()
        self.tray_icon.setContextMenu(None)
        self.tray_icon.hide()
        application = QApplication.instance()
        if application is not None:
            application.quit()
