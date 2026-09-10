# Undead Idler Implementation Tasks

This checklist converts `TECHNICAL_REQUIREMENTS.md` into ordered implementation work. Tasks should be completed in dependency order unless a task is explicitly marked independent.

Status values:

- `[ ]` Not started
- `[-]` In progress
- `[x]` Complete

## Phase 1: Project Foundation

### UI-001 Create Python project metadata

- Status: `[x]`
- Dependencies: None
- Define the project in `pyproject.toml`.
- Declare Python compatibility as `>=3.11`.
- Add the selected PySide6 6.11.x dependency.
- Define development commands for running the application and tests.

Completion criteria: the project can be installed in a clean Windows virtual environment.

### UI-002 Create source and test layout

- Status: `[x]`
- Dependencies: UI-001
- Create the `src/undead_idler` package.
- Create the initial `tests` package.
- Add package entry points for module execution.

Completion criteria: the package imports successfully and the test runner discovers the test directory.

### UI-003 Create minimal Qt application

- Status: `[x]`
- Dependencies: UI-002
- Create a minimal `QApplication` startup path.
- Start and stop the Qt event loop cleanly.
- Ensure the application does not create a persistent main window.

Completion criteria: a development command launches the application and exits without an exception.

## Phase 2: Windows Input Adapter

### WIN-001 Define SendInput ctypes structures

- Status: `[x]`
- Dependencies: UI-002
- Define the Windows structures required by `user32.SendInput`.
- Define keyboard input constants and the F15 virtual-key code.
- Set ctypes argument and return types explicitly.

Completion criteria: the adapter module imports on Windows and exposes a typed input operation without UI dependencies.

### WIN-002 Implement complete F15 keypress

- Status: `[x]`
- Dependencies: WIN-001
- Submit one F15 key-down event.
- Submit one F15 key-up event.
- Treat incomplete submission as failure.
- Ensure the key is never held between calls.

Completion criteria: the adapter returns success only when the complete keypress is submitted.

### WIN-003 Add input adapter diagnostics

- Status: `[x]`
- Dependencies: WIN-002
- Capture useful local diagnostic information when `SendInput` fails.
- Do not send diagnostics over the network.
- Keep diagnostic details available to the activity controller without coupling it to Windows error formatting.

Completion criteria: callers can distinguish success from failure and receive a useful local failure description.

### WIN-004 Manually validate F15 injection

- Status: `[x]`
- Dependencies: WIN-002
- Run the adapter in a supported Windows desktop session.
- Confirm F15 key-down and key-up events are submitted.
- Observe behavior with a test application that can display or record F15 input.

Completion criteria: F15 injection works in the development environment without requiring administrator privileges.

Validation record:

- The adapter returned `success=True` with 2 of 2 events submitted.
- A temporary Windows F15 hotkey listener received `WM_HOTKEY`.
- Windows' last-input timestamp changed after the keypress.
- The successful validation ran with `is_admin=False`.

## Phase 3: Activity Controller

### ACT-001 Define application states

- Status: `[x]`
- Dependencies: UI-002
- Implement explicit `Stopped`, `Running`, and `Error` states.
- Define state-change notifications for the tray controller.
- Ensure state transitions cannot create duplicate activity loops.

Completion criteria: state transitions are represented independently from the tray UI.

### ACT-002 Implement runtime interval model

- Status: `[x]`
- Dependencies: UI-002
- Initialize the interval to 5 minutes on every launch.
- Accept only whole-minute values from 1 through 10.
- Keep the value in memory only.
- Do not write interval data to disk or the registry.

Completion criteria: interval behavior can be tested without starting the Qt tray UI and resets to 5 minutes for a new controller instance.

### ACT-003 Implement immediate Start behavior

- Status: `[x]`
- Dependencies: WIN-002, ACT-001, ACT-002
- Reset the consecutive-failure counter.
- Submit one F15 keypress immediately.
- Record the local timestamp only after success.
- Transition to `Running` only after the initial keypress succeeds.

Completion criteria: Start never waits for the first interval before attempting input.

### ACT-004 Implement repeating QTimer behavior

