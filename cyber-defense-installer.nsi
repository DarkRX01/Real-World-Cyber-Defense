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
Section "Install Python (if needed)"
  Call CheckPythonInstallation
  ${If} $PythonInstalled == "false"
    SetOutPath "$TEMP"
    
    ; Download Python 3.11
    DetailPrint "Downloading Python 3.11..."
    NSClient::http GET "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe" "$TEMP\python-installer.exe"
    
    DetailPrint "Installing Python 3.11..."
    ExecWait "$TEMP\python-installer.exe /quiet InstallAllUsers=1 PrependPath=1"
    
    DetailPrint "Cleaning up Python installer..."
    Delete "$TEMP\python-installer.exe"
  ${EndIf}
SectionEnd

Section "Install Cyber Defense Application"
  SetOutPath "$INSTDIR"
  
  DetailPrint "Copying application files..."
  
  ; Copy Python files
  File "app_main.py"
  File "threat_engine.py"
  File "background_service.py"
  File "__init__.py"
  File "requirements.txt"
  
  ; Create subdirectories if needed
  CreateDirectory "$INSTDIR\icons"
  CreateDirectory "$INSTDIR\data"
  
  ; Install Python packages
  DetailPrint "Installing required Python packages..."
  ExecWait "python -m pip install --quiet PyQt5 requests pyperclip"
  
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
  CreateShortcut "$SMPROGRAMS\$StartMenuFolder\Cyber Defense.lnk" "python.exe" "-m app_main" "$INSTDIR" 0 SW_SHOWNORMAL
  CreateShortcut "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" "$INSTDIR\Uninstall.exe" "" "" 0 SW_SHOWNORMAL
  !insertmacro MUI_STARTMENU_WRITE_END
  
  ; Create Desktop shortcut
  CreateShortcut "$DESKTOP\Cyber Defense.lnk" "python.exe" "-m app_main" "$INSTDIR" 0 SW_SHOWNORMAL
  
  DetailPrint "Shortcuts created on Desktop and Start Menu"
SectionEnd

Section "Uninstall"
  DeleteRegKey HKCU "Software\Cyber Defense"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Cyber Defense"
  
  ; Remove application files
  Delete "$INSTDIR\app_main.py"
  Delete "$INSTDIR\threat_engine.py"
  Delete "$INSTDIR\background_service.py"
  Delete "$INSTDIR\__init__.py"
  Delete "$INSTDIR\requirements.txt"
  Delete "$INSTDIR\Uninstall.exe"
  
  RMDir "$INSTDIR\icons"
  RMDir "$INSTDIR\data"
  RMDir "$INSTDIR"
  
  ; Remove shortcuts
  RMDir /r "$SMPROGRAMS\Cyber Defense"
  Delete "$DESKTOP\Cyber Defense.lnk"
  
  DetailPrint "Cyber Defense has been uninstalled"
SectionEnd

; Function to check if Python is installed
Function CheckPythonInstallation
  ClearErrors
  EnumRegKey $0 HKLM "Software\Python\PythonCore" 0
  ${If} ${Errors}
    ; Check 64-bit Python
    SetRegView 64
    EnumRegKey $0 HKLM "Software\Python\PythonCore" 0
    ${If} ${Errors}
      StrCpy $PythonInstalled "false"
    ${Else}
      StrCpy $PythonInstalled "true"
      DetailPrint "Python is already installed"
    ${EndIf}
  ${Else}
    StrCpy $PythonInstalled "true"
    DetailPrint "Python is already installed"
  ${EndIf}
FunctionEnd

Function .onInit
  SetShellVarContext all
  ${If} ${RunningX64}
    SetRegView 64
  ${EndIf}
FunctionEnd
