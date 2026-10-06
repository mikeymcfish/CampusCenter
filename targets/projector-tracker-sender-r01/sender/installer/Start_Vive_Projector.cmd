@echo off
powershell.exe -NoProfile -File "%~dp0ProjectorSender.ps1" -Action Launch -Mode Vive -EnableSender
if errorlevel 1 pause
