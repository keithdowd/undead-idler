# Undead Idler Implementation Tasks

This checklist converts `docs/TECHNICAL_REQUIREMENTS.md` into ordered implementation work. Tasks should be completed in dependency order unless a task is explicitly marked independent.

Status values:

- `[ ]` Not started
- `[-]` In progress
- `[x]` Complete

Release scope: Phases 1-7 and their dependency summary below are the preserved 0.1.0 MVP record. New work is in [Release 0.2.0](#release-020-planned-implementation), based on [PRD section 12](PRD.md#12-planned-020-requirements), [technical section 12](TECHNICAL_REQUIREMENTS.md#12-planned-020-design), and the [release plan](releases/0.2.0/RELEASE_PLAN.md). Completed MVP tasks do not imply the planned release has been implemented or tested.

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

- Status: `[x]`
- Dependencies: TRAY-002, ACT-005, ACT-006, SET-003
- Show current state.
- Show current interval.
- Show the last successful keypress timestamp.
- Show `None` when no successful keypress has occurred.
- Show the 3-failure automatic-stop message in the error state.
- Refresh after state, interval, timestamp, and error changes.

Completion criteria: tooltip content matches the technical requirements for stopped, running, and error states.

### TRAY-005 Implement clean Exit

- Status: `[x]`
- Dependencies: TRAY-003, ACT-007
- Stop activity before closing.
- Remove the tray icon.
- Quit the Qt event loop cleanly.
- Ensure the application starts stopped on its next launch.

Completion criteria: Exit closes the application without leaving active timers or a visible tray icon.

## Phase 6: Packaging

### PKG-001 Configure PyInstaller build

- Status: `[x]`
- Dependencies: UI-003, TRAY-002
- Add a windowed/no-console PyInstaller configuration.
- Include Python, PySide6, Qt platform plugins, Python modules, and icon resources.
- Set the custom application icon.
- Build on Windows.

Completion criteria: a folder-based package is produced and launches on the development machine.

### PKG-002 Validate folder-based build

- Status: `[x]`
- Dependencies: PKG-001, TRAY-005
- Launch the packaged application without Python installed on the test machine if possible.
- Verify tray creation, menu actions, F15 input, settings, timestamps, and shutdown.
- Resolve missing Qt plugins or resources.

Completion criteria: the folder-based package passes the core end-to-end workflow.

### PKG-003 Produce single executable

- Status: `[x]`
- Dependencies: PKG-002
- Configure the PyInstaller single-file build.
- Include the custom icon and required Qt resources.
- Ensure no console window appears.

Completion criteria: a single Windows executable launches and operates without a separate Python installation.

## Phase 7: Verification and Release Readiness

### QA-001 Complete automated test suite

- Status: `[x]`
- Dependencies: ACT-002, ACT-003, ACT-005, ACT-006, ACT-007, ACT-008, SET-002, TRAY-004
- Run unit tests for interval validation, state transitions, timer behavior, failure handling, timestamps, and tooltip formatting.
- Confirm tests do not require real F15 injection.

Completion criteria: automated tests pass consistently in the development environment.

### QA-002 Perform Windows integration testing

- Status: `[x]`
- Dependencies: PKG-002
- Verify immediate and repeated F15 keypresses.
- Verify Start, Stop, Settings, and Exit behavior.
- Verify three-failure automatic stop.
- Observe intended behavior with Teams and Outlook.
- Verify the application does not alter power settings or create startup entries.

Completion criteria: the packaged application satisfies the observable PRD acceptance criteria on Windows.

### QA-003 Test supported Windows versions

- Status: `[x]`
- Dependencies: PKG-003, QA-002
- Test on Windows 10 where available.
- Test on Windows 11.
- Record platform-specific issues and resolutions.

Completion criteria: the single executable launches and passes the core workflow on each available supported Windows version.

### QA-004 Write user documentation

- Status: `[x]`
- Dependencies: QA-002
- Document manual launch.
- Document Start, Stop, Settings, and Exit.
- Document the 1-10 minute interval range and 5-minute launch default.
- Document the F15 behavior and last-keypress tooltip.
- Document known limitations, including no direct Teams/Outlook presence control and no sleep prevention.

Completion criteria: a user can operate the packaged MVP using the repository documentation.

### QA-005 Release checklist

- Status: `[x]`
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

## Release 0.2.0: Planned implementation

Tasks below are completed, in progress, or not started. Dependencies reference new tasks; the completed MVP is the baseline. Scope IDs refer to [RELEASE_PLAN.md](releases/0.2.0/RELEASE_PLAN.md). Follow the existing per-task implementation/commit workflow.

### V020-001 Prevent duplicate instances

- Status: `[x]`
- Dependencies: None (MVP baseline).
- Scope: BUG-001; PRD 12.2; technical 12.2.
- Add an atomic per-user/session instance guard before UI or input initialization; release resources at exit.
- Silently reject duplicates without changing the original instance.
- Validate sequential and simultaneous launch, original status/interval preservation, clean exit, and crash/relaunch behavior.

Completion criteria: exactly one tray/input owner exists per session; later legitimate launches are not blocked by stale state. Packaged validation also runs in V020-012.

Implementation record: the application acquires a per-user/session Windows named mutex before creating QApplication or tray UI. Duplicate launches return cleanly, and the native handle is released idempotently during shutdown. Unit coverage verifies duplicate rejection, handle cleanup, no-op non-Windows behavior, and bootstrap short-circuiting. Full suite result: 85 passed with the project source path configured.

### V020-002 Implement explicit error policy and warnings

- Status: `[x]`
- Dependencies: V020-001.
- Scope: BUG-003; PRD 12.8; technical 12.4.
- Support Stopped -> Error on initial failure and normal-mode retry from Error.
- Define full/zero/partial result handling, centralized Error cleanup, warnings for Running failures 1/2, and automatic Error at 3.
- Keep the timestamp unchanged on failure and reset counts only on success, explicit Stop, or a fresh Start.
- Test initial failure/retry, successful reset, all thresholds, timestamp preservation, and truthful tooltip reasons with mocked results. Native partial cleanup follows in V020-004.

Completion criteria: errors are visible at every stage; no retry timer survives Error, and no message incorrectly claims three failures for another cause.

Implementation record: failed Start transitions from Stopped to Error with the timer inactive. Running failures one and two remain Running with visible warning details; the third transitions to Error. Successful input clears the failure count and warning, and retrying from Error starts in normal mode. Focused controller/tray tests and the full suite pass (89 tests). Partial-submission cleanup remains assigned to V020-004.

### V020-003 Add key selection and complete sequences

- Status: `[x]`
- Dependencies: V020-002.
- Scope: FEAT-001; PRD 12.5; technical 12.3/12.6.
- Add a session-only F15/Scroll Lock enum with F15 launch default; extend Settings without adding Smart Mode.
- Submit one tagged batch of 2 F15 events or 4 Scroll Lock events for Start and timer events.
- Validate/apply Settings atomically; preserve scheduling for key-only/unchanged Save, reset for interval changes, and preserve values on Cancel/invalid input.
- Test event order/count/marker, defaults, invalid selections, settings transactions, and normal-mode scheduling.

Completion criteria: both keys are selectable and full success requires the complete batch; no persistence or extra keypress results from saving settings.

Implementation record: RuntimeSettings now holds a session-only F15/Scroll Lock selection with F15 as the launch default. Settings saves interval and key atomically; key-only changes preserve timer scheduling and interval changes restart it. F15 submits down/up and Scroll Lock submits down/up/down/up. Focused settings/input tests and the full suite pass (96 tests). Partial-submission cleanup remains assigned to V020-004.

### V020-004 Validate and implement partial-input cleanup

- Status: `[x]`
- Dependencies: V020-003.
- Scope: BUG-003, FEAT-001; PRD 12.8; technical 12.3; TECH-002.
- Validate what partial return counts establish and design bounded best-effort release of a potentially held simulated key.
- Never blindly replay or toggle; report immediate Error and Scroll Lock state uncertainty when applicable.
- Test every partial count for both keys, cleanup failure, no success timestamp/count reset, and no retry loop. Record controlled native validation limits.

Completion criteria: TECH-002 is resolved in technical requirements; partial submission is distinct from zero-event failure and cannot silently leave activity running.

Implementation record: partial results now enter Error immediately. Odd accepted counts receive one bounded key-up cleanup; even accepted counts receive no speculative event. Scroll Lock failures explain the uncertain toggle state, cleanup failures remain visible, and neither cleanup nor partial submission updates the success timestamp. Focused input/controller tests and the full suite pass (101 tests).

### V020-005 Handle session and power transitions

- Status: `[x]`
- Dependencies: V020-004.
- Scope: BUG-002; PRD 12.7; technical 12.7.
- Integrate session/power/shutdown notifications with centralized Stop and resource cleanup.
- Invalidate pending callbacks; remain Stopped after unlock/resume; never replay elapsed intervals.
- Test repeated notifications, Stopped/Running/Error inputs, queued timer races, and bounded shutdown.

Completion criteria: lock/suspend prevents future sequences; resume never auto-starts; shutdown is not vetoed or delayed. Native lifecycle matrix is verified in V020-012.

Implementation record: a Qt native event filter now handles session lock, suspend, query/end-session, and shutdown messages. Relevant events route through Stop, while resume/unlock messages do not restart activity. Native registration and hidden-window resources are cleaned up idempotently during application shutdown. Lifecycle mapping and stop-signal tests pass; packaged Windows 11 lifecycle validation remains in V020-012. Full suite result: 107 passed.

## Deferred future implementation: Smart Mode

FEAT-002 and all Smart Mode feasibility work are deferred from 0.2.0. The tasks below are retained as a future-release starting point and are not part of the 0.2.0 dependency graph or release acceptance.

### SMART-001 Validate Smart Mode monitoring feasibility

- Status: `Deferred`
- Dependencies: V020-001 and the completed 0.2.0 baseline.
- Scope: FEAT-002; PRD 12.6; technical 12.5; TECH-001.
- Evaluate the simplified v1 monitor: dedicated-thread hooks, own-event markers, keyboard/mouse/scrolling, key/button holds at enable, clean start/stop, packaged standard-user operation, and callback latency.
- Confirm UI responsiveness and document hook limitations without building Raw Input fallback, automatic recovery, remote-session support, extra device classes, or monitoring telemetry.
- Record findings and the chosen v1 approach in technical requirements without claiming guaranteed detection of every hook loss.

Completion criteria: future-release task; TECH-001 has an evidence-backed implementation approach before Smart Mode production work begins.

SMART-001 acceptance evidence must cover monitor startup/failure, keyboard activity, mouse movement and buttons, vertical and horizontal scrolling, held-input suppression through final release, own F15/Scroll Lock exclusion, other observed input, clean stop and stale-callback rejection, UI responsiveness, and packaged standard-user Windows 11 operation. Raw Input fallback, automatic recovery, remote sessions, extra device classes, and telemetry are deferred from this gate.

### SMART-002 Implement Smart Mode activity monitor

- Status: `Deferred`
- Dependencies: SMART-001.
- Scope: FEAT-002; PRD 12.6; technical 12.5.
- Implement validated monitoring with thread-safe activity/held-state delivery, own-input exclusion, minimal transient data, and teardown.
- Include keyboard down/up, mouse movement/buttons, vertical/horizontal scroll, and held-state initialization/reconciliation.
- Test repeat-down, final release, initialization failure, self-input versus other injected input, coalescing, and stale events after teardown. Do not log typed input.

Completion criteria: activity signals preserve idle/held semantics and monitoring starts/stops reliably without blocking UI or suppressing user input.

### SMART-003 Implement Smart Mode timing and tray toggle

- Status: `Deferred`
- Dependencies: SMART-002.
- Scope: FEAT-002, BUG-002, BUG-003; PRD 12.6-12.8; technical 12.4-12.7.
- Add checkable tray-only Smart Mode, available only while Running; successful Start always begins normal mode.
- Implement shared-interval idle/repeat timing, fresh enable/disable deadlines, held-input suppression, settings semantics, and dispatch eligibility checks.
- Connect Stop/Error/system events to cancel timing, remove monitoring, uncheck/disable the option, and discard stale callbacks.
- Test boundary input, mode switches, all settings combinations, canceled-dialog user activity, holds, input during batches, failure count across activity pauses, and no automatic resume.

Completion criteria: deterministic fake-clock tests demonstrate all PRD Smart Mode cases; waiting retains Running status and creates no extra public state.

### V020-009 Finish status and tooltip presentation

- Status: `[x]`
- Dependencies: V020-003, V020-005.
- Scope: CHG-001, CHG-003; PRD 12.3; technical 12.8.
- Show Status, Interval, Key, and Last keypress; no Smart Mode or Activity line in 0.2.0.
- Preserve Running/Stopped/Error icons and refresh after every relevant change; append concise truthful warnings/reasons.
- Test all statuses, keys/modes, None/time formatting, and error variants; verify native tooltip readability/length during release checks.

Completion criteria: no user-facing State label remains in the affected tray display and required fields stay readable.

Implementation record: the tray now labels the field Status and shows Status, Interval, Key, and Last keypress. Smart Mode and Activity are absent from the 0.2.0 tooltip. Tooltip refreshes now include selected-key changes, and warning/error details remain visible. Tray tests and the full suite pass (108 tests).

### V020-010 Add About and shared version metadata

- Status: `[x]`
- Dependencies: None (MVP baseline); resolve DOC-001 before completion. Independent UI task.
- Scope: CHG-002; PRD 12.4; technical 12.8.
- Resolve About description wording, add the action immediately above Exit, and implement a reusable dialog with OK.
- Use one application version source shared with packaging; do not hardcode a separate dialog version.
- Test repeated opening, all statuses, no activity interruption, and version consistency; verify bundled display in V020-012.

Completion criteria: approved copy and actual version appear in one dialog; activity, status, and settings remain unchanged when About is opened or closed.

Implementation record: About is immediately above Exit, available in every status, reusable, and non-modal to activity. The dialog uses the approved F15/Scroll Lock description and shared package version `0.2.0`; pyproject metadata reads the same package version. Tray/About/version tests and the full suite pass (109 tests).

### V020-011 Complete regression checks and user documentation

- Status: `[x]`
- Dependencies: V020-009, V020-010.
- Scope: All approved 0.2.0 items; PRD 12.9; technical 12.9.
- Run the full automated suite and resolve regressions without real input in unit tests.
- Update README for implemented tray operations, both keys, errors, session/power behavior, and limitations; identify Smart Mode as deferred and reconcile old platform claims with actual evidence.
- Check scope-to-test coverage and links; preserve historical MVP tasks and release records.

Completion criteria: automated regression suite passes and user instructions accurately describe implemented 0.2.0 behavior.

Implementation record: README now documents the 0.2.0 tray operations, F15 and paired Scroll Lock sequences, session-only settings, Status tooltip fields, About/version display, explicit error behavior, lifecycle stops, Windows 11 validation scope, and Smart Mode deferral. Documentation regression coverage checks the shipped behavior and prevents Smart Mode from being described as available. The full suite passes (110 tests).

### V020-012 Package and verify release 0.2.0

- Status: `[x]`
- Dependencies: V020-011.
- Scope: All approved 0.2.0 items; PRD 12.9; technical 12.9; TECH-003.
- Record exact build dependencies/runtime; reconcile metadata and legacy version requirements, then validate folder and single-file packages.
- Execute the Windows 11 standard-user matrix for both keys, duplicate launches and crash recovery, system transitions, errors, tooltip, and About. Record Smart Mode as deferred and Windows 10 as unverified for this release.
- Create RELEASE_CHECKLIST.md, QA_WINDOWS_INTEGRATION.md, and QA_SUPPORTED_WINDOWS.md in docs/releases/0.2.0 with actual results, environment, commands, artifact hash, and limitations; no copied pass claims.
- Archive executable and matching build metadata without overwriting 0.1.0 evidence. Verify no-console/no-Python operation, no startup registration/network/telemetry/power changes, and actual bundled version.

Completion criteria: release readiness in [RELEASE_PLAN.md](releases/0.2.0/RELEASE_PLAN.md) is demonstrated, all required cases are resolved, and TECH-003 is closed. Packaging/verification does not itself publish a release.

Implementation record: folder and single-file packages were rebuilt with Python 3.13.6, PySide6 6.11.0, and PyInstaller 6.21.0 on Windows 11 build 26200. Both forms launch, the folder validator checks runtime/icon resources, duplicate launch prevention passes, and native F15/Scroll Lock input passes in a medium-integrity standard-user token. The archived single-file artifact and matching metadata are recorded in `release/BUILD_METADATA-0.2.0.md`; release QA records are in `docs/releases/0.2.0/`. The existing folder validator was fixed to refresh its process before cleanup. V020-013 and V020-014 resolve the visual findings, and the rebuilt package passed manual startup tooltip, Settings, About, running, Stop, and Exit checks. Release verification is complete; Windows 10 remains unverified and Smart Mode is deferred.

### V020-013 Initialize tooltip on tray creation

- Status: `[x]`
- Dependencies: V020-012 manual review finding.
- Scope: BUG-004; PRD 12.3; technical 12.8.
- Populate the complete Status, Interval, Key, and Last keypress tooltip before the first Start action.
- Preserve existing refresh behavior for state, settings, success, warnings, and errors.
- Test the initial stopped tooltip and confirm no activity is triggered by initialization.

Completion criteria: hovering the tray icon immediately after launch shows the complete stopped tooltip with the default values.

Implementation record: tray initialization now formats and assigns the complete stopped tooltip before showing the icon. A tray-controller regression test verifies the default Status, interval, key, and `None` timestamp without starting activity. Focused tray tests and the full suite pass (112 tests).

### V020-014 Reposition interval helper text

- Status: `[x]`
- Dependencies: V020-012 manual review finding.
- Scope: CHG-004; PRD 12.5; technical 5.2/12.8.
- Place the whole-number range helper text directly below the interval input and before the key selector.
- Preserve existing validation, sizing, and Save/Cancel behavior.
- Test the dialog layout relationship and retain the existing validation coverage.

Completion criteria: the Settings dialog visually associates the range guidance with the interval field without changing runtime behavior.

Implementation record: the interval range helper label now appears immediately below the interval input and before the key selector. A Settings-dialog regression test verifies the form-row order while existing validation and Save/Cancel tests remain unchanged. Focused Settings tests and the full suite pass (113 tests).
