# Undead Idler

Undead Idler is a Windows tray utility that sends an F15 keypress at a runtime-configured interval while manually enabled. It is intended to help applications such as Teams and Outlook observe recent computer input.

## Launch

For the packaged MVP, double-click:

```text
dist\UndeadIdler.exe
```

The application has no main window and starts in the `Stopped` state. It is not registered to launch with Windows. To run from source during development, activate the project virtual environment and run:

```powershell
.\.venv\Scripts\Activate.ps1
python -m undead_idler
```

## Tray Operations

Right-click the skull icon in the Windows system tray:

- `Start` sends one F15 keypress immediately and continues at the configured interval.
- `Stop` stops future keypresses without changing the interval.
- `Settings` changes the interval for the current session.
- `Exit` stops activity, removes the tray icon, and closes the application.

The icon uses gray eyes for stopped, green eyes for running, and red eyes for the error state.

## Interval and Tooltip

The default interval is 5 minutes on every launch. The setting accepts whole-minute values from 1 through 10 inclusive. Changes are runtime-only and are not persisted between sessions.

The tray tooltip shows the current state, interval, and the date/time of the last successful keypress. It shows `None` before a successful keypress has occurred. Three consecutive failed keypresses stop the activity loop and show an error message.

## F15 Behavior

When enabled, the application submits a press and release of the F15 virtual key through the Windows `SendInput` API. It does not use PowerShell or a separate worker process.

## Limitations

- The application does not directly set or control Teams or Outlook presence.
- It does not reset native Windows idle detection.
- It does not prevent the computer from sleeping or lock behavior.
- It requires Windows and a manually launched process.
- The current release validation covers Windows 11. Windows 10 requires a separate test machine before making a release claim for that platform.