- Status: `[x]`
- Dependencies: ACT-003
- Start a QTimer after a successful initial keypress.
- Convert the whole-minute interval to milliseconds.
- Submit one keypress per timeout.
- Prevent overlapping timers and duplicate loops.

Completion criteria: a running controller produces one keypress per configured interval.

### ACT-005 Implement success timestamp tracking

- Status: `[x]`
- Dependencies: ACT-003, ACT-004
- Store the last successful keypress timestamp for the current session.
- Use local system time.
- Use the format `YYYY-MM-DD HH:mm:ss` when formatted for display.
- Leave the timestamp unchanged after a failed keypress.

Completion criteria: the timestamp reflects the last successful complete keypress only.

### ACT-006 Implement failure handling

- Status: `[x]`
- Dependencies: ACT-003, ACT-004, WIN-003
- Increment the consecutive-failure counter after each failed keypress.
- Reset the counter after any successful keypress.
- Stop the timer after 3 consecutive failures.
- Transition to `Error` and expose the failure description.
- Allow a later Start action to retry.

Completion criteria: three consecutive failures stop activity and produce an observable error state.

### ACT-007 Implement Stop and cleanup behavior

- Status: `[x]`
- Dependencies: ACT-004, ACT-006
- Stop the timer immediately.
- Reset the consecutive-failure counter.
- Transition to `Stopped` when Stop is selected.
- Preserve the last successful timestamp for the current session.
- Ensure shutdown does not leave a pending active timer.

Completion criteria: Stop prevents all future keypresses and leaves the controller in a clean state.

### ACT-008 Implement runtime interval changes

- Status: `[x]`
- Dependencies: ACT-004, ACT-002
- Apply a valid saved interval to future timer events.
- If running, stop and restart the timer.
- Do not send an extra keypress when the setting changes.
- Schedule the next keypress one full new interval after the change.

Completion criteria: interval changes take effect during the current session and are not persisted between launches.

## Phase 4: Settings Dialog

### SET-001 Build interval settings dialog

- Status: `[x]`
- Dependencies: UI-003, ACT-002
- Add a whole-number interval input.
- Display the allowed range of 1 through 10 minutes.
- Add `Save` and `Cancel` actions.
- Initialize the input from the current runtime interval.

Completion criteria: the dialog opens with the current interval and contains no unrelated settings.

### SET-002 Add interval validation

- Status: `[x]`
- Dependencies: SET-001
- Reject empty values.
- Reject non-numeric values.
- Reject fractional values.
- Reject values below 1 or above 10.
- Keep the prior interval when validation fails.

Completion criteria: only valid whole-minute values can be saved.

### SET-003 Connect settings to activity controller

- Status: `[x]`
- Dependencies: SET-002, ACT-008
- Apply valid changes to the activity controller.
- Refresh the tray tooltip after saving.
- Leave running state unchanged when the dialog is canceled.

Completion criteria: valid changes affect the active session and cancel leaves all runtime behavior unchanged.

## Phase 5: Tray Interface and Icon

### TRAY-001 Create custom icon assets

- Status: `[x]`
- Dependencies: None
- Create a custom Undead Idler ICO asset.
- Include standard Windows application and tray sizes.
- Use a compact undead/skull visual with a dark neutral base.
- Provide gray stopped, green running, and red error treatments.
- Verify legibility at small tray sizes.

Completion criteria: the icon assets are available in the repository in a format suitable for PySide6 and PyInstaller.

### TRAY-002 Implement tray icon controller

- Status: `[x]`
- Dependencies: UI-003, TRAY-001, ACT-001
- Create the `QSystemTrayIcon`.
- Load icon resources without absolute development-machine paths.
- Set the initial stopped icon.
- Update the icon for running and error states.

Completion criteria: the application displays the correct custom icon for each state.

### TRAY-003 Implement tray menu actions

- Status: `[x]`
- Dependencies: TRAY-002, ACT-003, ACT-007, SET-003
- Add `Start`, `Stop`, `Settings`, and `Exit` actions.
- Enable and disable actions according to application state.
- Make Start idempotent.
- Make Stop safe when already stopped.

Completion criteria: all required operations are available from the tray and invoke the correct controller behavior.

### TRAY-004 Implement tooltip formatting

