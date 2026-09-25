@echo off
start "" "C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe" "%~dp0unreal_project\CampusCenter.uproject" /Game/Campus/Maps/CampusCenter_ArchitectDecals_v04 -DDC=CommonsLocal -ShaderWorkingDir="%~dp0unreal_project\Intermediate\ShaderWork"
