; NSIS installer for Cyber Defense v3.0.0
; Created automatically — run with makensis.exe

!define APP_NAME "Cyber Defense"
!define APP_VERSION "3.0.0"
!define EXE_NAME "CyberDefense.exe"
!define OUTFILE "${APP_NAME}-setup-${APP_VERSION}.exe"

Name "${APP_NAME} ${APP_VERSION}"
OutFile "${OUTFILE}"
InstallDir "$PROGRAMFILES\\${APP_NAME}"
RequestExecutionLevel admin

Page directory
Page instfiles

Section "Install"
    SetOutPath "$INSTDIR"
    ; Copy main EXE and uninstaller helpers
    File "..\\dist\\${EXE_NAME}"
    ; include optional uninstaller scripts if present
    ; these will be embedded into installer if they exist in repo
    File "..\\uninstall.bat"
    File "..\\uninstall.py"

    ; Desktop shortcut
    CreateShortCut "$DESKTOP\\${APP_NAME}.lnk" "$INSTDIR\\${EXE_NAME}"

    ; Add uninstall entry in Add/Remove Programs
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "DisplayName" "${APP_NAME} ${APP_VERSION}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "UninstallString" "$INSTDIR\\uninstall.bat"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "DisplayIcon" "$INSTDIR\\${EXE_NAME}"
SectionEnd

Section "Uninstall"
    ; Attempt best-effort cleanup
    Delete "$INSTDIR\\${EXE_NAME}"
    Delete "$INSTDIR\\uninstall.bat"
    Delete "$INSTDIR\\uninstall.py"
    Delete "$DESKTOP\\${APP_NAME}.lnk"
    RMDir "$INSTDIR"
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}"
SectionEnd
