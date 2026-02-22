@echo off
REM Cyber Defense uninstaller launcher (Windows).
REM Tries to use pythonw.exe to avoid a console window; falls back to python.

setlocal
set APP_DIR=%~dp0

if exist "%APP_DIR%pythonw.exe" (
    start "" "%APP_DIR%pythonw.exe" "%APP_DIR%uninstall.py"
) else (
    start "" pythonw.exe "%APP_DIR%uninstall.py"
)

endlocal

