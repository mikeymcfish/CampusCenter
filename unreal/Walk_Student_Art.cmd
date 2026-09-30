@echo off
setlocal
set "EDITOR=%UNREAL_EDITOR%"
if not defined EDITOR set "EDITOR=C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe"
if not exist "%EDITOR%" (
  echo Unreal Engine 5.8.2 is required. Set UNREAL_EDITOR for a custom install.
  pause
  exit /b 1
)
if not exist "%~dp0unreal_project\Content\Campus\Maps\CampusCenter_StudentArt_v01.umap" (
  echo Run Apply_Student_Art.cmd first and check student_art_v01\apply_report.json.
  pause
  exit /b 1
)
start "" "%EDITOR%" "%~dp0unreal_project\CampusCenter.uproject" /Game/Campus/Maps/CampusCenter_StudentArt_v01 -game -windowed -ResX=1920 -ResY=1080 -DDC=CommonsLocal -ShaderWorkingDir="%~dp0unreal_project\Intermediate\ShaderWork"
