# Undead Idler Product Requirements Document

## Release scope

Sections 1-11 preserve the original 0.1.0 MVP requirements. Section 12 is the planned 0.2.0 specification and supersedes conflicting MVP requirements for that release only. Section 12.6 records a deferred future-release concept and is excluded from 0.2.0 scope. Planned requirements do not describe shipped functionality. See [release plan](releases/0.2.0/RELEASE_PLAN.md) and [0.1.0 evidence](releases/0.1.0/RELEASE_CHECKLIST.md).

## 1. Product Summary

Undead Idler is a local Windows tray application that manually generates periodic F15 keyboard input while enabled. Its intended use is to prevent supported applications such as Microsoft Teams and Outlook from interpreting the user as idle or away.

The application will be distributed as a single Windows executable and will not require a user account, cloud service, or automatic startup configuration.

## 2. Goals

- Allow the user to manually start and stop synthetic keyboard activity.
- Generate an F15 keypress immediately when activity is started.
- Repeat the keypress at a user-configured whole-minute interval.
- Clearly communicate whether activity is running or stopped.
- Show the time of the last successful keypress.
- Package the application as a single Windows executable.
- Provide a custom Undead Idler application and tray icon.

## 3. Non-Goals

Undead Idler will not:

- Call, modify, or automate Teams or Outlook APIs.
- Directly manipulate application presence or availability status.
- Prevent the computer from sleeping, locking, hibernating, or changing display power state.
- Run automatically at Windows login.
- Run synthetic input while the application is stopped.
- Support configurable keys in the initial release; the key will be fixed to F15.
- Require an account, network connection, or external service.

## 4. Target Platform

- Windows 10 and Windows 11.
- Desktop user session only.
- Single packaged Windows executable.
- Python 3.11 or newer for development and build tooling.

## 5. Primary User

A Windows user who wants a simple, manually controlled utility for maintaining local keyboard activity during periods when they are intentionally away from the keyboard.

## 6. User Stories

- As a user, I want to launch Undead Idler manually so it does not run unexpectedly.
- As a user, I want to start activity from the system tray.
- As a user, I want the first F15 keypress to occur immediately after I start activity.
- As a user, I want to configure how many whole minutes pass between keypresses.
- As a user, I want to stop activity immediately from the system tray.
- As a user, I want to see whether the utility is currently active.
- As a user, I want to see when the last successful keypress occurred.

## 7. Functional Requirements

### 7.1 Manual Launch

- The user must launch the application manually.
- The application must not register itself for Windows startup.
- Every launch must begin in the `Stopped` state.
- The application must run as a tray utility without requiring a persistent main window.

### 7.2 Tray Menu

The tray menu must provide:

- `Start`
- `Stop`
- `Settings`
- `Exit`

The menu must prevent duplicate activity loops. Selecting `Start` while already running must not create another timer or increase the keypress frequency. Selecting `Stop` while stopped must have no adverse effect.

### 7.3 Synthetic Input

- The application must generate the F15 key-down and key-up events as a complete keypress.
- The first keypress must occur immediately after `Start` is selected.
- Subsequent keypresses must occur at the configured interval.
- The application must not hold F15 between keypresses.
- The application must not generate input while stopped.

### 7.4 Interval Setting

- The user must be able to configure the interval in whole minutes.
- Fractional-minute values must not be accepted.
- The default interval must be 5 minutes.
- The minimum interval must be 1 minute.
- The maximum interval must be 10 minutes.
- The application must validate the value before saving it.
- The interval must reset to 5 minutes each time the application is launched.
- Changing the interval while running must apply to future keypresses without requiring an application restart.

### 7.5 Status and Tooltip

The tray icon must make the current state visually distinguishable between `Running` and `Stopped`.

The tray tooltip must include:

- Current state.
- Configured interval.
- Time of the last successful keypress when available.

Example running tooltip:

```text
Undead Idler - Running
Interval: 5 minutes
Last keypress: 09/09/2026 2:32:00 PM
```

Before the first keypress, the tooltip may display `Last keypress: None` or an equivalent message.

The last-keypress timestamp must be updated only after the complete F15 keypress has been successfully submitted.

### 7.6 Stop and Exit

- `Stop` must stop future keypresses immediately.
- `Exit` must stop activity before closing the application.
- Exiting must remove the tray icon and terminate the application cleanly.
- No confirmation dialog is required for Exit in the initial release.

