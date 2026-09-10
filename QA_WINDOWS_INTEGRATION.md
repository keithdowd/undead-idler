# Windows Integration Test Record

Date: 2026-09-10

## Environment

- OS: Windows 11 (`10.0.26200`)
- Runtime used for direct adapter check: project `.venv`, Python 3.13.6
- Tested executable: `dist/UndeadIdler.exe`
- Executable SHA-256: recorded during `QA-005`

## Results

| Check | Result | Evidence |
| --- | --- | --- |
| Direct F15 injection | Pass | `SendInput` submitted 2 of 2 events with elevated Windows execution. |
| Packaged launch | Pass | Executable remained running for five seconds. |
| No console window | Pass | Packaged process reported `MainWindowHandle = 0`. |
| Tray Start, Stop, Settings, and Exit | Pass | Covered by automated tray-controller tests and owner manual confirmation. |
| Three-failure automatic stop | Pass | Covered by automated activity-controller tests. |
| Power settings unchanged | Pass | `powercfg /getactivescheme` matched before and after launch. |
| Startup registration | Pass | No startup registration code or task is present; application is manually launched. |
| Network service or account requirement | Pass | No network, login, or service integration is present. |
| Teams/Outlook presence observation | Pass | Owner manual validation confirmed the intended F15-based behavior. |

The application only submits F15 input and does not directly control presence state.
