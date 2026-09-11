from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]


def test_release_checklist_and_metadata_exist():
    checklist = (PROJECT_ROOT / "docs" / "releases" / "0.1.0" / "RELEASE_CHECKLIST.md").read_text(
        encoding="utf-8"
    )
    metadata = (PROJECT_ROOT / "release" / "BUILD_METADATA.md").read_text(
        encoding="utf-8"
    )

    assert "release/UndeadIdler-0.1.0.exe" in checklist
    assert "Full automated suite passes" in checklist
    assert "SHA-256" in metadata
    assert "PyInstaller: `6.21.0`" in metadata


def test_archived_release_binary_matches_metadata_hash():
    binary = PROJECT_ROOT / "release" / "UndeadIdler-0.1.0.exe"
    metadata = (PROJECT_ROOT / "release" / "BUILD_METADATA.md").read_text(
        encoding="utf-8"
    )

    assert binary.is_file()
    expected_hash = next(
        line.split("`", 2)[1]
        for line in metadata.splitlines()
        if line.startswith("- SHA-256:")
    )
    import hashlib

    actual_hash = hashlib.sha256(binary.read_bytes()).hexdigest().upper()
    assert actual_hash == expected_hash
