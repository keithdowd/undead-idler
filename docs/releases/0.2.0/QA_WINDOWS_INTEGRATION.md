# Windows Integration Test Record — 0.2.0

Date: 2026-09-11

## Environment

- OS reported by the Python runtime: `Windows-11-10.0.26200-SP0`
- Python: `3.13.6` from the project `.venv`
- PySide6: `6.11.0`
- PyInstaller: `6.21.0`
- Folder package: `dist/UndeadIdler/UndeadIdler.exe`
- Single-file package: `dist/UndeadIdler.exe`
- Archived artifact: `release/UndeadIdler-0.2.0.exe`

## Results

| Check | Result | Evidence or limitation |
| --- | --- | --- |
| Folder package build | Pass | PyInstaller completed successfully. |
| Folder package launch | Pass | Existing validator kept the process running and found the required runtime/icon files. |
| Single-file package build | Pass | PyInstaller completed successfully. |
| Single-file launch/no console | Pass | Process remained alive for five seconds; `MainWindowHandle = 0`. |
| Duplicate launch prevention | Pass | First folder process remained alive; second process exited with code 0. |
| F15 native injection | Pass | Unrestricted medium-integrity standard-user token submitted 2/2 events. |
| Scroll Lock native injection | Pass | Unrestricted medium-integrity standard-user token submitted 4/4 events. |
| Error and partial-input handling | Pass (automated) | Activity-controller and input-adapter tests cover initial/run/partial failures and cleanup. |
| Lock/suspend/shutdown mapping | Pass (automated) | Windows lifecycle event mapping and centralized Stop are covered by tests; interactive packaged event matrix remains unrun. |
| Settings key selection | Pass (automated) | Settings and runtime model tests cover F15/Scroll Lock and session-only behavior. |
| Status tooltip | Pass (automated) | Tray tests cover Status, interval, key, timestamp, warnings, and errors. |
| About/version | Pass (automated) | Tray/About tests cover approved copy, reusable dialog, and shared version `0.2.0`. |
| Native interactive UI review | Not run | Requires an interactive desktop session outside this restricted shell. |
| Initial launch tooltip | Pass | V020-013 initializes the complete stopped tooltip before showing the tray icon. |
| Interval helper-text placement | Fail | Manual review found the range text below Key; tracked as CHG-004. |

Native input passed in the available medium-integrity standard-user token. Interactive visual checks still require a desktop review before distribution sign-off.

