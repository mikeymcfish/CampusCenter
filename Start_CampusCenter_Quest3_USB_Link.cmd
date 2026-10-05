@echo off
setlocal
powershell.exe -NoProfile -File "%~dp0tools\Run-CampusCenterQuest.ps1" %*
if errorlevel 1 (
 echo Quest preparation or launch stopped. Existing installations were preserved.
 pause
)
endlocal
