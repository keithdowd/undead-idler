param(
    [string]$Python = ".\.venv\Scripts\python.exe"
)

& $Python -m PyInstaller --noconfirm --clean packaging\undead_idler_onefile.spec
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
