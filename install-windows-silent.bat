@echo off
REM Cyber Defense - Silent Windows Installer v2.0
REM Ultra-fast, completely silent installation - no terminal windows shown
REM Downloads everything automatically and starts the app

setlocal enabledelayedexpansion
cd /d "%~dp0"

:: Suppress all output and window displays
powershell -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Application]::EnableVisualStyles()" 2>nul

:: Check if Python exists silently
python --version >nul 2>&1
if errorlevel 1 (
    REM Python not found - download and install silently
    echo Downloading Python...
    powershell -NoProfile -Command "
        $ProgressPreference = 'SilentlyContinue'
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        (New-Object System.Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe', '%TEMP%\py-setup.exe')
    " 2>nul
    
    REM Install Python silently
    %TEMP%\py-setup.exe /quiet InstallAllUsers=1 PrependPath=1 >nul 2>&1
    
    REM Wait for Python installation
    timeout /t 5 /nobreak >nul 2>&1
    del %TEMP%\py-setup.exe >nul 2>&1
)

REM Install packages silently
python -m pip install --quiet --no-cache-dir PyQt5 requests pyperclip >nul 2>&1

REM Start the app
echo Starting Cyber Defense...
python app_main.py
