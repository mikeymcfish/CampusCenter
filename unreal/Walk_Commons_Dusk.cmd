@echo off
start "" "C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe" "%~dp0unreal_project\CampusCenter.uproject" /Game/Campus/Maps/CampusCenter_Dusk_ArchitectFinishes_v03 -game -windowed -ResX=1920 -ResY=1080 -DDC=CommonsLocal -ShaderWorkingDir="%~dp0unreal_project\Intermediate\ShaderWork"
