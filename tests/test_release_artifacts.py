from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]


def test_release_checklist_and_metadata_exist():
    checklist = (PROJECT_ROOT / "docs" / "releases" / "0.1.0" / "RELEASE_CHECKLIST.md").read_text(
        encoding="utf-8"
    )
    metadata = (PROJECT_ROOT / "release" / "0.1.0" / "BUILD_METADATA.md").read_text(
        encoding="utf-8"
    )

    assert "release/0.1.0/UndeadIdler-0.1.0.exe" in checklist
    assert "Full automated suite passes" in checklist
    assert "SHA-256" in metadata
    assert "PyInstaller: `6.21.0`" in metadata


def test_archived_release_binary_matches_metadata_hash():
    binary = PROJECT_ROOT / "release" / "0.1.0" / "UndeadIdler-0.1.0.exe"
    metadata = (PROJECT_ROOT / "release" / "0.1.0" / "BUILD_METADATA.md").read_text(
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


def test_020_release_evidence_and_metadata_are_recorded_without_replacing_mvp():
    release_docs = PROJECT_ROOT / "docs" / "releases" / "0.2.0"
    checklist = (release_docs / "RELEASE_CHECKLIST.md").read_text(encoding="utf-8")
    integration = (release_docs / "QA_WINDOWS_INTEGRATION.md").read_text(encoding="utf-8")
    supported = (release_docs / "QA_SUPPORTED_WINDOWS.md").read_text(encoding="utf-8")
    metadata = (PROJECT_ROOT / "release" / "0.2.0" / "BUILD_METADATA.md").read_text(
        encoding="utf-8"
    )

    assert "release/0.2.0/UndeadIdler-0.2.0.exe" in checklist
    assert "113 tests" in checklist
    assert "F15 native injection | Pass" in integration
    assert "Scroll Lock native injection | Pass" in integration
    assert "Windows 10 | Unverified" in supported
    assert "Release: `0.2.0`" in metadata
    assert "3489EF9CA1B940DDB0F67BFBAB7C082B094F70F688538CCD3BE1D3E46524AA21" in metadata
