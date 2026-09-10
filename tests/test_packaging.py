from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]
SPEC_PATH = PROJECT_ROOT / "packaging" / "undead_idler.spec"
BUILD_SCRIPT_PATH = PROJECT_ROOT / "packaging" / "build_folder.ps1"
SINGLE_SPEC_PATH = PROJECT_ROOT / "packaging" / "undead_idler_onefile.spec"
SINGLE_BUILD_SCRIPT_PATH = PROJECT_ROOT / "packaging" / "build_single.ps1"
VALIDATE_SCRIPT_PATH = PROJECT_ROOT / "packaging" / "validate_folder.ps1"


def test_folder_build_configuration_exists_and_is_windowed():
    spec = SPEC_PATH.read_text(encoding="utf-8")

    assert "console=False" in spec
    assert 'name="UndeadIdler"' in spec
    assert '"assets/icons"' in spec
    assert "undead-idler.ico" in spec
    assert "COLLECT(" in spec


def test_folder_build_script_uses_project_virtual_environment():
    script = BUILD_SCRIPT_PATH.read_text(encoding="utf-8")

    assert ".venv\\Scripts\\python.exe" in script
    assert "packaging\\undead_idler.spec" in script


def test_folder_validation_script_checks_runtime_and_icons():
    script = VALIDATE_SCRIPT_PATH.read_text(encoding="utf-8")

    assert "UndeadIdler.exe" in script
    assert "python313.dll" in script
    assert "undead-idler-running.ico" in script
    assert "Start-Process" in script


def test_single_file_configuration_is_windowed_and_does_not_collect_folder():
    spec = SINGLE_SPEC_PATH.read_text(encoding="utf-8")

    assert "console=False" in spec
    assert 'name="UndeadIdler"' in spec
    assert '"assets/icons"' in spec
    assert "undead-idler.ico" in spec
    assert "COLLECT(" not in spec


def test_single_file_build_script_uses_onefile_spec():
    script = SINGLE_BUILD_SCRIPT_PATH.read_text(encoding="utf-8")

    assert ".venv\\Scripts\\python.exe" in script
    assert "packaging\\undead_idler_onefile.spec" in script
