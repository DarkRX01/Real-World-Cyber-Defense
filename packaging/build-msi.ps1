# Build MSI with WiX Toolset. Install: https://wixtoolset.org/
# Run from repo root: .\packaging\build-msi.ps1
$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Resolve-Path (Join-Path $scriptDir "..")

# Build exe first if missing
$exe = Join-Path $root "dist\CyberDefense\CyberDefense.exe"
if (-not (Test-Path $exe)) {
    Set-Location $root
    python build-safe-exe.py
}

$wixDir = Join-Path $scriptDir "wix"
$candle = "candle.exe"
$light = "light.exe"
# WiX typically in Program Files
$wixPath = "${env:ProgramFiles(x86)}\WiX Toolset v3.11\bin"
if (-not (Test-Path (Join-Path $wixPath $candle))) {
    $wixPath = "$env:ProgramFiles\WiX Toolset v3.11\bin"
}
if (-not (Test-Path (Join-Path $wixPath $candle))) {
    Write-Host "WiX Toolset not found. Install from https://wixtoolset.org/"
    exit 1
}

Set-Location $wixDir
& (Join-Path $wixPath $candle) CyberDefense.wxs -out (Join-Path $wixDir "CyberDefense.wixobj")
& (Join-Path $wixPath $light) CyberDefense.wixobj -out (Join-Path $root "dist\CyberDefense-Setup.msi")
Write-Host "MSI: $root\dist\CyberDefense-Setup.msi"
