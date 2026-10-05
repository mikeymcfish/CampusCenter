@echo off
powershell.exe -NoProfile -File "%~dp0QuestPCVR.ps1" -Action Launch %*
exit /b %errorlevel%
