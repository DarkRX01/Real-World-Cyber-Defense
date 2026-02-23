@echo off
REM Build helper for NSIS installer (Windows)
REM Usage: run this from the project root (it will call makensis if installed)

setlocal
IF NOT EXIST "%~dp0..\dist\CyberDefense.exe" (
    echo dist\CyberDefense.exe not found. Build the EXE first.
    exit /b 1
)

where makensis >nul 2>&1
if %errorlevel% neq 0 (
    echo makensis (NSIS) not found in PATH. Install NSIS from https://nsis.sourceforge.io/Download and add makensis to PATH.
    pause
    exit /b 1
)

echo Building NSIS installer...
makensis "build\\CyberDefense-installer.nsi"
if %errorlevel% neq 0 (
    echo NSIS build failed.
    exit /b 1
)

echo Installer build finished.
pause
endlocal
