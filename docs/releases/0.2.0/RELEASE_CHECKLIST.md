# Undead Idler 0.2.0 Release Checklist

Release candidate: `0.2.0`
Date: 2026-09-11
Verification platform: Windows 11 build 26200, project `.venv`, standard desktop shell restrictions noted below.

## Build and artifact checks

- [x] Folder-based PyInstaller build completed with Python 3.13.6, PySide6 6.11.0, and PyInstaller 6.21.0.
- [x] Folder package contains `UndeadIdler.exe`, Python runtime DLL, and all three tray icon resources.
- [x] Folder package launches and remains running during the validator check.
- [x] Single-file PyInstaller build completed.
- [x] Single-file package launches without a console window (`MainWindowHandle = 0`) and remains running for five seconds.
- [x] Release artifact is archived at `release/UndeadIdler-0.2.0.exe`.
- [x] Matching SHA-256 and build metadata are recorded in `release/BUILD_METADATA-0.2.0.md`.

## Automated and packaged behavior

- [x] Full automated suite passes: 110 tests.
- [x] Duplicate folder-package launch exits with code 0 while the original process remains running.
- [x] Error handling, partial-input cleanup, lifecycle mapping, settings, tooltip, About, and version consistency are covered by automated tests.
- [x] No startup registration, network service, account requirement, telemetry, or power-setting changes are present in the implementation.
- [x] Native F15 and Scroll Lock injection passes in an unrestricted medium-integrity standard-user Windows token (2/2 and 4/4 events).
- [ ] Packaged visual checks of the Settings, About, and tooltip surfaces: not run through an interactive desktop session in this environment.

## Release limitations

- Windows 11 is the only platform targeted for this release; Windows 10 remains unverified.
- Smart Mode is deferred and is not included in 0.2.0.
- Interactive visual checks of Settings, About, and the tooltip remain outstanding before final distribution sign-off.

