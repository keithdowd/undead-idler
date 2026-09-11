from pathlib import Path


README = Path(__file__).parents[1] / "README.md"


def test_user_documentation_covers_mvp_operation():
    documentation = README.read_text(encoding="utf-8")

    for required_text in (
        "dist\\UndeadIdler.exe",
        "`Start`",
        "`Stop`",
        "`Settings`",
        "`About`",
        "`Exit`",
        "1 through 10",
        "default interval is 5 minutes",
        "F15",
        "Scroll Lock",
        "Status",
        "last successful keypress",
        "Smart Mode is deferred",
        "Windows 10 remains unverified",
        "does not directly set or control Teams or Outlook presence",
        "does not prevent the computer from sleeping",
    ):
        assert required_text in documentation


def test_user_documentation_does_not_describe_deferred_smart_mode_as_available():
    documentation = README.read_text(encoding="utf-8")

    assert "Smart Mode is deferred from release 0.2.0 and is not available" in documentation
