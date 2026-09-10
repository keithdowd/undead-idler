# Supported Windows Test Record

Date: 2026-09-10

| Windows version | Result | Notes |
| --- | --- | --- |
| Windows 11, build 26200 | Pass | The single executable launched, created the tray process, and remained running without a console window. |
| Windows 10 | Not available | No Windows 10 test machine or isolated environment is available in this workspace. |

## Issue Resolution

The first packaged build used a relative import in `__main__.py`. PyInstaller executes that entrypoint without a package parent, so launch failed with `attempted relative import with no known parent package`. The entrypoint now uses an absolute package import, and a rebuilt executable passed the Windows 11 launch check.

Windows 10 remains an external validation requirement before a release claim covering that platform is made.
