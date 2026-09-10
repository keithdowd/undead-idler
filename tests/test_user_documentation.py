from pathlib import Path


README = Path(__file__).parents[1] / "README.md"


def test_user_documentation_covers_mvp_operation():
    documentation = README.read_text(encoding="utf-8")

    for required_text in (
        "dist\\UndeadIdler.exe",
        "`Start`",
        "`Stop`",
        "`Settings`",
        "`Exit`",
        "1 through 10",
        "default interval is 5 minutes",
        "F15",
        "last successful keypress",
        "does not directly set or control Teams or Outlook presence",
        "does not prevent the computer from sleeping",
    ):
        assert required_text in documentation
