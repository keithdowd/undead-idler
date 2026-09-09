"""Low-level Windows keyboard input definitions for Undead Idler."""

from __future__ import annotations

import ctypes
from collections.abc import Sequence
from ctypes import wintypes

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


__all__ = [
    "HARDWAREINPUT",
    "INPUT",
    "INPUTUNION",
    "KEYBDINPUT",
    "KEYEVENTF_KEYUP",
    "MOUSEINPUT",
    "VK_F15",
    "send_input",
]

