# Undead Idler Product Requirements Document

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
