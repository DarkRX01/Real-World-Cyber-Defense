<#
Quick cleanup script for repository artifacts.
Run from repo root in an elevated PowerShell prompt if you want to remove build artifacts, caches, and large logs.
Review before running. This will delete `dist/`, `build/release.zip`, `releases/*.zip`, and Python cache files.
#>

Write-Host "Running CyberDefense repo cleanup..." -ForegroundColor Cyan

Write-Host "Listing large files (>1 MB):" -ForegroundColor Yellow
Get-ChildItem -Path . -Recurse -File |
  Where-Object { $_.Length -gt 1MB } |
  Sort-Object Length -Descending |
  Select-Object FullName, @{n='MB';e={[math]::Round($_.Length/1MB,2)}} | Format-Table -AutoSize

Read-Host "Press Enter to continue and remove common build artifacts, or Ctrl+C to abort"

Write-Host "Removing dist/ folder..." -ForegroundColor Green
Remove-Item -Recurse -Force .\dist -ErrorAction SilentlyContinue

Write-Host "Removing build/release.zip (if present)..." -ForegroundColor Green
Remove-Item -Force .\build\release.zip -ErrorAction SilentlyContinue
Remove-Item -Force .\build\release*.zip -ErrorAction SilentlyContinue

Write-Host "Removing release archives in releases/ (if present)..." -ForegroundColor Green
Remove-Item -Force .\releases\*.zip -ErrorAction SilentlyContinue

Write-Host "Removing Python caches (__pycache__ and .pyc files)..." -ForegroundColor Green
Get-ChildItem -Path . -Recurse -Force -Include __pycache__ | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Recurse -Force -Include *.pyc | Remove-Item -Force -ErrorAction SilentlyContinue

Write-Host "Cleanup finished." -ForegroundColor Cyan
