@echo off
REM ========================================
REM Real-World Cyber Defense Extension Setup
REM ========================================

setlocal enabledelayedexpansion

echo.
echo ========================================
echo Real-World Cyber Defense Installer
echo ========================================
echo.

REM Check if Chrome is installed
echo Checking for Google Chrome...
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    echo ✓ Chrome found!
    set CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    echo ✓ Chrome found!
    set CHROME_PATH=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe
) else (
    echo ✗ Chrome not found. Please install Google Chrome first:
    echo   Download from: https://www.google.com/chrome/
    pause
    exit /b 1
)

REM Create installation directory
echo.
echo Creating installation directory...
set INSTALL_DIR=%USERPROFILE%\AppData\Local\CyberDefenseExtension

if not exist "!INSTALL_DIR!" (
    mkdir "!INSTALL_DIR!"
    echo ✓ Directory created: !INSTALL_DIR!
) else (
    echo ✓ Directory exists: !INSTALL_DIR!
)

REM Look for the zip file
echo.
echo Looking for extension zip file...

if exist "cyber-defense-extension-v1.0.0.zip" (
    set ZIP_FILE=%CD%\cyber-defense-extension-v1.0.0.zip
    echo ✓ Found: !ZIP_FILE!
) else if exist "%~dp0cyber-defense-extension-v1.0.0.zip" (
    set ZIP_FILE=%~dp0cyber-defense-extension-v1.0.0.zip
    echo ✓ Found: !ZIP_FILE!
) else (
    echo ✗ ZIP file not found!
    echo Please make sure cyber-defense-extension-v1.0.0.zip is in:
    echo   - Current directory
    echo   - Same folder as this setup script
    echo.
    echo Download from: https://github.com/DarkRX01/Real-World-Cyber-Defense/releases
    pause
    exit /b 1
)

REM Extract the zip file
echo.
echo Extracting files...
cd /d "!INSTALL_DIR!"

REM Use PowerShell to extract since it's built-in
powershell -NoProfile -Command "Expand-Archive -Path '!ZIP_FILE!' -DestinationPath '!INSTALL_DIR!' -Force" >nul 2>&1

if errorlevel 1 (
    echo ✗ Extraction failed!
    echo Please ensure the ZIP file is valid.
    pause
    exit /b 1
) else (
    echo ✓ Files extracted successfully!
)

REM Create a shortcut with instructions
echo.
echo Creating desktop shortcut...

set SHORTCUT=%USERPROFILE%\Desktop\Cyber Defense Extension.txt
(
    echo.
    echo ===== CYBER DEFENSE EXTENSION INSTALLATION COMPLETE =====
    echo.
    echo NEXT STEPS:
    echo.
    echo 1. Open Google Chrome
    echo.
    echo 2. Type this in the address bar and press Enter:
    echo    chrome://extensions/
    echo.
    echo 3. Turn ON "Developer mode" (toggle at top-right)
    echo.
    echo 4. Click "Load unpacked"
    echo.
    echo 5. Navigate to:
    echo    %INSTALL_DIR%
    echo.
    echo 6. Click "Select Folder"
    echo.
    echo 7. Done! The extension is now active!
    echo.
    echo TROUBLESHOOTING:
    echo If you need help, visit:
    echo https://github.com/DarkRX01/Real-World-Cyber-Defense/issues
    echo.
    echo DOCUMENTATION:
    echo Installation guide: %INSTALL_DIR%\FIRST-TIME-USERS.md
    echo Troubleshooting: %INSTALL_DIR%\TROUBLESHOOTING.md
    echo.
) > "!SHORTCUT!"

echo ✓ Shortcut created on Desktop: Cyber Defense Extension.txt

REM Open the installation guide in default browser
echo.
echo Opening installation guide...

if exist "!INSTALL_DIR!\FIRST-TIME-USERS.md" (
    start "" "!INSTALL_DIR!\FIRST-TIME-USERS.md"
    timeout /t 2 /nobreak >nul
)

REM Display final instructions
cls
echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo The extension has been installed to:
echo !INSTALL_DIR!
echo.
echo NEXT STEPS:
echo.
echo 1. Open Google Chrome
echo.
echo 2. Go to: chrome://extensions/
echo.
echo 3. Enable "Developer mode" (top right)
echo.
echo 4. Click "Load unpacked"
echo.
echo 5. Select this folder:
echo    !INSTALL_DIR!
echo.
echo 6. Your extension is now active!
echo.
echo For questions, visit:
echo https://github.com/DarkRX01/Real-World-Cyber-Defense/issues
echo.
echo Press any key to close this window...
pause >nul
