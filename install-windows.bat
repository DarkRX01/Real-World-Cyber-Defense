@echo off
REM Real-World Cyber Defense - Windows Installer
REM Downloads Python, PyQt5, and sets up the desktop security app

setlocal enabledelayedexpansion
title Cyber Defense - Windows Installer

:: Check if Python is installed
echo.
echo Checking for Python installation...
python --version >nul 2>&1

if errorlevel 1 (
    echo.
    echo ❌ Python 3 is not installed!
    echo.
    echo 📥 Downloading Python 3.11...
    
    :: Download Python installer
    powershell -Command "(New-Object System.Net.ServicePointManager).SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; (New-Object System.Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe', '%TEMP%\python-installer.exe')"
    
    echo.
    echo ⚙️ Installing Python...
    start /wait %TEMP%\python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    
    if errorlevel 1 (
        echo ❌ Python installation failed. Please install Python 3.9+ manually from https://www.python.org
        pause
        exit /b 1
    )
) else (
    for /f "tokens=*" %%i in ('python --version') do set PYTHON_VER=%%i
    echo ✅ Found Python: !PYTHON_VER!
)

:: Install required packages
echo.
echo 📦 Installing required packages...
echo   - PyQt5 (GUI framework)
echo   - requests (HTTP library)
echo   - pyperclip (Clipboard access)

python -m pip install --quiet --upgrade pip
python -m pip install --quiet PyQt5 requests pyperclip

if errorlevel 1 (
    echo ❌ Package installation failed
    pause
    exit /b 1
) else (
    echo ✅ All packages installed successfully
)

:: Check for Chrome
echo.
echo 🌐 Checking for Chrome...
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    echo ✅ Chrome found at: C:\Program Files\Google\Chrome\Application\chrome.exe
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    echo ✅ Chrome found at: C:\Program Files (x86)\Google\Chrome\Application\chrome.exe
) else (
    echo ⚠️ Chrome not found. The app works best with Chrome/Chromium.
    echo 📥 Download from: https://www.google.com/chrome/
)

:: Create desktop shortcut
echo.
echo 📌 Creating desktop shortcut...

set DESKTOP=%USERPROFILE%\Desktop
set APP_DIR=%USERPROFILE%\.cyber-defense
set SHORTCUT=%DESKTOP%\Cyber Defense.lnk

mkdir "%APP_DIR%" 2>nul

:: Create VBS script to make shortcut (since PowerShell can be slow)
powershell -Command "
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('%DESKTOP%\Cyber Defense.lnk')
$Shortcut.TargetPath = 'python.exe'
$Shortcut.Arguments = '-m cyber_defense.app_main'
$Shortcut.WorkingDirectory = '%APP_DIR%'
$Shortcut.IconLocation = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
$Shortcut.Save()
"

echo ✅ Desktop shortcut created

:: Setup complete
echo.
echo ================================================
echo   ✅ INSTALLATION COMPLETE!
echo ================================================
echo.
echo 🚀 To start Cyber Defense:
echo    1. Double-click the "Cyber Defense" shortcut on your Desktop
echo    2. Or run: python -m cyber_defense.app_main
echo.
echo 🔧 Features:
echo    ✓ Real-time URL scanning
echo    ✓ Phishing detection
echo    ✓ Tracker blocking
echo    ✓ Download protection
echo    ✓ Background monitoring
echo    ✓ System tray integration
echo.
echo ⚙️ First Launch Tips:
echo    - Check Settings to enable/disable features
echo    - Background service is optional
echo    - Enable "Auto-start on boot" in settings if desired
echo.
echo 📖 Documentation:
echo    - See README.md for detailed guide
echo    - Check GETTING_STARTED.md for setup
echo.
echo ================================================
echo.
pause