- Status: `[ ]`
- Dependencies: TRAY-002, ACT-005, ACT-006, SET-003
- Show current state.
- Show current interval.
- Show the last successful keypress timestamp.
- Show `None` when no successful keypress has occurred.
- Show the 3-failure automatic-stop message in the error state.
- Refresh after state, interval, timestamp, and error changes.

Completion criteria: tooltip content matches the technical requirements for stopped, running, and error states.

### TRAY-005 Implement clean Exit

- Status: `[ ]`
- Dependencies: TRAY-003, ACT-007
- Stop activity before closing.
- Remove the tray icon.
- Quit the Qt event loop cleanly.
- Ensure the application starts stopped on its next launch.

Completion criteria: Exit closes the application without leaving active timers or a visible tray icon.

## Phase 6: Packaging

### PKG-001 Configure PyInstaller build

- Status: `[ ]`
- Dependencies: UI-003, TRAY-002
- Add a windowed/no-console PyInstaller configuration.
- Include Python, PySide6, Qt platform plugins, Python modules, and icon resources.
- Set the custom application icon.
- Build on Windows.

Completion criteria: a folder-based package is produced and launches on the development machine.

### PKG-002 Validate folder-based build

- Status: `[ ]`
- Dependencies: PKG-001, TRAY-005
- Launch the packaged application without Python installed on the test machine if possible.
- Verify tray creation, menu actions, F15 input, settings, timestamps, and shutdown.
- Resolve missing Qt plugins or resources.

Completion criteria: the folder-based package passes the core end-to-end workflow.

### PKG-003 Produce single executable

- Status: `[ ]`
- Dependencies: PKG-002
- Configure the PyInstaller single-file build.
- Include the custom icon and required Qt resources.
- Ensure no console window appears.

Completion criteria: a single Windows executable launches and operates without a separate Python installation.

## Phase 7: Verification and Release Readiness

### QA-001 Complete automated test suite

- Status: `[ ]`
- Dependencies: ACT-002, ACT-003, ACT-005, ACT-006, ACT-007, ACT-008, SET-002, TRAY-004
- Run unit tests for interval validation, state transitions, timer behavior, failure handling, timestamps, and tooltip formatting.
- Confirm tests do not require real F15 injection.

Completion criteria: automated tests pass consistently in the development environment.

### QA-002 Perform Windows integration testing

- Status: `[ ]`
- Dependencies: PKG-002
- Verify immediate and repeated F15 keypresses.
- Verify Start, Stop, Settings, and Exit behavior.
- Verify three-failure automatic stop.
- Observe intended behavior with Teams and Outlook.
- Verify the application does not alter power settings or create startup entries.

Completion criteria: the packaged application satisfies the observable PRD acceptance criteria on Windows.

### QA-003 Test supported Windows versions

- Status: `[ ]`
- Dependencies: PKG-003, QA-002
- Test on Windows 10 where available.
- Test on Windows 11.
- Record platform-specific issues and resolutions.

Completion criteria: the single executable launches and passes the core workflow on each available supported Windows version.

### QA-004 Write user documentation

- Status: `[ ]`
- Dependencies: QA-002
- Document manual launch.
- Document Start, Stop, Settings, and Exit.
- Document the 1-10 minute interval range and 5-minute launch default.
- Document the F15 behavior and last-keypress tooltip.
- Document known limitations, including no direct Teams/Outlook presence control and no sleep prevention.

Completion criteria: a user can operate the packaged MVP using the repository documentation.

### QA-005 Release checklist

- Status: `[ ]`
- Dependencies: QA-001, QA-003, QA-004
- Confirm all PRD acceptance criteria are satisfied.
- Confirm the executable starts stopped.
- Confirm interval settings are not persisted.
- Confirm no startup registration, scheduled task, network service, or account requirement exists.
- Archive the tested single executable and build metadata.

Completion criteria: the MVP is ready for distribution as a single Windows executable.

## Dependency Summary

The recommended critical path is:

```text
Project foundation
  -> Windows input adapter
      -> Activity controller
          -> Settings dialog
          -> Tray interface
              -> Packaging
                  -> Integration testing
                      -> Release checklist
```

The custom icon task can proceed in parallel with the input adapter and activity controller, but it must be complete before final packaging.
