$ErrorActionPreference='Stop'
$projectFile=Join-Path $PSScriptRoot 'unreal_project/CampusCenter.uproject'
$archiveDir=Join-Path $PSScriptRoot 'unreal_delivery'
$uat='C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/RunUAT.bat'
& $uat BuildCookRun "-project=$projectFile" -noP4 -platform=Win64 -clientconfig=Development -cook -stage -pak -archive "-archivedirectory=$archiveDir" -nocompile -nocompileeditor -installed -unattended '-unrealexe=UnrealEditor-Cmd.exe'
if($LASTEXITCODE -ne 0){throw "Unreal packaging failed with exit code $LASTEXITCODE"}
