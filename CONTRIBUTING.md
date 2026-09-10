# Contributing to Undead Idler

## Development Environment

Undead Idler is developed and packaged on Windows with Python 3.11 or newer.

Create the project-local virtual environment from the repository root:

```powershell
py -3.11 -m venv .venv
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the declared dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The active shell should show the virtual-environment Python when running:

```powershell
python --version
python -c "import sys; print(sys.executable)"
```

Do not commit `.venv` or generated build output.

## Validation

Run the test suite from an activated virtual environment:

```powershell
python -m pytest
```

Run the application from the activated virtual environment after the application entry point is implemented:

```powershell
python -m undead_idler
```

Use the project metadata and requirements file as the source of truth for the supported Python and dependency versions.

## Implementation Workflow

1. Select the next incomplete task in `docs/IMPLEMENTATION_TASKS.md`.
2. Confirm that its listed dependencies are complete.
3. Implement only the selected task and its required tests or assets.
4. Run the relevant validation commands.
5. Mark the task complete in `docs/IMPLEMENTATION_TASKS.md` in the same change.
6. Create one Git commit for the task.

Each task must have its own commit. Setup, asset, testing, and packaging tasks follow the same rule as coding tasks.

Commit messages should identify the task and describe the result. Use the format:

```text
<task-id>: <short description>
```

Examples:

```text
UI-001: add Python project metadata
WIN-002: implement F15 SendInput adapter
QA-001: add activity controller tests
```

Do not combine unrelated tasks in one commit. Do not amend an existing task commit unless explicitly requested.

## Baseline Commit

The initial baseline commit contains the approved planning documents, project workflow, dependency files, project metadata, and Git ignore rules. It does not contain implementation code or the virtual environment.
