@echo off
setlocal
cd /d "%~dp0"
if not exist "%~dp0CampusCenter.exe" (
 echo Put this launcher inside the existing Windows build folder.
 exit /b 2
)
"%~dp0CampusCenter.exe" %*
endlocal
