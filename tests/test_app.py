from PySide6.QtWidgets import QApplication

from undead_idler.app import create_application, main


def test_application_event_loop_exits_cleanly(monkeypatch):
    monkeypatch.setattr(QApplication, "exec", lambda self: 0)
    assert main([]) == 0


def test_application_bootstrap_uses_no_persistent_window():
    application = QApplication.instance() or create_application([])

    assert application.quitOnLastWindowClosed() is False
