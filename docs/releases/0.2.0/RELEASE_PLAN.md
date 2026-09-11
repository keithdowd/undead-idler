# Undead Idler Release Plan

Planning date: 2026-09-11. Target: **0.2.0**. Status: implementation complete; release verification is in progress. No release date is assigned.

## Document ownership

- [PRD](../../PRD.md#12-planned-020-requirements): planned product behavior and acceptance requirements.
- [Technical requirements](../../TECHNICAL_REQUIREMENTS.md#12-planned-020-design): design, technical assumptions, and verification approach.
- [Implementation tasks](../../IMPLEMENTATION_TASKS.md#release-020-planned-implementation): executable work units, dependencies, completion criteria.
- This document: scope, release grouping, unresolved decisions, and unscheduled backlog.

The original MVP sections remain explicitly historical; the 0.2.0 sections override conflicts for the new release. [0.1.0 checklist](../0.1.0/RELEASE_CHECKLIST.md), [integration evidence](../0.1.0/QA_WINDOWS_INTEGRATION.md), and [platform evidence](../0.1.0/QA_SUPPORTED_WINDOWS.md) remain unchanged. Executables stay under the repository's release/ directory, separate from docs/releases/.

## Approved 0.2.0 scope

Planning IDs identify scope; task IDs identify implementation work and current status.

| ID | Type | Outcome | PRD section | Technical section | Tasks |
| --- | --- | --- | --- | --- | --- |
| BUG-001 | Bug fix | Prevent duplicate instances per user session; leave existing instance unchanged. | 12.2 | 12.2 | V020-001 |
| BUG-002 | Bug fix | Stop on lock/sleep/hibernate; remain Stopped after unlock/resume; exit cleanly on shutdown/restart. | 12.7 | 12.7 | V020-005 |
| BUG-003 | Bug fix | Visible initial/run failures; explicit failed Start; immediate Error for partial sequences. | 12.8 | 12.3-12.4 | V020-002, V020-004 |
| CHG-001 | Change | Rename State to Status; retain Running/Stopped/Error. | 12.3 | 12.8 | V020-009 |
| CHG-002 | Change | About menu/dialog with description and actual release version. | 12.4 | 12.8 | V020-010 |
| CHG-003 | Change | Show selected key in tooltip. | 12.3 | 12.8 | V020-009 |
| BUG-004 | Bug fix | Initialize the complete tray tooltip before the first user action. | 12.3 | 12.8 | V020-013 |
| CHG-004 | Change | Place the interval range helper text directly below the interval input. | 12.5 | 5.2, 12.8 | V020-014 |
| FEAT-001 | Feature | Settings offers F15 or paired Scroll Lock; session-only selection. | 12.5 | 12.3, 12.6 | V020-003, V020-004 |

All items also flow through V020-011, V020-012, and the V020-013/014 follow-up tasks for documentation, regression testing, packaging, and release evidence. No separate 0.1.1 release is planned.

## Agreed behavior summary

- Launch Stopped with 5 minutes, F15, Smart Mode off. Start sends the selected sequence immediately in normal mode.
- System lock/suspend stops activity; unlock/resume requires manual Start. Shutdown/restart exits cleanly without delaying shutdown.

Smart Mode (FEAT-002) and its feasibility work are intentionally deferred from 0.2.0. The detailed behavior remains recorded as a future-release product and technical concept in the PRD and technical requirements.

## Implementation and release sequence

1. V020-001: single-instance guard.
2. V020-002: error policy and visibility.
3. V020-003/004: selectable sequences, tagging, and partial-input cleanup.
4. V020-005: session/power lifecycle.
5. V020-009/010: final tooltip and About changes.
6. V020-011/012: regression verification, user docs, packaging, and recorded Windows checks.
7. V020-013/014: resolve visual findings from the packaged manual review.

The Status rename and About are independent UI work that can move earlier subject to task dependencies. Each implementation task includes relevant checks; final verification assesses the combined packaged product. Follow CONTRIBUTING.md's per-task commit workflow when development begins.

## Decisions and technical validation still open

| ID | Question | Proposed treatment / gate |
| --- | --- | --- |
| DOC-001 | Approved About description names only F15. | **Resolved:** use "A Windows tray utility that generates periodic F15 or paired Scroll Lock keypresses while running to maintain local keyboard activity." Keep the rest of the approved copy. |
| TECH-001 | Can dedicated-thread hooks reliably meet monitoring requirements? | **Deferred with FEAT-002:** the simplified v1 feasibility gate is retained for a future Smart Mode release. It is no longer a 0.2.0 dependency. |
| TECH-002 | What limited cleanup is justified after partial SendInput? | **Resolved:** if a partial batch ends after key-down, send one bounded key-up cleanup; if it ends after key-up, send no extra sequence. Enter Error immediately, never replay or speculate about Scroll Lock restoration, and leave the success timestamp unchanged. V020-004 validates this policy against Windows behavior. |
| TECH-003 | Which exact build runtime/dependency versions are tested? | **Resolved:** keep source compatibility at Python >=3.11; build 0.2.0 reproducibly with Python 3.13.6, PySide6 6.11.0, and PyInstaller 6.21.0. V020-012 records the exact environment and Windows 11 evidence. Windows 10 remains an unverified target for this release. |

These are wording/technical validation items; they do not undo approved user-visible behavior. Do not mark feasibility or QA gates complete without evidence.

## Release readiness

- All 0.2.0 tasks complete with their acceptance evidence and no unresolved blocking decisions.
- Relevant automated checks and the full regression suite pass; no inherited 0.1.0 pass claims.
- Folder and single-file packaging validated, including resources, version display, no-console startup, and no separate Python requirement.
- Windows 11 standard-user evidence covers input, single instance, lifecycle, dialogs, and tooltip. Windows 10 is recorded as unverified for this release; unavailable scenarios are identified rather than marked passed.
- Updated README describes implemented behavior and limitations accurately.
- During verification, create RELEASE_CHECKLIST.md, QA_WINDOWS_INTEGRATION.md, and QA_SUPPORTED_WINDOWS.md under docs/releases/0.2.0/. Record actual results and artifact hashes/build versions; do not prefill passes.
- Archive the tested 0.2.0 artifact and matching build metadata without overwriting 0.1.0 evidence. Release date/publication follows readiness, not this planning edit.
- Current gate: the interval helper-text placement remains outstanding; do not merge to `main` or sign off distribution until CHG-004 is resolved and the remaining interactive checks are recorded.
- Manual review findings are tracked as BUG-004 and CHG-004 and must be resolved before the release gate closes.

## Future backlog — not scheduled

No entry below is committed to 0.2.0 or assigned another release. Priorities and detailed acceptance criteria will be set when selected; do not add implementation tasks yet.

| ID | Item | Purpose and next step |
| --- | --- | --- |
| BKL-001 | Explorer tray-icon recovery | Verify current behavior after Explorer restarts; identify recovery work needed so users retain access to Stop/Exit. |
| BKL-002 | Improved error visibility | Consider notifications for errors that stop activity; define triggers and suppression of repeated alerts. |
| BKL-003 | Keyboard accessibility and non-color status review | Assess tray navigation, dialogs, and status cues; identify specific gaps before defining changes. |
| BKL-004 | Smart Mode and monitoring feasibility | Move FEAT-002 and TECH-001 into a future release focused specifically on user-activity monitoring, idle scheduling, own-input filtering, held-input tracking, and the simplified Windows 11 feasibility gate. |
