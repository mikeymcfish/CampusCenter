@echo off
setlocal
set "EDITOR=%UNREAL_EDITOR%"
if not defined EDITOR set "EDITOR=C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe"
if not exist "%EDITOR%" (
  echo Unreal Engine 5.8.2 is required on this PC.
  echo For a custom install, set UNREAL_EDITOR to the full UnrealEditor.exe path.
  pause
  exit /b 1
)
set "PROJECT=%~dp0unreal_project\CampusCenter.uproject"
set "SOURCE=%~dp0unreal_project\Content\Campus\Maps\CampusCenter_Dusk_ArchitectFinishes_v03.umap"
if not exist "%SOURCE%" goto missing
for %%F in ("%SOURCE%") do if %%~zF LSS 1024 goto missing
if not exist "%~dp0student_art_v02\manifest.json" goto missing
echo Close other CampusCenter editor sessions before applying this update.
echo Opening Unreal to create the separate CampusCenter_StudentArt_v02 map.
echo Results: student_art_v02\apply_report.json and Unreal's Output Log.
start "" "%EDITOR%" "%PROJECT%" -ExecutePythonScript="%~dp0student_art_v02\apply_student_art.py" -DDC=CommonsLocal -ShaderWorkingDir="%~dp0unreal_project\Intermediate\ShaderWork"
exit /b 0
:missing
echo Missing map or art update files. Copy the complete update, and run git lfs pull in your cloned repository.
pause
exit /b 1
