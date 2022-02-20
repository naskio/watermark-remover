# NSIS Script File (.nsi) is config to build the .exe installer (Windows only)
; install files, creates desktop shortcuts and an entry in the start menu, adding Uninstall.exe.

;--------------------------------
;Include Modern UI

  !include "MUI2.nsh"

;--------------------------------
;General

  ;Name and file
  Name "WatermarkRemover"
  OutFile "WatermarkRemover-installer.exe"
  Unicode True
  !define NAME "WatermarkRemover"

  ;Default installation folder
  InstallDir "$PROGRAMFILES\${NAME}"

  ;Get installation folder from registry if available
  InstallDirRegKey HKCU "Software\${NAME}" ""

  ;Request root privileges
  ;RequestExecutionLevel admin

  ;Others
  ;ShowInstDetails "nevershow"
  ;ShowUninstDetails "nevershow"
  SetCompressor "lzma"
  # zlib|bzip2|lzma

;--------------------------------
;Interface Settings

; icon
  !define MUI_ICON "resources\icon.ico"
  !define MUI_UNICON "resources\icon.ico"

;--------------------------------
;Pages

  !define MUI_PAGE_CUSTOMFUNCTION_SHOW MyWelcomeShowCallback
  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_LICENSE "LICENSE"
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES

;--------------------------------
;Languages

  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

Section "Main Section" SecMain

  SetOutPath "$INSTDIR"

  # File "LICENSE"
  # File "dist\${NAME}.exe"
  # File /r "resources\*"

  ;Adding files
  File "LICENSE"
  File /r "dist\${NAME}\*"


  ;create desktop shortcut
  CreateShortCut "$DESKTOP\${NAME}.lnk" "$INSTDIR\${NAME}.exe" ""

  ;create start-menu items
  CreateDirectory "$SMPROGRAMS\${NAME}"
  CreateShortCut "$SMPROGRAMS\${NAME}\Uninstall.lnk" "$INSTDIR\Uninstall.exe" "" "$INSTDIR\Uninstall.exe" 0
  CreateShortCut "$SMPROGRAMS\${NAME}\${NAME}.lnk" "$INSTDIR\${NAME}.exe" "" "$INSTDIR\${NAME}.exe" 0

  ;write uninstall information to the registry
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${NAME}" "DisplayName" "${NAME} (remove only)"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${NAME}" "UninstallString" "$INSTDIR\Uninstall.exe"

  ;Store installation folder
  WriteRegStr HKCU "Software\${NAME}" "" $INSTDIR

  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd

;--------------------------------
;Uninstaller Section

Section "Uninstall"

  ;ADD YOUR OWN FILES HERE...
  ;SetOutPath "$INSTDIR"

  ;Delete Files
  Delete "$INSTDIR\Uninstall.exe"
  RMDir /r "$INSTDIR\*"

  ;Remove the installation directory
  RMDir "$INSTDIR"

  ;Delete Start Menu Shortcuts
  Delete "$DESKTOP\${NAME}.lnk"
  Delete "$SMPROGRAMS\${NAME}\*"
  RmDir  "$SMPROGRAMS\${NAME}"

  ;Delete Uninstaller And Uninstall Registry Entries
  DeleteRegKey HKEY_LOCAL_MACHINE "SOFTWARE\${NAME}"
  DeleteRegKey HKEY_LOCAL_MACHINE "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\${NAME}"

  DeleteRegKey /ifempty HKCU "Software\${NAME}"

SectionEnd


;--------------------------------
; Custom functions

Function MyWelcomeShowCallback
  ${NSD_CreateLabel} 120u 150u 50% 12u "Developed by: GitHub@naskio"
  Pop $0
  SetCtlColors $0 "" "${MUI_BGCOLOR}"
FunctionEnd

;--------------------------------
;MessageBox Section

;Function that calls a messagebox when installation finished correctly

#Function .onInstSuccess
#  MessageBox MB_OK "You have successfully installed ${NAME}. Use the desktop icon to start the program."
#FunctionEnd

#Function un.onUninstSuccess
#  MessageBox MB_OK "You have successfully uninstalled ${NAME}."
#FunctionEnd