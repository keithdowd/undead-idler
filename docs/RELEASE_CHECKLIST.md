# Undead Idler MVP Release Checklist

Release candidate: `0.1.0`
Date: 2026-09-10

## Acceptance Criteria

- [x] Manual launch displays a tray icon.
- [x] Application starts in the `Stopped` state.
- [x] Start submits an immediate F15 keypress.
- [x] Repeated keypress timing is controlled by the configured whole-minute interval.
- [x] Stop prevents future keypresses.
- [x] Settings accepts whole-minute values from 1 through 10 and rejects fractional values.
- [x] Interval changes are runtime-only and reset to 5 minutes on a new launch.
- [x] Tooltip shows state, interval, and the last successful keypress time.
- [x] Exit stops activity, removes the tray icon, and closes the application.

## Release Checks

- [x] Single executable is archived at `release/UndeadIdler-0.1.0.exe`.
- [x] Executable starts without a separate Python installation.
- [x] Executable uses a windowed/no-console build.
- [x] No startup registration or scheduled task is created.
- [x] No network service, login, or account is required.
- [x] No power settings are modified.
- [x] Full automated suite passes.
- [x] Windows 11 launch and F15 integration checks pass.
- [x] Windows 10 launch and core workflow pass.
- [x] Teams/Outlook presence behavior was manually observed and passed.

The application does not directly control presence state or prevent sleep.