### 7.7 Error Handling

- The application must detect and report failures when synthetic input cannot be submitted.
- A failed keypress must not update the last-successful-keypress timestamp.
- The application must display an error state through the tray tooltip or another visible local indication.
- After 3 consecutive input failures, the application must stop the activity loop automatically rather than continuing silently.
- The user-facing error presentation will be defined during technical requirements.

## 8. Configuration and Privacy

- Interval configuration is session-only and must not be persisted between application launches.
- Every application launch must use the 5-minute default interval.
- No usage data, keypress history, telemetry, credentials, or network data may be collected.
- The application must not require administrator privileges for normal operation.

## 9. Non-Functional Requirements

- The application should have a small memory and CPU footprint while stopped or running.
- Start and Stop actions should feel immediate to the user.
- The single executable should run without requiring a separate Python installation.
- The packaged application must launch without opening a console window.
- The application and tray icon should use custom Undead Idler branding.
- The application should provide a clear distinction between an intended active state and an input failure.
- The application should be maintainable with a separation between tray UI, activity timing, runtime configuration, and Windows input integration.

## 10. Acceptance Criteria

The MVP is acceptable when:

1. A user can launch the packaged executable manually and see a tray icon.
2. The application starts in the `Stopped` state.
3. Selecting `Start` sends an F15 keypress immediately.
4. Additional F15 keypresses occur at the configured whole-minute interval.
5. Selecting `Stop` prevents further keypresses.
6. The user can change and save the interval, with fractional values rejected.
7. The interval resets to 5 minutes after closing and relaunching the application.
8. The tooltip shows the current state, interval, and last successful keypress time.
9. Selecting `Exit` stops activity and closes the application.
10. Three consecutive input failures stop the activity loop.
11. Input failures are visible and do not produce an incorrect success timestamp.
12. The single packaged executable runs on the supported Windows versions without a separate Python installation.
13. The application and tray icon use the custom Undead Idler icon.

## 11. Technical Design Follow-Up

The next document should define:

- Python 3.11 or newer and PySide6 version targets.
- The Windows `SendInput` integration and ctypes data structures.
- Timer and state-management behavior.
- Runtime-only interval configuration and default handling.
- Tray icon states and tooltip update behavior.
- Failure detection and automatic-stop rules.
- Single-executable packaging and build configuration.
- Custom icon asset format and packaging.
- Automated and manual test strategy.

## 12. Planned 0.2.0 requirements

Status: approved planning scope; implementation and release verification not started.

### 12.1 Scope and retained constraints

The release adds selectable input while retaining manual launch, Windows 10/11 support, no console, no administrator requirement for normal operation, and a single packaged executable. Smart Mode is deferred to a future release. It does not prevent lock or sleep, directly control presence, add startup registration, persist settings, or collect input history or telemetry. Configurable keys are now limited to F15 and Scroll Lock; the MVP fixed-key restriction is superseded. Notifications, Explorer tray recovery work, Smart Mode, and a broader accessibility review remain unscheduled backlog items.

### 12.2 BUG-001: Single instance

Only one instance may run per Windows user session. A duplicate launch must exit silently before creating UI, monitoring, or an input loop. It must not close or modify the existing instance. Simultaneous launches must yield one instance. Normal exit and crashes must not prevent a later launch.

### 12.3 CHG-001, CHG-003: Status and tooltip

Replace the user-facing label `State` with `Status`. Values remain `Running`, `Stopped`, and `Error`. No Smart Mode or Activity line is included in the 0.2.0 tooltip.

The tooltip must show these fields in every status, refreshing when values change:

```text
Status: Running
Interval: 5 minutes
Key: Scroll Lock
Last keypress: 2026-09-11 14:32:00
```

Use `On`/`Off`, local time formatted `YYYY-MM-DD HH:mm:ss`, and `None` before a successful sequence. Preserve the timestamp through Stop and Error within the session. Append concise warnings or error reasons as appropriate; do not claim three failures for other error causes.

### 12.4 CHG-002: About

Add About immediately above Exit in the tray menu. It is available in all statuses and opens one reusable dialog with OK; repeated selection brings the existing dialog forward. Opening or closing it does not change status or settings. Future Smart Mode behavior will define how dialog interaction counts as activity.

Approved description:

> A Windows tray utility that generates periodic F15 or paired Scroll Lock keypresses while running to maintain local keyboard activity. Start and stop activity manually, and configure the interval in Settings.
>
> Undead Idler does not directly control application presence or prevent your computer from sleeping.

