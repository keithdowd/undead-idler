from pathlib import Path

from PySide6.QtGui import QImage, QImageReader


ICON_DIR = Path(__file__).parents[1] / "assets" / "icons"
SIZES = (16, 20, 24, 32, 48, 64, 128, 256)
STATES = ("stopped", "running", "error")


def test_each_state_has_svg_png_and_ico_assets():
    for state in STATES:
        assert (ICON_DIR / f"undead-idler-{state}.svg").is_file()
        assert (ICON_DIR / f"undead-idler-{state}.ico").is_file()
        for size in SIZES:
            image = QImage(str(ICON_DIR / f"undead-idler-{state}-{size}.png"))
            assert not image.isNull()
            assert image.size().width() == size
            assert image.size().height() == size


def test_ico_assets_include_standard_windows_sizes():
    for state in STATES:
        reader = QImageReader(str(ICON_DIR / f"undead-idler-{state}.ico"))
        assert reader.canRead()
        image = reader.read()
        assert image.width() in (16, 20, 24, 32)
        assert image.width() == image.height()


def test_default_icon_is_the_stopped_treatment():
    assert (
        ICON_DIR / "undead-idler.ico"
    ).read_bytes() == (ICON_DIR / "undead-idler-stopped.ico").read_bytes()
