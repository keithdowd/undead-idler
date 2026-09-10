"""Low-level Windows keyboard input definitions for Undead Idler."""

from __future__ import annotations

import ctypes
from collections.abc import Sequence
from ctypes import wintypes
from dataclasses import dataclass

if ctypes.sizeof(ctypes.c_void_p) == 8:
    ULONG_PTR = ctypes.c_uint64
else:
    ULONG_PTR = ctypes.c_uint32


INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

KEYEVENTF_KEYUP = 0x0002
VK_F15 = 0x7E


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class INPUTUNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]


class INPUT(ctypes.Structure):
    _anonymous_ = ("union",)
    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", INPUTUNION),
    ]


_SendInput = ctypes.WinDLL("user32", use_last_error=True).SendInput
_SendInput.argtypes = [
    wintypes.UINT,
    ctypes.POINTER(INPUT),
    ctypes.c_int,
]
_SendInput.restype = wintypes.UINT


@dataclass(frozen=True, slots=True)
class InputResult:
    """Outcome and local diagnostic details for an input submission."""

    success: bool
    requested_events: int
    submitted_events: int
    error_code: int | None = None
    error_message: str | None = None


def send_input(events: Sequence[INPUT]) -> int:
    """Submit a sequence of prepared Windows input events.

    The return value is the number of events accepted by Windows. Callers are
    responsible for interpreting a partial submission as a failure.
    """
    if not events:
        raise ValueError("at least one input event is required")

    input_array = (INPUT * len(events))(*events)
    return _SendInput(
        len(input_array),
        input_array,
        ctypes.sizeof(INPUT),
    )


def send_input_with_result(events: Sequence[INPUT]) -> InputResult:
    """Submit input and return a caller-friendly success or failure result."""
    requested_events = len(events)
    if not events:
        raise ValueError("at least one input event is required")

    try:
        submitted_events = send_input(events)
    except OSError as error:
        error_code = ctypes.get_last_error() or None
        return InputResult(
            success=False,
            requested_events=requested_events,
            submitted_events=0,
            error_code=error_code,
            error_message=str(error),
        )

    if submitted_events == requested_events:
        return InputResult(
            success=True,
            requested_events=requested_events,
            submitted_events=submitted_events,
        )

    error_code = ctypes.get_last_error() or None
    detail = (
        f"SendInput accepted {submitted_events} of "
        f"{requested_events} events."
    )
    if error_code is not None:
        detail += f" Windows error {error_code}: {ctypes.FormatError(error_code).strip()}"

    return InputResult(
        success=False,
        requested_events=requested_events,
        submitted_events=submitted_events,
        error_code=error_code,
        error_message=detail,
    )


def _build_f15_events() -> tuple[INPUT, INPUT]:
    """Build one F15 key-down and key-up sequence."""
    key_down = INPUT()
    key_down.type = INPUT_KEYBOARD
    key_down.ki = KEYBDINPUT(wVk=VK_F15)

    key_up = INPUT()
    key_up.type = INPUT_KEYBOARD
    key_up.ki = KEYBDINPUT(wVk=VK_F15, dwFlags=KEYEVENTF_KEYUP)

    return key_down, key_up


def send_f15_keypress_with_result() -> InputResult:
    """Submit F15 and return success plus local failure diagnostics."""
    return send_input_with_result(_build_f15_events())


def send_f15_keypress() -> bool:
    """Submit one complete F15 key-down and key-up sequence."""
    return send_f15_keypress_with_result().success


__all__ = [
    "HARDWAREINPUT",
    "INPUT",
    "INPUTUNION",
    "InputResult",
    "KEYBDINPUT",
    "KEYEVENTF_KEYUP",
    "MOUSEINPUT",
    "VK_F15",
    "send_f15_keypress",
    "send_f15_keypress_with_result",
    "send_input",
    "send_input_with_result",
]
