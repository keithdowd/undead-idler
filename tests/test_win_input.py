import ctypes

from undead_idler.win_input import (
    INPUT,
    INPUT_KEYBOARD,
    KEYBDINPUT,
    KEYEVENTF_KEYUP,
    VK_F15,
    _SendInput,
)


def test_keyboard_input_definitions_are_configured():
    assert INPUT_KEYBOARD == 1
    assert KEYEVENTF_KEYUP == 0x0002
    assert VK_F15 == 0x7E
    assert ctypes.sizeof(INPUT) >= ctypes.sizeof(KEYBDINPUT)
    assert _SendInput.argtypes[0] is ctypes.c_uint
    assert _SendInput.restype is ctypes.c_uint

