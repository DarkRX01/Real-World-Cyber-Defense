@echo off
REM Cyber Defense - Installation Script
REM Simple, reliable, no encoding issues
REM Just double-click this file and it handles everything

cd /d "%~dp0"
cls

echo ================================================================
echo                  CYBER DEFENSE SETUP
echo ================================================================
echo.

REM Check if Python exists
python --version >nul 2>&1
if errorlevel 1 (
    echo Checking for Python...
    echo Python not found. Downloading...
    
    REM Download Python silently
    powershell -Command "^
        $ProgressPreference = 'SilentlyContinue'; ^
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; ^
        (New-Object System.Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe', '%TEMP%\python-setup.exe'); ^
        Start-Process '%TEMP%\python-setup.exe' -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait; ^
        Remove-Item '%TEMP%\python-setup.exe' -Force -ErrorAction SilentlyContinue
    "
    
    echo Python installed!
) else (
    echo Python found!
)

echo.
echo Installing required packages...
python -m pip install --quiet --no-cache-dir PyQt5 requests pyperclip

echo.
echo Setup complete! Starting Cyber Defense...
echo.

REM Launch the app
start "" python app_main.py

REM Close this window
exit /b 0