Show `Undead Idler` and the actual application release version from shared version metadata (0.2.0 for this release, not the earlier example's 0.1.0). The description above reflects the selectable F15 and Scroll Lock keys.

### 12.5 FEAT-001: Key selection

Settings offers F15 or Scroll Lock alongside the existing whole-minute interval (1-10, default 5). F15 is the launch default; key selection is session-only. Each activity event sends one complete F15 press or two consecutive complete Scroll Lock presses. This applies to immediate Start and subsequent events. A successful Scroll Lock pair normally restores the original toggle state; failure handling must not promise restoration after partial submission.

Save validates all fields before applying either. Cancel or invalid input keeps prior settings. Key-only changes affect the next sequence without resetting its schedule. Interval changes restart timing with the new interval; combined changes use the new key and interval. Save without changes has no timing side effect. Settings never contains Smart Mode.

### 12.6 Deferred FEAT-002: Smart Mode

Smart Mode is deferred from 0.2.0 and is retained here as a future-release concept. It is not part of the 0.2.0 acceptance criteria or implementation sequence.

Smart Mode is a checkable tray option, off by default and unavailable while Stopped or Error. Start first attempts an immediate sequence in normal mode. Only a successful Start makes Smart Mode available. Enabling it cancels normal timing and starts a fresh idle countdown. Disabling it schedules the next normal sequence one full configured interval later, without immediate input.

Smart Mode uses the same Settings interval for both idle detection and repeated sequences. Keyboard down/up, mouse movement, button down/up, and scrolling count as activity. Held keys/buttons are ongoing activity; count idle time only after all are released. Activity resets the countdown, pauses future sequences, and does not change Running status. After one full idle interval, send a sequence, then repeat at that interval until activity resumes. Ignore this application's tagged input; count other observed input, including accessibility-generated input. Touch, pen, controllers, and remote-session support are not promised by this scope.

Changing the interval restarts the idle countdown. Changing only the key does not independently reset it. Interaction with Settings or other UI still counts as user activity, including Cancel and unchanged Save. If input arrives during an already-submitted sequence, finish that sequence and restart idle timing from the user activity; held-input rules still apply.

Stop turns Smart Mode off, makes it unavailable, stops timing and monitoring, and preserves session settings. Every later Start begins in normal mode.

### 12.7 BUG-002: Session and power transitions

Lock, sleep, or hibernate invokes Stop behavior: cancel future input and monitoring, turn Smart Mode off, and show Stopped. Unlock and resume remain Stopped and require manual Start. Shutdown/restart stops activity and exits cleanly without blocking shutdown; the next launch is Stopped. These rules apply to normal mode and Smart Mode, including pending callbacks.

### 12.8 BUG-003: Errors in normal mode

| Outcome | Required behavior |
| --- | --- |
| Complete sequence submitted | Update success timestamp; clear warning and consecutive-failure count. |
| Start submits no events | Enter Error immediately, stop timers, show reason, require manual retry. |
| Running sequence submits no events: failure 1 or 2 | Stay Running, show warning with count, retry at next eligible interval. |
| Third consecutive zero-event failure while Running | Enter Error and cancel timing. |
| Partial sequence, including partial F15 | Attempt bounded key-release cleanup; enter Error immediately; do not blindly replay or toggle Scroll Lock. |
| Smart Mode monitoring cannot initialize | Deferred with Smart Mode; not a 0.2.0 case. |

Failed attempts and cleanup do not update the success timestamp. Start from Error clears the count and attempts normal-mode input again. Partial Scroll Lock failure must explain `Input sequence incomplete. Check Scroll Lock state.` No notification dialog is required. Smart Mode error behavior is deferred with FEAT-002.

### 12.9 Release acceptance

All in-scope requirements in 12.2-12.5, 12.7, and 12.8 must have automated or recorded Windows verification, including simultaneous launches/crash recovery, both keys, all failure classes, settings changes, and session/power transitions. Deferred section 12.6 is excluded from 0.2.0 acceptance. Retained MVP behavior must not regress. The packaged build must display its actual version, run without Python or elevation, and have Windows 11 evidence. Windows 10 remains a documented target platform but is unverified for 0.2.0; no Windows 10 support claim may be presented as tested. No 0.1.0 pass record establishes a 0.2.0 pass.
