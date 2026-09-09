"""Qt application bootstrap for Undead Idler."""

from __future__ import annotations

import sys
from collections.abc import Sequence

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication


def create_application(argv: Sequence[str] | None = None) -> QApplication:
    """Create the application object without creating a main window."""
    arguments = list(sys.argv if argv is None else argv)
    application = QApplication(arguments)
    application.setQuitOnLastWindowClosed(False)
    return application


def run_application(application: QApplication) -> int:
    """Run the Qt event loop and shut it down cleanly for the bootstrap smoke run."""
    QTimer.singleShot(0, application.quit)
    return application.exec()


def main(argv: Sequence[str] | None = None) -> int:
    """Start the minimal application bootstrap."""
    return run_application(create_application(argv))

