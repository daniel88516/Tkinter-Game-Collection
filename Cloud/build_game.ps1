$ErrorActionPreference = 'Continue'

$projectRoot = [System.IO.Path]::GetFullPath($PSScriptRoot)
$stagingBuild = Join-Path $projectRoot 'build.new'
$stagingDist = Join-Path $projectRoot 'dist.new'
$finalBuild = Join-Path $projectRoot 'build'
$finalDist = Join-Path $projectRoot 'dist'

function Find-UsablePython {
    $candidates = [System.Collections.Generic.List[string]]::new()

    $localPythonRoot = Join-Path $env:LOCALAPPDATA 'Programs\Python'
    if (Test-Path -LiteralPath $localPythonRoot) {
        Get-ChildItem -LiteralPath $localPythonRoot -Directory -Filter 'Python3*' -ErrorAction SilentlyContinue |
            Sort-Object Name -Descending |
            ForEach-Object { $candidates.Add((Join-Path $_.FullName 'python.exe')) }
    }

    Get-Command python.exe -All -ErrorAction SilentlyContinue |
        ForEach-Object { $candidates.Add($_.Source) }

    foreach ($candidate in ($candidates | Select-Object -Unique)) {
        if (-not (Test-Path -LiteralPath $candidate)) {
            continue
        }

        try {
            & $candidate -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' *> $null
            if ($LASTEXITCODE -eq 0) {
                return $candidate
            }
        }
        catch {
            continue
        }
    }

    return $null
}

function Remove-StagingDirectory([string] $path) {
    $resolved = [System.IO.Path]::GetFullPath($path)
    $expectedPrefix = $projectRoot.TrimEnd('\') + '\'
    if (-not $resolved.StartsWith($expectedPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to remove a directory outside the project: $resolved"
    }

    if (Test-Path -LiteralPath $resolved) {
        Remove-Item -LiteralPath $resolved -Recurse -Force -ErrorAction Stop
    }
}

function Invoke-Checked([string] $description, [scriptblock] $command) {
    & $command
    if ($LASTEXITCODE -ne 0) {
        throw "$description failed with exit code $LASTEXITCODE."
    }
}

try {
    Set-Location -LiteralPath $projectRoot

    $python = Find-UsablePython
    if (-not $python) {
        Write-Host '[INFO] Python was not found. Installing Python 3.12 with winget...'
        $winget = Get-Command winget.exe -ErrorAction SilentlyContinue
        if (-not $winget) {
            throw 'winget is unavailable. Install App Installer from Microsoft Store and try again.'
        }

        Invoke-Checked 'Python installation' {
            & $winget.Source install --id Python.Python.3.12 --exact --scope user `
                --accept-package-agreements --accept-source-agreements
        }

        $python = Find-UsablePython
        if (-not $python) {
            throw 'Python was installed but python.exe could not be located. Run the batch file again.'
        }
    }

    Write-Host "[INFO] Using Python: $python"
    & $python --version

    & $python -m pip --version *> $null
    if ($LASTEXITCODE -ne 0) {
        Write-Host '[INFO] Installing pip...'
        Invoke-Checked 'pip installation' { & $python -m ensurepip --upgrade }
    }

    & $python -c 'import PyInstaller, requests, PIL' *> $null
    if ($LASTEXITCODE -ne 0) {
        Write-Host '[INFO] Installing PyInstaller, requests, and Pillow...'
        Invoke-Checked 'Python dependency installation' {
            & $python -m pip install --disable-pip-version-check pyinstaller requests pillow
        }
    }

    Invoke-Checked 'Python dependency check' {
        & $python -c 'import sqlite3, tkinter, tkinter.simpledialog, PyInstaller, requests, PIL'
    }

    $imageSuffix = [string][char]0x5716 + [char]0x7247
    $gameMenuImages = 'GameMenu' + $imageSuffix
    $threeHallImages = 'ThreeHall' + $imageSuffix
    $zombieImages = 'Zombie' + $imageSuffix

    $dataItems = @(
        @{ Source = $gameMenuImages; Destination = $gameMenuImages },
        @{ Source = 'Images'; Destination = 'Images' },
        @{ Source = $threeHallImages; Destination = $threeHallImages },
        @{ Source = $zombieImages; Destination = $zombieImages },
        @{ Source = 'minesweeper.db'; Destination = '.' },
        @{ Source = 'zombie_rand.db'; Destination = '.' }
    )

    foreach ($item in $dataItems) {
        $sourcePath = Join-Path $projectRoot $item.Source
        if (-not (Test-Path -LiteralPath $sourcePath)) {
            throw "Required game resource is missing: $sourcePath"
        }
    }

    Remove-StagingDirectory $stagingBuild
    Remove-StagingDirectory $stagingDist

    $arguments = @(
        '-m', 'PyInstaller',
        '--noconfirm',
        '--clean',
        '--onefile',
        '--windowed',
        '--hidden-import=sqlite3',
        '--hidden-import=requests',
        '--hidden-import=tkinter.simpledialog',
        '--workpath', $stagingBuild,
        '--distpath', $stagingDist,
        '--specpath', $stagingBuild
    )

    foreach ($item in $dataItems) {
        $sourcePath = Join-Path $projectRoot $item.Source
        $arguments += @('--add-data', "$sourcePath;$($item.Destination)")
    }
    $arguments += (Join-Path $projectRoot 'GameMenu.py')

    Write-Host '[INFO] Building GameMenu.exe...'
    Invoke-Checked 'PyInstaller build' { & $python @arguments }

    $newExe = Join-Path $stagingDist 'GameMenu.exe'
    if (-not (Test-Path -LiteralPath $newExe)) {
        throw "PyInstaller completed but did not create $newExe"
    }

    Get-Process -Name GameMenu -ErrorAction SilentlyContinue | Stop-Process -Force
    Remove-StagingDirectory $finalBuild
    Remove-StagingDirectory $finalDist
    Move-Item -LiteralPath $stagingBuild -Destination $finalBuild -ErrorAction Stop
    Move-Item -LiteralPath $stagingDist -Destination $finalDist -ErrorAction Stop

    $finalExe = Join-Path $finalDist 'GameMenu.exe'
    Write-Host "[OK] Build completed: $finalExe" -ForegroundColor Green
    Start-Process -FilePath $finalExe -WorkingDirectory $projectRoot
    exit 0
}
catch {
    Write-Host ''
    Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red
    Write-Host 'The previous dist directory was not removed unless a new executable was built.'
    exit 1
}
