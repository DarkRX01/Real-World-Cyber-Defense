@echo off
REM Cyber Defense - Simple Windows Installer
REM No confusing steps, no terminal windows, just works

setlocal enabledelayedexpansion
cd /d "%~dp0"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [*] Python not found, downloading...
    powershell -NoProfile -Command "^
        $ProgressPreference = 'SilentlyContinue'; ^
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; ^
        Write-Host '[*] Downloading Python 3.11'; ^
        (New-Object System.Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe', '%TEMP%\py-setup.exe'); ^
        Write-Host '[*] Installing Python...'; ^
        Start-Process '%TEMP%\py-setup.exe' -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait; ^
        Remove-Item '%TEMP%\py-setup.exe' -Force -ErrorAction SilentlyContinue; ^
        Write-Host '[+] Python installed'
    "
) else (
    echo [+] Python already installed
)

REM Install packages
echo [*] Installing dependencies...
python -m pip install --quiet --no-cache-dir PyQt5 requests pyperclip >nul 2>&1

echo [+] Setup complete! Starting app...
python app_main.py
exit /b 0
