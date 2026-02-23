@echo off
:: Cyber Defense - System Cleaner
:: Cleans temp files, Windows Update cache, Recycle Bin.
:: Run as Administrator for full cleanup (app requests elevation automatically).

:: Admin check: net session works on all Windows editions
net session >nul 2>&1
if %errorlevel% NEQ 0 (
    echo Requesting Administrator rights...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b 0
)

echo ====================================
echo   CYBER DEFENSE - SYSTEM CLEANER
echo ====================================
echo.

:: Clean user temp folder (always works)
echo [1/5] Cleaning user temp files (%TEMP%)...
if exist "%TEMP%" (
    del /f /s /q "%TEMP%\*" 2>nul
    for /d %%D in ("%TEMP%\*") do rd /s /q "%%D" 2>nul
    echo   Done.
) else (
    echo   Folder not found.
)

:: Clean Windows temp folder (needs admin)
echo [2/5] Cleaning Windows temp (C:\Windows\Temp)...
if exist "C:\Windows\Temp" (
    del /f /s /q "C:\Windows\Temp\*" 2>nul
    for /d %%D in ("C:\Windows\Temp\*") do rd /s /q "%%D" 2>nul
    echo   Done.
) else (
    echo   Skipped (admin required).
)

:: Windows Update cache
echo [3/5] Clearing Windows Update cache...
net stop wuauserv >nul 2>&1
if exist "C:\Windows\SoftwareDistribution\Download" (
    rd /s /q "C:\Windows\SoftwareDistribution\Download" 2>nul
    echo   Done.
)
net start wuauserv >nul 2>&1

:: Empty Recycle Bin via PowerShell
echo [4/5] Emptying Recycle Bin...
powershell -Command "Clear-RecycleBin -Force -ErrorAction SilentlyContinue" 2>nul
echo   Done.

:: Browser caches (optional - user folders only)
echo [5/5] Clearing browser temp (if present)...
if exist "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache" (
    rd /s /q "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache" 2>nul
)
if exist "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache" (
    rd /s /q "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache" 2>nul
)
echo   Done.

echo.
echo ====================================
echo   Cleanup Complete!
echo ====================================
echo.
pause
