@echo off
REM ============================================================
REM  CYBER DEFENSE - WINDOWS INSTALLER
REM  Just double-click this file and you're done!
REM ============================================================

setlocal enabledelayedexpansion
title Installing Cyber Defense...

REM Hide this window after starting
powershell -Command "
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::UTF8
$console = [Console]::Out
Write-Output 'Cyber Defense: Installing...'
" > nul 2>&1

REM Check and install Python if needed
python --version >nul 2>&1
if errorlevel 1 (
    REM Python not installed - download silently
    powershell -NoProfile -Command "
        $ProgressPreference = 'SilentlyContinue'
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Write-Host 'Downloading Python 3.11...' -ForegroundColor Green
        (New-Object System.Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe', '$env:TEMP\python-setup.exe')
        Write-Host 'Installing Python...' -ForegroundColor Green
        Start-Process '$env:TEMP\python-setup.exe' -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait
        Remove-Item '$env:TEMP\python-setup.exe' -Force -ErrorAction SilentlyContinue
        Write-Host 'Python installed!' -ForegroundColor Green
    "
) else (
    powershell -NoProfile -Command "Write-Host 'Python found!' -ForegroundColor Green"
)

REM Install packages
powershell -NoProfile -Command "
    Write-Host 'Installing packages...' -ForegroundColor Green
    python -m pip install --quiet --no-cache-dir PyQt5 requests pyperclip | Out-Null
    Write-Host 'Ready to go!' -ForegroundColor Green
    Write-Host 'Launching Cyber Defense...' -ForegroundColor Cyan
    Start-Process 'python' -ArgumentList 'app_main.py' -WindowStyle Hidden
    Start-Sleep -Seconds 2
"

REM Close this window
exit /b 0
