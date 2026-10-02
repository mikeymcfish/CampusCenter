@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\Run-CampusCenter.ps1" -Build Desktop %*
set "CampusCenterExit=%ERRORLEVEL%"
if not "%CampusCenterExit%"=="0" pause
exit /b %CampusCenterExit%
