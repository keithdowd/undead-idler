# Undead Idler

Undead Idler is a Windows tray utility that generates periodic F15 or paired Scroll Lock keypresses while running to maintain local keyboard activity. It is intended to help applications such as Teams and Outlook observe recent computer input.

## Launch

For the packaged release, double-click:

```text
dist\UndeadIdler.exe
```

The application has no main window and starts in the `Stopped` state. It is not registered to launch with Windows. To run from source during development, activate the project virtual environment and run:

```powershell
.\.venv\Scripts\Activate.ps1
python -m undead_idler
```

Only one instance is allowed per Windows user session. A later launch exits without changing the existing instance.

## Tray Operations

Right-click the skull icon in the Windows system tray:

- `Start` sends the selected key sequence immediately and continues at the configured interval.
- `Stop` stops future keypresses without changing the interval or selected key.
- `Settings` changes the interval and selected key for the current session.
- `About` displays the application description and release version (`0.2.0`).
- `Exit` stops activity, removes the tray icon, and closes the application.

The icon uses gray eyes for stopped, green eyes for running, and red eyes for the error state.

## Interval, Key, and Tooltip

The default interval is 5 minutes on every launch. The setting accepts whole-minute values from 1 through 10 inclusive. Changes are runtime-only and are not persisted between sessions.

Settings offers two simulated-key choices:

- `F15` submits one key-down and one key-up event.
- `Scroll Lock` submits a paired sequence of key-down, key-up, key-down, and key-up events so the key ends in its original toggle state after a complete sequence.

The tray tooltip is available as soon as the tray icon appears and shows the current `Status`, `Interval`, selected `Key`, and the date/time of the last successful keypress. It shows `None` before a successful keypress has occurred. A failed initial keypress enters the error state immediately. During a running session, the first two consecutive failures remain visible as warnings and the third stops activity and enters the error state. A partial input sequence enters the error state immediately; for Scroll Lock, the tooltip also reports that the toggle state may be uncertain.

## Windows Session and Power Events

Locking Windows, suspending, hibernating, or shutting down stops activity. The application remains `Stopped` after unlock or resume and requires a new `Start` action; it does not replay missed intervals or start automatically.

## Smart Mode

Smart Mode is deferred from release 0.2.0 and is not available in this release.

## Limitations

- The application does not directly set or control Teams or Outlook presence.
- It does not reset native Windows idle detection.
- It does not prevent the computer from sleeping or lock behavior.
- It requires Windows and a manually launched process.
- The current release validation covers Windows 11. Windows 10 remains unverified for this release.
