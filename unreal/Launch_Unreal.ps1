$ErrorActionPreference = 'Stop'
$baseDir = $PSScriptRoot
$projectDir = Join-Path $baseDir 'unreal_project'
if (-not (Test-Path -LiteralPath $projectDir)) { $projectDir = Join-Path $baseDir 'Project' }
$projectFile = Join-Path $projectDir 'CampusCenter.uproject'
$standalone = Join-Path $baseDir 'unreal_delivery\Windows\CampusCenter.exe'
if (-not (Test-Path -LiteralPath $standalone)) { $standalone = Join-Path $baseDir 'Standalone\Windows\CampusCenter.exe' }
$maps = @{ E='CampusCenter'; I='Room_02'; L='Room_04'; B='Room_05'; F='Room_06'; U='Room_07'; G='Campus_GuidedTour'; N='Campus_NoStudents' }
Write-Host 'KING SCHOOL - CAMPUS CENTER'
Write-Host 'E Entrance / full exploration    I Innovation Lab'
Write-Host 'L Lockers                       B Student bathroom'
Write-Host 'F Fitness room                  U Upper commons overlook'
Write-Host 'G Automatic guided tour         N Explore without students'
Write-Host 'WASD move, mouse look, Space jump, Alt+F4 close, Alt+Enter fullscreen.'
$selection = (Read-Host 'Choose E/I/L/B/F/U/G/N (Enter = entrance)').ToUpperInvariant()
if (-not $maps.ContainsKey($selection)) { $selection='E' }
$map = '/Game/Campus/Maps/' + $maps[$selection]
if (Test-Path -LiteralPath $standalone) {
 Start-Process -FilePath $standalone -ArgumentList @($map,'-windowed','-ForceRes','-ResX=1920','-ResY=1080')
} else {
 $editorExe='C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
 if (-not (Test-Path -LiteralPath $editorExe)) { throw 'Unreal 5.8 editor was not found; open CampusCenter.uproject with your installed editor.' }
 Start-Process -FilePath $editorExe -ArgumentList @(('"'+$projectFile+'"'),$map,'-game','-windowed','-ForceRes','-ResX=1920','-ResY=1080','-nosplash')
}


