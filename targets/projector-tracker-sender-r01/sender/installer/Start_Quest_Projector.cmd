@echo off
powershell.exe -NoProfile -File "%~dp0ProjectorSender.ps1" -Action Launch -Mode Quest -EnableSender
if errorlevel 1 pause
