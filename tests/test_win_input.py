import ctypes

import pytest

import undead_idler.win_input as win_input
from undead_idler.win_input import (
    INPUT,
    INPUT_KEYBOARD,
    InputResult,
    KEYBDINPUT,
    KEYEVENTF_KEYUP,
    VK_F15,
    VK_SCROLL_LOCK,
    _SendInput,
)


def test_keyboard_input_definitions_are_configured():
    assert INPUT_KEYBOARD == 1
    assert KEYEVENTF_KEYUP == 0x0002
    assert VK_F15 == 0x7E
    assert ctypes.sizeof(INPUT) >= ctypes.sizeof(KEYBDINPUT)
    assert _SendInput.argtypes[0] is ctypes.c_uint
    assert _SendInput.restype is ctypes.c_uint


def test_f15_keypress_submits_key_down_then_key_up(monkeypatch):
    submitted = []

    def fake_send_input(events):
        submitted.extend(events)
        return len(events)

    monkeypatch.setattr(win_input, "send_input", fake_send_input)

    assert win_input.send_f15_keypress() is True
    assert len(submitted) == 2
    assert submitted[0].type == INPUT_KEYBOARD
    assert submitted[0].ki.wVk == VK_F15
    assert submitted[0].ki.dwFlags == 0
    assert submitted[1].type == INPUT_KEYBOARD
    assert submitted[1].ki.wVk == VK_F15
    assert submitted[1].ki.dwFlags == KEYEVENTF_KEYUP


def test_f15_keypress_rejects_partial_submission(monkeypatch):
    monkeypatch.setattr(win_input, "send_input", lambda events: len(events) - 1)

    assert win_input.send_f15_keypress() is False


def test_f15_keypress_result_contains_partial_submission_diagnostics(monkeypatch):
    monkeypatch.setattr(win_input, "send_input", lambda events: len(events) - 1)

    result = win_input.send_f15_keypress_with_result()

    assert isinstance(result, InputResult)
    assert result.success is False
    assert result.requested_events == 2
    assert result.submitted_events == 1
    assert result.error_message == "SendInput accepted 1 of 2 events."


def test_scroll_lock_sequence_submits_two_complete_presses(monkeypatch):
    submitted = []

    def fake_send_input(events):
        submitted.extend(events)
        return len(events)

    monkeypatch.setattr(win_input, "send_input", fake_send_input)

    result = win_input.send_keypress_with_result(win_input.SimulatedKey.SCROLL_LOCK)

    assert result.success is True
    assert len(submitted) == 4
    assert [event.ki.wVk for event in submitted] == [VK_SCROLL_LOCK] * 4
    assert [event.ki.dwFlags for event in submitted] == [0, KEYEVENTF_KEYUP, 0, KEYEVENTF_KEYUP]


@pytest.mark.parametrize("submitted_events", [1, 3])
def test_partial_scroll_lock_cleanup_releases_only_after_key_down(
    monkeypatch, submitted_events
):
    submitted = []

    def fake_send_input(events):
        submitted.extend(events)
        return len(events)

    monkeypatch.setattr(win_input, "send_input", fake_send_input)

    result = win_input.cleanup_partial_input(
        win_input.SimulatedKey.SCROLL_LOCK, submitted_events
    )

    assert result.success is True
    assert len(submitted) == 1
    assert submitted[0].ki.wVk == VK_SCROLL_LOCK
    assert submitted[0].ki.dwFlags == KEYEVENTF_KEYUP


def test_partial_f15_cleanup_releases_after_key_down(monkeypatch):
    submitted = []
    monkeypatch.setattr(win_input, "send_input", lambda events: submitted.extend(events) or len(events))

    result = win_input.cleanup_partial_input(win_input.SimulatedKey.F15, 1)

    assert result.success is True
    assert len(submitted) == 1
    assert submitted[0].ki.wVk == VK_F15
    assert submitted[0].ki.dwFlags == KEYEVENTF_KEYUP


def test_partial_scroll_lock_cleanup_does_not_send_speculative_event(monkeypatch):
    submitted = []
    monkeypatch.setattr(win_input, "send_input", lambda events: submitted.extend(events) or len(events))

    result = win_input.cleanup_partial_input(win_input.SimulatedKey.SCROLL_LOCK, 2)

    assert result.success is True
    assert result.requested_events == 0
    assert submitted == []


def test_input_result_contains_exception_diagnostics(monkeypatch):
    monkeypatch.setattr(
        win_input,
        "send_input",
        lambda events: (_ for _ in ()).throw(OSError("input blocked")),
    )

    result = win_input.send_input_with_result((INPUT(),))

    assert result.success is False
    assert result.requested_events == 1
    assert result.submitted_events == 0
    assert result.error_message == "input blocked"
