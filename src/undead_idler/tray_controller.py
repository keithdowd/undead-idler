"""System-tray icon state management."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QSystemTrayIcon

from .activity_controller import ActivityController
from .models import ActivityState


def icon_directory() -> Path:
    """Return the icon directory for source and bundled application runs."""
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root is not None:
        return Path(bundle_root) / "assets" / "icons"
    return Path(__file__).resolve().parents[2] / "assets" / "icons"


class TrayIconController:
    """Display the activity controller state in the Windows notification area."""

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
        self.activity_controller = activity_controller
        self.tray_icon = QSystemTrayIcon(parent)
        self._icons = {
            state: QIcon(str(icon_directory() / filename))
            for state, filename in self._icon_names.items()
        }
        self.activity_controller.state_changed.connect(self.set_state)
        self.set_state(ActivityState.STOPPED)
        self.tray_icon.show()

    @property
    def icon(self) -> QIcon:
        """Return the currently displayed icon."""
        return self.tray_icon.icon()

    def set_state(self, state: ActivityState) -> None:
        """Update the tray icon to represent an activity state."""
        self.tray_icon.setIcon(self._icons[state])

    def icon_path(self, state: ActivityState) -> Path:
        """Return the asset path used for a state."""
        return icon_directory() / self._icon_names[state]
