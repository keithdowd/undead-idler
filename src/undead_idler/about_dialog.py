"""About dialog for Undead Idler."""

from __future__ import annotations

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout

from . import __version__


ABOUT_DESCRIPTION = (
    "A Windows tray utility that generates periodic F15 or paired Scroll Lock "
    "keypresses while running to maintain local keyboard activity. Start and "
    "stop activity manually, and configure the interval in Settings.\n\n"
    "Undead Idler does not directly control application presence or prevent "
    "your computer from sleeping."
)


class AboutDialog(QDialog):
    """Display product identity, release version, and approved description."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("About Undead Idler")
        self.setModal(False)

        title = QLabel("Undead Idler", self)
        title.setObjectName("about_title")
        version = QLabel(f"Version {__version__}", self)
        version.setObjectName("about_version")
        description = QLabel(ABOUT_DESCRIPTION, self)
        description.setObjectName("about_description")
        description.setWordWrap(True)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, parent=self)
        buttons.setObjectName("about_buttons")
        buttons.accepted.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(version)
        layout.addWidget(description)
        layout.addWidget(buttons)


__all__ = ["ABOUT_DESCRIPTION", "AboutDialog"]
