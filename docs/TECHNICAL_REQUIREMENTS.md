# Undead Idler Technical Requirements

## Release scope

Sections 1-11 preserve the original MVP design. Section 12 defines planned 0.2.0 behavior and supersedes conflicting MVP design for that release, including fixed F15, Settings contents, and error rules. Section 12.5-12.6 is retained as deferred Smart Mode design and is excluded from 0.2.0. See [PRD](PRD.md#12-planned-020-requirements), [release plan](releases/0.2.0/RELEASE_PLAN.md), and [tasks](IMPLEMENTATION_TASKS.md#release-020-planned-implementation). No 0.2.0 functionality or QA completion is implied.

## 1. Purpose

This document translates the requirements in `docs/PRD.md` into an implementation design and ordered build sequence for the Undead Idler MVP.

The MVP is a Windows-only Python desktop application with a PySide6 system-tray interface. It directly calls the Windows `SendInput` API through Python `ctypes` to generate periodic F15 keypresses. It does not launch PowerShell or any other worker process.

## 2. Technical Decisions

- Language: Python 3.11 or newer.
- GUI framework: PySide6.
- Operating system API access: Python `ctypes` and `user32.dll`.
- Input API: Windows `SendInput`.
- Input key: F15, fixed for the MVP.
- Timer: PySide6 `QTimer`.
- Configuration: in-memory only; no settings file or registry storage.
- Packaging: PyInstaller single-executable Windows build.
- UI mode: system tray application with no required persistent main window.
- Startup behavior: manual launch only; no startup registration or scheduled task.
- Initial interval: 5 minutes.
- Valid interval range: 1 through 10 whole minutes, inclusive.
- Automatic failure threshold: 3 consecutive failed keypresses.
- Release build baseline: Python 3.11.x.
- PySide6 release line: 6.11.x, with the exact patch version pinned in project metadata.

## 3. Architecture

The application must run as one process with these logical components:

```text
Application bootstrap
  -> Qt application/event loop
      -> Tray controller
          -> Activity controller
              -> QTimer
                  -> Windows input adapter
      -> Runtime settings controller
      -> Custom icon resources
```

### 3.1 Application Bootstrap

Responsibilities:

- Create the Qt application object.
- Initialize the runtime interval to 5 minutes.
- Create the tray controller and activity controller.
- Start the Qt event loop.
- Ensure the application has no console window in packaged builds.

The bootstrap must not start activity automatically.

### 3.2 Tray Controller

Responsibilities:

- Create and display the custom tray icon.
- Build the tray context menu.
- Expose `Start`, `Stop`, `Settings`, and `Exit` actions.
- Reflect the current application state in the menu and icon.
- Build and refresh the tray tooltip.
- Forward user actions to the activity and settings controllers.

The tray controller must not directly construct Windows input structures or manage timer callbacks.

### 3.3 Activity Controller

Responsibilities:

- Own the `Stopped`, `Running`, and `Error` states.
- Own the `QTimer` used for repeated keypresses.
- Send the immediate first keypress when starting.
- Start repeated keypresses after the configured interval.
- Stop the timer when activity is stopped or an error threshold is reached.
- Track the last successful keypress timestamp.
- Track consecutive failures.
- Emit state and timestamp changes for the tray controller.

The controller must prevent multiple active timers. Starting an already running controller must be idempotent.

### 3.4 Runtime Settings Controller

Responsibilities:

- Hold the current interval in memory.
- Initialize the interval to 5 minutes at every launch.
- Validate whole-minute values from 1 through 10.
- Apply a saved interval to future timer events.
- Reject invalid values without changing the active interval.

No runtime setting may be written to disk, the Windows registry, environment variables, or a remote service.

### 3.5 Windows Input Adapter

Responsibilities:

- Define the `INPUT`, `KEYBDINPUT`, and related ctypes structures required by `SendInput`.
- Define the F15 virtual-key value.
- Submit one F15 key-down event and one F15 key-up event as a complete keypress.
- Return a clear success or failure result to the activity controller.
- Keep all Windows API-specific code isolated from the Qt UI.

The adapter must not hold F15 between timer events. A key-down event must always be paired with a key-up event in the same keypress operation.

Reference documentation:

- [Python ctypes](https://docs.python.org/3.11/library/ctypes.html)
- [Microsoft SendInput](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendinput)
- [Microsoft INPUT structure](https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-input)

## 4. Application State and Behavior

### 4.1 States

`Stopped`

- No timer is active.
- No synthetic input is generated.
- The tray icon indicates inactive state.

`Running`

- The timer is active.
- F15 keypresses are generated according to the configured interval.
- The tray icon indicates active state.
- The tooltip shows the interval and last successful keypress.

`Error`

- The timer is stopped.
- No additional keypresses are generated.
- The tray icon or tooltip indicates an input failure.
- The user can select Start to attempt a new run.

The implementation must use an explicit `Error` state so the tray controller can distinguish automatic failure from a normal user stop.

### 4.2 Start Sequence

When the user selects `Start`:

1. Validate the current interval.
2. Reset the consecutive-failure counter.
3. Submit one complete F15 keypress immediately.
4. If successful, record the local timestamp and transition to `Running`.
5. If unsuccessful, record the failure and apply the failure policy.
6. If the initial attempt succeeds, start the timer using the configured interval.

The first keypress must not be delayed until the first timer interval expires.

### 4.3 Repeated Keypress Sequence

On each timer timeout:

1. Submit one complete F15 keypress.
2. On success, update the last-successful-keypress timestamp and reset consecutive failures to zero.
3. On failure, increment consecutive failures and leave the timestamp unchanged.
4. After the third consecutive failure, stop the timer and transition to `Error`.

The timer interval must be calculated in milliseconds from the current whole-minute setting.

### 4.4 Stop Sequence

When the user selects `Stop`:

- Stop the timer immediately.
- Reset the consecutive-failure counter.
- Transition to `Stopped`.
- Preserve the last-successful-keypress timestamp for display during the current application session.

Stop must not send a compensating keypress.

### 4.5 Settings Changes

When the user saves a valid interval:

- Update the in-memory interval.
- Close the settings dialog.
- Refresh the tooltip.
- If running, stop and restart the timer so the next keypress occurs one full new interval after the settings change.
- Do not send an extra keypress solely because the interval changed.

When the user cancels or enters an invalid value:

- Keep the prior interval unchanged.
- Keep the current running state unchanged.

## 5. Tray User Interface

### 5.1 Menu

The tray menu must contain:

- `Start`: enabled when stopped or in error state.
- `Stop`: enabled when running.
- `Settings`: always enabled.
- `Exit`: always enabled.

The menu should visually distinguish the active state through action availability and icon treatment.

### 5.2 Settings Dialog

The settings dialog must contain:

- A whole-number interval input.
- The allowed range, 1 through 10 minutes.
- `Save` and `Cancel` actions.

The dialog must reject fractional, empty, non-numeric, below-minimum, and above-maximum values.

The dialog must not expose key selection, schedules, power settings, application targeting, or persistence options.

### 5.3 Tooltip

The tooltip must refresh when:

- The state changes.
- The interval changes.
- A keypress succeeds.
- An input failure occurs.

The running tooltip must include:

- `Running` state.
- Current interval.
- Last successful keypress local date and time.

The stopped tooltip must include the stopped state and current interval. If no successful keypress has occurred during the session, it should display an explicit empty value such as `Inactive`.

The error tooltip must use this structure:

```text
Undead Idler - Error
Activity stopped after 3 consecutive input failures
Last keypress: YYYY-MM-DD HH:mm:ss
```

If no successful keypress occurred during the session, the last line must display `None`.

The initial error presentation must use the error icon state, menu state, and tooltip. A Windows notification is not required for the MVP.

The timestamp must use the user's local system time and the format `YYYY-MM-DD HH:mm:ss`.

## 6. Custom Icon Requirements

- Provide a custom Undead Idler icon in a Windows-compatible format.
- Include at least the standard application icon and tray icon sizes required by Windows.
- Provide visually distinct inactive, active, and error treatments.
- Use a compact undead/skull visual with a dark neutral base and a restrained green active treatment.
- Use a muted gray treatment for stopped and a red treatment for error.
- Package the icon resources into the executable.
- Ensure the icon remains legible at small tray sizes.

The icon design itself is a separate asset task, but the application must support loading the resulting resource without an absolute development-machine path.

## 7. Error Handling

The input adapter must treat an incomplete or failed `SendInput` submission as a failure. The activity controller must not update the timestamp on failure.

The application must:

- Keep the UI responsive if an input call fails.
- Display a local error indication.
- Stop after 3 consecutive failures.
- Reset the failure counter after a successful keypress.
- Allow the user to retry with Start after an automatic stop.
- Avoid silently continuing after the failure threshold.

The implementation should log diagnostic details during development, but the MVP must not collect or transmit telemetry.

## 8. Project Structure

The implementation should use a separation similar to:

```text
src/
  undead_idler/
    __init__.py
    __main__.py
    app.py
    tray_controller.py
    activity_controller.py
    settings_controller.py
    win_input.py
    models.py
    resources/
      icons/
tests/
  test_settings.py
  test_activity_controller.py
  test_tooltip.py
assets/
  undead_idler.ico
pyproject.toml
README.md
```

The exact module names may change during implementation, but UI, timing/state logic, settings validation, and Windows API integration must remain separable.

## 9. Dependency and Build Requirements

- Declare Python compatibility as `>=3.11`.
- Use Python 3.11.x for development and release builds.
- Keep source compatibility with Python 3.11 and newer.
- Use the PySide6 6.11.x release line.
- Pin the exact tested PySide6 patch version in project metadata.
- Keep runtime dependencies limited to PySide6 and the Python standard library where practical.
- Do not require PowerShell, a separate Python installation, or a network connection at runtime.
- Build on Windows because the target executable is Windows-specific.
- Use PyInstaller for packaging.
- Use a windowed/no-console build mode.
- Validate a folder-based PyInstaller build before producing the single-executable build.
- Include the custom icon in the PyInstaller build configuration.

## 10. Testing Requirements

### 10.1 Unit Tests

Unit tests must cover:

- Default interval initialization to 5 minutes.
- Acceptance of integer values from 1 through 10.
- Rejection of fractional, empty, non-numeric, and out-of-range values.
- Runtime-only settings behavior.
- State transitions for Start, Stop, Error, and retry.
- Immediate first-keypress behavior through a mocked input adapter.
- Failure counter reset after success.
- Automatic stop after 3 consecutive failures.
- Last-successful-keypress timestamp updates only after success.
- Tooltip content for stopped, running, and error states.

### 10.2 Windows Integration Tests

On a supported Windows machine, manually verify:

- The packaged executable launches without a console window.
- The tray icon appears and uses the custom asset.
- Start sends F15 immediately.
- Repeated keypresses occur at the configured interval.
- Stop prevents further keypresses.
- Changing the interval affects future timer events.
- Relaunching resets the interval to 5 minutes.
- Teams and Outlook behavior can be observed during a running session.
- Three failed input attempts produce an automatic stop and visible error state.

### 10.3 Package Verification

Verify that the single executable:

- Runs on Windows 10 and Windows 11 test environments.
- Does not require Python to be installed.
- Does not require a console window.
- Contains the required Qt runtime components and icon resources.
- Starts in the stopped state.
- Does not create startup entries or scheduled tasks.

## 11. Ordered Implementation Plan

### Phase 1: Project Foundation

1. Create the Python project metadata and virtual environment instructions.
2. Establish the `src` and `tests` layout.
3. Add Python version and PySide6 dependency constraints.
4. Add basic test and formatting commands.

Exit criteria: the project installs on Windows and a minimal PySide6 application can start and exit.

### Phase 2: Windows Input Adapter

1. Define the ctypes structures and constants for `SendInput`.
2. Implement one complete F15 keypress operation.
3. Return explicit success or failure.
4. Add mocked unit tests for adapter consumers.
5. Manually validate F15 input on Windows.

Exit criteria: a standalone development command can submit F15 and report whether submission succeeded.

### Phase 3: Activity Controller

1. Implement the stopped/running/error state model.
2. Add immediate first keypress behavior.
3. Add QTimer-based repeated input.
4. Add interval updates without persistence.
5. Add timestamp and consecutive-failure tracking.
6. Add automatic stop after 3 consecutive failures.
7. Add unit tests with a mocked input adapter and controllable timer abstraction where needed.

Exit criteria: activity behavior is testable without the tray UI and meets all timing/state requirements.

### Phase 4: Settings Dialog

1. Implement the interval input control.
2. Add whole-number and range validation.
3. Add Save and Cancel behavior.
4. Connect valid changes to the activity controller.
5. Add validation and runtime-only behavior tests.

Exit criteria: the user can change the interval during a session, and every new launch returns to 5 minutes.

### Phase 5: Tray Interface

1. Add the custom tray icon resource.
2. Implement the tray menu actions.
3. Connect menu state to the activity controller.
4. Add active, stopped, and error icon treatments.
5. Implement tooltip formatting and refresh events.
6. Add clean Exit behavior.

Exit criteria: the complete application can be operated from the tray without a main window.

### Phase 6: Packaging

1. Configure PyInstaller for a windowed build.
2. Produce and test a folder-based build.
3. Resolve Qt plugin and resource inclusion issues.
4. Produce the single-executable build.
5. Verify launch, tray behavior, icon loading, and no-console behavior.

Exit criteria: the packaged single executable runs independently of a Python installation.

### Phase 7: Verification and Release Readiness

1. Run the complete automated test suite.
2. Perform Windows integration testing.
3. Verify interval, state, failure, timestamp, and restart behavior against the PRD.
4. Test on Windows 10 and Windows 11 where available.
5. Document launch and operation instructions.
6. Record known limitations, including that the application does not directly control Teams or Outlook presence and does not prevent sleep.

Exit criteria: all PRD acceptance criteria are demonstrated and known limitations are documented.

## 12. Planned 0.2.0 design

### 12.1 Components and ordering

Extend the existing architecture with an instance guard and a session/power event adapter. Smart Mode monitoring is deferred and is not part of the 0.2.0 architecture. The activity controller remains the owner of status, failure counts, and scheduling. Use a monotonic clock for elapsed time and local wall time only for display timestamps.

Implementation sequence: instance guard; errors; selectable sequences; system transitions; final UI; release verification. Smart Mode feasibility and orchestration are future-release work. See release tasks for exact dependencies.

### 12.2 Single-instance guard (BUG-001)

Proposed mechanism: a Windows named mutex scoped to the current user and Windows session, acquired atomically before tray construction or input setup. Keep its handle for the process lifetime and close it during exit. An already-existing guard causes the new process to return silently; do not signal, stop, or alter the owner. Validate simultaneous launch, crash recovery, and PyInstaller single-file startup rather than relying on process-name searches or stale PID files. Distinguish guard acquisition errors from duplicate detection. Final naming and access handling are implementation details to validate; cross-session exclusion is not required.

### 12.3 Input adapter and results (FEAT-001, BUG-003)

Represent the selected key with a validated enum. Construct one SendInput batch per event: F15 down/up (2 events) or Scroll Lock down/up/down/up (4 events). Put an application-specific pointer-sized marker in every event's dwExtraInfo, including cleanup events. A listener ignores only our marked events, not all injected input.

Return structured results that distinguish full, zero, and partial submission, including requested/submitted counts and useful diagnostics. Count failures per sequence, not per individual press. Never infer that successful submission proves a target application's presence or toggle behavior.

For partial submission, perform at most a bounded, best-effort release of the potentially held simulated key, then report immediate Error. Do not replay the batch or send speculative toggle corrections. Cleanup is not success and cannot reset the failure count or timestamp. Avoid claiming the original Scroll Lock state was restored. Validate the cleanup algorithm against the API's guarantees; a returned count alone must not be treated as stronger evidence than documented. Failure to clean up must remain visible in the error reason.

Sources: [SendInput](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendinput), [KEYBDINPUT](https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-keybdinput). The batch orders submitted events without interleaving other user input; it is not a guarantee that every event succeeds.

### 12.4 Failure state transitions

Allow Stopped -> Error for unsuccessful Start. Start from either Stopped or Error clears transient failures and attempts the selected sequence immediately. Full success enters Running and schedules the next event; any Start failure enters Error without a retry timer.

During Running, zero-submission failures 1 and 2 preserve Running with a warning; failure 3 enters Error. Full success clears failures and updates time. Partial submission enters Error immediately after bounded cleanup. Smart Mode failure behavior is deferred.

Centralize Error entry: invalidate pending work, cancel timers, retain last success, and emit reason/status updates. Stop clears transient errors and retains interval, key, and last success. Start is idempotent while Running.

### 12.5 Deferred activity monitor (FEAT-002)

This section is deferred from 0.2.0 and retained for a future Smart Mode release. It is not a 0.2.0 implementation dependency.

Planned v1 approach: one Windows low-level keyboard and mouse hook monitor on a dedicated thread with a message loop. Run it only while Smart Mode is on. Callbacks must promptly forward events through the hook chain, never suppress user input, and avoid UI work, disk writes, or blocking operations. Marshal only minimal activity/held-state information to the controller using thread-safe notification and coalesce high-frequency mouse movement without losing the latest activity time or releases. This first build does not implement Raw Input fallback, automatic hook recovery, remote-session monitoring, extra device classes, or monitoring telemetry.

Ignore our marker and count other observed events, including injected accessibility input. Track key identities only while needed to maintain the held set, mouse-button states, and last activity time. Do not decode text, retain event history, log key identifiers, or collect application/window content. Include vertical and horizontal scrolling. Repeated key-down does not create duplicate held entries; releases remove them. Reconcile keys/buttons already held when monitoring starts and test missed-release/multiple-device behavior so tracking cannot incorrectly authorize idle input.

Keep elapsed-time scheduling independent of system clock changes. Recheck current activity and held state at dispatch, not only when scheduling. A generation/cancellation token or equivalent must reject callbacks queued before Stop, Error, a mode change, or a system transition. The first-build monitor needs only a small held-key/button set and one latest-activity timestamp; it does not retain event history.

Technical validation gate: [Microsoft's hook guidance](https://learn.microsoft.com/en-us/windows/win32/winmsg/lowlevelkeyboardproc) warns that timed-out hooks can be removed silently and recommends considering Raw Input. For v1, validate only callback latency, startup held-state reconciliation, own-input filtering, clean start/stop, packaged standard-user operation, and UI responsiveness on Windows 11. Do not claim every hook loss is detectable. If a core v1 case fails, stop before production integration and revisit the design; do not silently weaken product behavior. Known monitoring initialization failure enters Error.

Additional references: [keyboard event metadata](https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-kbdllhookstruct), [mouse callback](https://learn.microsoft.com/en-us/windows/win32/winmsg/lowlevelmouseproc), [GetAsyncKeyState](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getasynckeystate). Validate asynchronous held-state queries outside the hook callback, whose event can precede the state update.

### 12.6 Deferred Smart Mode scheduling and Settings

This section is deferred from 0.2.0 and retained for a future Smart Mode release. It is not a 0.2.0 implementation dependency.

Smart Mode is a boolean orthogonal to Running/Stopped/Error; no public Waiting or Active substatus is introduced. It can be true only while Running.

| Trigger | Timing effect |
| --- | --- |
| Successful Start | Normal mode; first sequence already sent; next due after interval. |
| Enable Smart Mode | Cancel normal schedule, initialize monitor, begin fresh idle countdown. |
| Observed input | Cancel prior eligible deadline; last activity advances. No injection while any key/button is held. |
| All held input released | Begin full idle interval after the final release. |
| Idle deadline | Recheck eligibility; send selected batch; schedule one further interval. |
| Disable Smart Mode | Stop monitor; next normal event one full interval later; no immediate sequence. |
| Changed interval | Restart normal schedule or Smart idle countdown using new interval. |
| Changed key only | Replace next batch selection without independent timing reset. |
| Changed both | New interval deadline with new key. |
| Unchanged Save, Cancel, invalid Save | No settings-driven timing change. User interaction still resets Smart idle timing. |

Validate and commit Settings atomically. Defaults at launch: 5 minutes, F15, Smart Mode off, Stopped. No settings persistence. Input that arrives during a submitted batch takes effect immediately afterward; do not introduce sleeps between Scroll Lock presses. Preserve the real input timestamp and held state when recalculating idle eligibility.

### 12.7 Session, power, and shutdown (BUG-002)

Proposed Windows integration: register for current-session lock/unlock notifications and process suspend/resume and session-end messages through the Qt native event integration or a dedicated native message window. Validate notification delivery in both folder and single-file packages. Handle lock and suspend by invoking centralized Stop. Unlock/resume defensively retain Stopped and never replay missed deadlines. Shutdown/restart cancels activity, removes monitoring and UI, releases native resources, and exits without vetoing or delaying shutdown. Do not modify power settings or register startup behavior.

Native event ordering can race with queued timer callbacks: invalidate work before teardown and recheck state before submission. Complete already-submitted batches without launching later sequences. Teardown must be idempotent and bounded, including when already Stopped/Error. Pair every registration with cleanup. Hard process termination cannot guarantee cleanup; never claim otherwise.

### 12.8 Tray, Settings, and About (CHG-001/002/003)

Menu: Start, Stop, Settings, About, Exit, with separators as useful. About is immediately above Exit. Smart Mode is deferred from 0.2.0. Settings exposes only interval and key selection. Keep distinct Running/Stopped/Error icons; no Activity field.

Use the four 0.2.0 tooltip fields in PRD 12.3 (Status, Interval, Key, and Last keypress), with concise appended warning/error reason. Refresh on status, interval, key, success, and warning changes. Validate native tooltip length/rendering; do not let a long diagnostic hide essential status/error information. A startup failure or partial submission must not display a misleading three-failure message.

About uses a single reusable dialog, OK, the approved description (subject to DOC-001), and a shared application version source that also drives packaging metadata. Verify the bundled version without assuming installed package metadata exists. Opening dialogs must not block activity scheduling or change status.

### 12.9 Verification and release evidence

Use mocked adapters, fake monotonic time, and controllable monitor/system events for deterministic logic tests. Cover all result counts, no false success on cleanup, Start failure, error retry, settings atomicity, deadline boundaries, held input, self-input exclusion, stale callbacks, and repeated teardown. Keep real input out of unit tests.

Record Windows 11 integration evidence for both keys, simultaneous launch/crash recovery, lock/unlock, sleep/resume, hibernate/resume where supported, and shutdown/restart. Test standard-user operation and full tooltip/About rendering. Smart Mode monitoring and its feasibility matrix are deferred to a future release. Record Windows 10 as unverified for 0.2.0 and record other unsupported environmental cases explicitly rather than marking them passed.

Build and test folder packaging before single-file packaging. Record exact Python, PySide6, PyInstaller, OS builds, artifact identity/hash, and test commands/results. Keep source compatibility at Python >=3.11 and use Python 3.13.6, PySide6 6.11.0, and PyInstaller 6.21.0 for the reproducible 0.2.0 release build. Create version-specific evidence under docs/releases/0.2.0 during verification. README is updated when behavior is implemented; do not publish planned features as currently available.
