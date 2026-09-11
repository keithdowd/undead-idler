"""Single-instance protection for the Windows tray application."""

from __future__ import annotations

import ctypes
import getpass
import hashlib
import os
from ctypes import wintypes


ERROR_ALREADY_EXISTS = 183
_DEFAULT_PREFIX = "Local\\UndeadIdler-"


def _running_on_windows() -> bool:
    """Return whether the current runtime provides the Windows mutex API."""
    return os.name == "nt"


def default_mutex_name() -> str:
    """Build a stable per-user name in the current Windows session namespace."""
    username = getpass.getuser() or "unknown-user"
    user_token = hashlib.sha256(username.encode("utf-8")).hexdigest()[:16]
    return f"{_DEFAULT_PREFIX}{user_token}"


class InstanceGuard:
    """Own the named mutex handle for the lifetime of one application."""

    def __init__(self, handle, close_handle=None) -> None:
        self._handle = handle
        self._close_handle = close_handle

    @property
    def acquired(self) -> bool:
        """Return whether this guard owns a native mutex handle."""
        return self._handle is not None

    def release(self) -> None:
        """Release the native handle once; safe to call repeatedly."""
        if self._handle is None:
            return
        handle = self._handle
        self._handle = None
        if self._close_handle is not None:
            self._close_handle(handle)


def acquire_instance(name: str | None = None) -> InstanceGuard | None:
    """Acquire the process guard, returning None for a duplicate launch.

    Non-Windows environments return a no-op guard so application-level tests can
    exercise bootstrap behavior without emulating the Windows API.
    """
    if not _running_on_windows():
        return InstanceGuard(None)

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    create_mutex = kernel32.CreateMutexW
    create_mutex.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
    create_mutex.restype = wintypes.HANDLE
    close_handle = kernel32.CloseHandle
    close_handle.argtypes = [wintypes.HANDLE]
    close_handle.restype = wintypes.BOOL

    mutex_handle = create_mutex(None, False, name or default_mutex_name())
    if not mutex_handle:
        error_code = ctypes.get_last_error() or 1
        raise OSError(error_code, "CreateMutexW failed")

    if ctypes.get_last_error() == ERROR_ALREADY_EXISTS:
        close_handle(mutex_handle)
        return None

    return InstanceGuard(mutex_handle, close_handle)


__all__ = ["ERROR_ALREADY_EXISTS", "InstanceGuard", "acquire_instance", "default_mutex_name"]
