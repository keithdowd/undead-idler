param(
    [string]$PackageDirectory = ".\dist\UndeadIdler"
)

$package = (Resolve-Path $PackageDirectory).Path
$executable = Join-Path $package "UndeadIdler.exe"
$internal = Join-Path $package "_internal"
$requiredFiles = @(
    $executable,
    (Join-Path $internal "python313.dll"),
    (Join-Path $internal "assets\icons\undead-idler.ico"),
    (Join-Path $internal "assets\icons\undead-idler-running.ico"),
    (Join-Path $internal "assets\icons\undead-idler-error.ico")
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
        throw "Required packaged file is missing: $file"
    }
}

$process = Start-Process -FilePath $executable -WorkingDirectory $package -PassThru
try {
    Start-Sleep -Seconds 3
    if ($process.HasExited) {
        throw "Packaged application exited during launch validation with code $($process.ExitCode)."
    }
    Write-Output "Folder package launched successfully: $executable"
}
finally {
    $process.Refresh()
    if (-not $process.HasExited) {
        Stop-Process -Id $process.Id -Force
    }
}
