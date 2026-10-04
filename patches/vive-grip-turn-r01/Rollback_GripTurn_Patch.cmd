@echo off
cd /d "%~dp0"
"%~dp0InstallGripTurnPatch.exe" rollback "%~dp0"
if errorlevel 1 echo Patch stopped. Read the message above; no system settings were changed.
pause
