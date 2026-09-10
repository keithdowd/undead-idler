"""Qt application bootstrap for Undead Idler."""

from __future__ import annotations

import sys
from collections.abc import Sequence

from PySide6.QtWidgets import QApplication

from .activity_controller import ActivityController
from .tray_controller import TrayIconController


def create_application(argv: Sequence[str] | None = None) -> QApplication:
    """Create the application object without creating a main window."""
    arguments = list(sys.argv if argv is None else argv)
    application = QApplication(arguments)
    application.setQuitOnLastWindowClosed(False)
    return application


def run_application(application: QApplication) -> int:
    """Run the Qt event loop until the tray controller requests Exit."""
    return application.exec()


def main(argv: Sequence[str] | None = None) -> int:
    """Start the tray application in its initial stopped state."""
    application = create_application(argv)
    activity_controller = ActivityController(parent=application)
    TrayIconController(activity_controller, parent=application)
    return run_application(application)
