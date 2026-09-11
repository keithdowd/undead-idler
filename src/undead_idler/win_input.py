"""Low-level Windows keyboard input definitions for Undead Idler."""

from __future__ import annotations

import ctypes
from collections.abc import Sequence
from ctypes import wintypes
from dataclasses import dataclass

from .models import SimulatedKey

if ctypes.sizeof(ctypes.c_void_p) == 8:
    ULONG_PTR = ctypes.c_uint64
else:
    ULONG_PTR = ctypes.c_uint32


INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

KEYEVENTF_KEYUP = 0x0002
VK_F15 = 0x7E
VK_SCROLL_LOCK = 0x91


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
        ctypes.set_last_error(0)
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


def _build_key_events(virtual_key: int, presses: int = 1) -> tuple[INPUT, ...]:
    """Build complete down/up events for one or more consecutive presses."""
    events = []
    for _ in range(presses):
        key_down = INPUT()
        key_down.type = INPUT_KEYBOARD
        key_down.ki = KEYBDINPUT(wVk=virtual_key)
        key_up = INPUT()
        key_up.type = INPUT_KEYBOARD
        key_up.ki = KEYBDINPUT(wVk=virtual_key, dwFlags=KEYEVENTF_KEYUP)
        events.extend((key_down, key_up))
    return tuple(events)


def _build_f15_events() -> tuple[INPUT, INPUT]:
    """Build one F15 key-down and key-up sequence."""
    return _build_key_events(VK_F15)


def _build_scroll_lock_events() -> tuple[INPUT, ...]:
    """Build two complete Scroll Lock presses."""
    return _build_key_events(VK_SCROLL_LOCK, presses=2)


def build_key_events(key: SimulatedKey) -> tuple[INPUT, ...]:
    """Build the complete event batch for a selected simulated key."""
    if key is SimulatedKey.F15:
        return _build_f15_events()
    if key is SimulatedKey.SCROLL_LOCK:
        return _build_scroll_lock_events()
    raise ValueError("unsupported simulated key")


def _build_key_up_event(virtual_key: int) -> INPUT:
    """Build one key-up event for bounded partial-sequence cleanup."""
    key_up = INPUT()
    key_up.type = INPUT_KEYBOARD
    key_up.ki = KEYBDINPUT(wVk=virtual_key, dwFlags=KEYEVENTF_KEYUP)
    return key_up


def cleanup_partial_input(key: SimulatedKey, submitted_events: int) -> InputResult:
    """Release a simulated key only when a partial batch ended key-down.

    Even submitted counts end after key-up, so no speculative event is sent.
    The returned result describes cleanup only; it is never activity success.
    """
    if submitted_events <= 0 or submitted_events % 2 == 0:
        return InputResult(success=True, requested_events=0, submitted_events=0)
    virtual_key = VK_F15 if key is SimulatedKey.F15 else VK_SCROLL_LOCK
    return send_input_with_result((_build_key_up_event(virtual_key),))


def send_keypress_with_result(key: SimulatedKey) -> InputResult:
    """Submit one complete activity sequence for the selected key."""
    return send_input_with_result(build_key_events(key))


def send_f15_keypress_with_result() -> InputResult:
    """Submit F15 and return success plus local failure diagnostics."""
    return send_keypress_with_result(SimulatedKey.F15)


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
    "VK_SCROLL_LOCK",
    "build_key_events",
    "cleanup_partial_input",
    "send_keypress_with_result",
    "send_f15_keypress",
    "send_f15_keypress_with_result",
    "send_input",
    "send_input_with_result",
]
