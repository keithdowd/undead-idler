"""Windows session, power, and shutdown notifications."""

from __future__ import annotations

import ctypes
import os
from ctypes import wintypes

from PySide6.QtCore import QAbstractNativeEventFilter, QObject, Qt, Signal
from PySide6.QtWidgets import QApplication, QWidget


WM_QUERYENDSESSION = 0x0011
WM_ENDSESSION = 0x0016
WM_POWERBROADCAST = 0x0218
WM_WTSSESSION_CHANGE = 0x02B1

PBT_APMSUSPEND = 0x0004
WTS_SESSION_LOCK = 0x7
WTS_SESSION_UNLOCK = 0x8
NOTIFY_FOR_THIS_SESSION = 0


class _MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt_x", wintypes.LONG),
        ("pt_y", wintypes.LONG),
    ]


class WindowsLifecycleMonitor(QObject, QAbstractNativeEventFilter):
    """Translate relevant Windows messages into one stop signal."""

    stop_requested = Signal(str)

    def __init__(self, application: QObject, parent: QObject | None = None) -> None:
        QObject.__init__(self, parent)
        QAbstractNativeEventFilter.__init__(self)
        self._application = application
        self._window: QWidget | None = None
        self._registered = False
        self._filter_installed = False
        if (
            os.name == "nt"
            and QApplication.instance() is not None
            and hasattr(application, "installNativeEventFilter")
        ):
            self._install_windows_notifications()

    def _install_windows_notifications(self) -> None:
        """Install a hidden native window for current-session notifications."""
        self._window = QWidget()
        self._window.setAttribute(Qt.WidgetAttribute.WA_NativeWindow, True)
        self._window.hide()
        self._application.installNativeEventFilter(self)
        self._filter_installed = True

        wtsapi32 = ctypes.WinDLL("wtsapi32", use_last_error=True)
        register = wtsapi32.WTSRegisterSessionNotification
        register.argtypes = [wintypes.HWND, wintypes.DWORD]
        register.restype = wintypes.BOOL
        self._registered = bool(
            register(wintypes.HWND(int(self._window.winId())), NOTIFY_FOR_THIS_SESSION)
        )

    def nativeEventFilter(self, _event_type, message):
        """Handle a native message without consuming it."""
        try:
            message_pointer = int(message)
            native_message = ctypes.cast(
                message_pointer,
                ctypes.POINTER(_MSG),
            ).contents
        except (TypeError, ValueError, OSError):
            return False

        self.handle_message(native_message.message, native_message.wParam)
        return False

    def handle_message(self, message: int, wparam: int = 0) -> bool:
        """Process a message value; return whether it requests a stop."""
        reason = None
        if message in (WM_QUERYENDSESSION, WM_ENDSESSION):
            reason = "shutdown"
        elif message == WM_POWERBROADCAST and wparam == PBT_APMSUSPEND:
            reason = "suspend"
        elif message == WM_WTSSESSION_CHANGE and wparam == WTS_SESSION_LOCK:
            reason = "session lock"

        if reason is None:
            return False
        self.stop_requested.emit(reason)
        return True

    def close(self) -> None:
        """Unregister native notifications and remove the event filter."""
        if self._registered and self._window is not None:
            wtsapi32 = ctypes.WinDLL("wtsapi32", use_last_error=True)
            unregister = wtsapi32.WTSUnRegisterSessionNotification
            unregister.argtypes = [wintypes.HWND]
            unregister.restype = wintypes.BOOL
            unregister(wintypes.HWND(int(self._window.winId())))
            self._registered = False
        if self._filter_installed:
            self._application.removeNativeEventFilter(self)
            self._filter_installed = False
        if self._window is not None:
            self._window.close()
            self._window.deleteLater()
            self._window = None


__all__ = [
    "PBT_APMSUSPEND",
    "WM_ENDSESSION",
    "WM_POWERBROADCAST",
    "WM_QUERYENDSESSION",
    "WM_WTSSESSION_CHANGE",
    "WTS_SESSION_LOCK",
    "WindowsLifecycleMonitor",
]
