def test_package_imports():
    import undead_idler

    assert undead_idler.__name__ == "undead_idler"


def test_module_entrypoint_uses_absolute_import():
    entrypoint = (
        __import__("pathlib").Path(__file__).parents[1]
        / "src"
        / "undead_idler"
        / "__main__.py"
    )

    assert "from undead_idler.app import main" in entrypoint.read_text()
