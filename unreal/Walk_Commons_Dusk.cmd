@echo off
start "" "C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe" "%~dp0unreal_project\CampusCenter.uproject" /Game/Campus/Maps/CampusCenter_StandardAssets_v07 -DisablePlugins=MetaHumanCrowdContent -game -fullscreen -ResX=1920 -ResY=1080 -ExecCmds="r.ScreenPercentage 50,stat fps" -DDC=CommonsLocal -ShaderWorkingDir="%~dp0unreal_project\Intermediate\ShaderWork"

