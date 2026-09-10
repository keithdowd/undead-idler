from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]
SPEC_PATH = PROJECT_ROOT / "packaging" / "undead_idler.spec"
BUILD_SCRIPT_PATH = PROJECT_ROOT / "packaging" / "build_folder.ps1"


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
