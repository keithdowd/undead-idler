# PyInstaller onedir configuration for the development and folder-based build.

from pathlib import Path


project_root = Path(SPECPATH).parent
source_root = project_root / "src"
icon_root = project_root / "assets" / "icons"

analysis = Analysis(
    [str(source_root / "undead_idler" / "__main__.py")],
    pathex=[str(source_root)],
    binaries=[],
    datas=[(str(icon_root), "assets/icons")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(analysis.pure)

executable = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="UndeadIdler",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_root / "undead-idler.ico"),
)

collection = COLLECT(
    executable,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="UndeadIdler",
)
