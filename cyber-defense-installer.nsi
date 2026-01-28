; Real-World Cyber Defense - Windows Installer
; NSIS Installer Script
; Download NSIS: https://nsis.sourceforge.io/

!include "MUI2.nsh"
!include "x64.nsh"

; Basic Settings
Name "Real-World Cyber Defense"
OutFile "cyber-defense-installer.exe"
InstallDir "$PROGRAMFILES\Cyber Defense"
InstallDirRegKey HKCU "Software\Cyber Defense" ""

!define MUI_FINISHPAGE_RUN
!define MUI_FINISHPAGE_RUN_TEXT "Run Cyber Defense"
!define MUI_FINISHPAGE_RUN_FUNCTION LaunchApp

; Variables
Var StartMenuFolder
Var PythonInstalled
Var Python311Path

; Settings
SetCompressor /SOLID lzma
SetDatablockOptimize on
CRCCheck on
XPStyle on
ShowInstDetails show

; MUI Settings
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_STARTMENU "Cyber Defense" $StartMenuFolder
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

; Installer Sections
Section "Install Cyber Defense Application"
  SetOutPath "$INSTDIR"
  
  DetailPrint "Copying application files..."

  ; Install pre-built onedir application
  ; Build first: python build-safe-exe.py
  File /r "dist\CyberDefense\*.*"
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  ; Registry entries
  WriteRegStr HKCU "Software\Cyber Defense" "" "$INSTDIR"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Cyber Defense" "DisplayName" "Real-World Cyber Defense"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Cyber Defense" "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Cyber Defense" "InstallLocation" "$INSTDIR"
  
  DetailPrint "Installation completed successfully!"
SectionEnd

Section "Create Shortcuts"
  SetOutPath "$INSTDIR"
  
  ; Create Start Menu folder
  !insertmacro MUI_STARTMENU_WRITE_BEGIN "Cyber Defense"
  CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
  CreateShortcut "$SMPROGRAMS\$StartMenuFolder\Cyber Defense.lnk" "$INSTDIR\CyberDefense.exe" "" "$INSTDIR" 0 SW_SHOWNORMAL
  CreateShortcut "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" "$INSTDIR\Uninstall.exe" "" "" 0 SW_SHOWNORMAL
  !insertmacro MUI_STARTMENU_WRITE_END
  WriteRegStr HKCU "Software\Cyber Defense" "StartMenuFolder" "$StartMenuFolder"
  
  ; Create Desktop shortcut
  CreateShortcut "$DESKTOP\Cyber Defense.lnk" "$INSTDIR\CyberDefense.exe" "" "$INSTDIR" 0 SW_SHOWNORMAL
  
  DetailPrint "Shortcuts created on Desktop and Start Menu"
SectionEnd

Section "Uninstall"
  ReadRegStr $StartMenuFolder HKCU "Software\Cyber Defense" "StartMenuFolder"
  StrCmp $StartMenuFolder "" 0 +2
    StrCpy $StartMenuFolder "Cyber Defense"

  DeleteRegKey HKCU "Software\Cyber Defense"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Cyber Defense"
  
  ; Remove application files
  Delete "$INSTDIR\CyberDefense.exe"
  RMDir /r "$INSTDIR"
  RMDir "$INSTDIR"
  
  ; Remove shortcuts
  RMDir /r "$SMPROGRAMS\$StartMenuFolder"
  Delete "$DESKTOP\Cyber Defense.lnk"
  
  DetailPrint "Cyber Defense has been uninstalled"
SectionEnd

Function .onInit
  SetShellVarContext all
  ${If} ${RunningX64}
    SetRegView 64
  ${EndIf}
FunctionEnd

Function LaunchApp
  SetOutPath "$INSTDIR"
  Exec '"$INSTDIR\CyberDefense.exe"'
FunctionEnd
