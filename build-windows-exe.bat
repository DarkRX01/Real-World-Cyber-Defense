@echo off
REM Real-World Cyber Defense - Windows Installer Builder
REM This creates a ready-to-distribute installer for Windows

setlocal enabledelayedexpansion
title Cyber Defense - Windows Installer Builder

echo.
echo ================================================
echo   Cyber Defense - Build Windows Installer
echo ================================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed!
    echo Please install Python 3.9+ from https://www.python.org
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Install PyInstaller
echo 📦 Installing PyInstaller...
python -m pip install --quiet pyinstaller PyQt5 requests pyperclip

if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed
echo.

REM Build EXE
echo 🔨 Building Windows EXE...
echo This may take a few minutes...
echo.

python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name CyberDefense ^
    --icon=NONE ^
    --add-data "requirements.txt:." ^
    --distpath "./dist" ^
    --buildpath "./build" ^
    --specpath "." ^
    --noconfirm ^
    --clean ^
    app_main.py

if errorlevel 1 (
    echo ❌ Build failed
    echo Check error messages above
    pause
    exit /b 1
)

echo.
echo ================================================
echo   ✅ BUILD SUCCESSFUL!
echo ================================================
echo.
echo 📁 Executable location:
echo    %CD%\dist\CyberDefense.exe
echo.
echo 🚀 Next steps:
echo    1. Test: dist\CyberDefense.exe
echo    2. Share: Upload dist\CyberDefense.exe to GitHub Releases
echo    3. Users can download and run directly!
echo.
echo 📊 File info:
for %%A in (dist\CyberDefense.exe) do (
    echo    Size: %%~zA bytes
)
echo.
echo ================================================
echo.
pause
