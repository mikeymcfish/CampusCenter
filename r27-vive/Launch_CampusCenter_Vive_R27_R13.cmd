@echo off
cd /d "%~dp0"
start "" "%~dp0CampusCenter\Binaries\Win64\CampusCenter.exe" /Game/Campus/Maps/CampusCenter_Vive_R27_R13_Private_Review -DisablePlugins=MetaHumanCrowdContent -vr -fullscreen -ResX=1920 -ResY=1080 -ExecCmds="r.ScreenPercentage 50,stat fps"
