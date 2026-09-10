from PySide6.QtWidgets import QApplication

from undead_idler.activity_controller import ActivityController
from undead_idler.win_input import InputResult


def test_controller_acceptance_smoke_does_not_require_native_injection(monkeypatch):
    """The automated acceptance path must remain independent of Windows input."""
    import undead_idler.win_input as win_input

    monkeypatch.setattr(
        win_input,
        "_SendInput",
        lambda *args: (_ for _ in ()).throw(AssertionError("native input called")),
    )
    controller = ActivityController(
        input_sender=lambda: InputResult(True, 2, 2),
    )

    assert controller.start() is True
    assert controller.last_successful_keypress is not None


def test_qt_acceptance_tests_have_a_single_application_context():
    assert QApplication.instance() is None or isinstance(
        QApplication.instance(), QApplication
    )
