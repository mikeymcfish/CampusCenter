$ErrorActionPreference = 'Stop'
$stageRoot = Join-Path $PSScriptRoot 'CampusCenter-new-plans/downstream/desktop_r01/unreal_project'
$protected = @(Get-ChildItem (Join-Path $stageRoot 'Config') -File -Recurse)
$protected += Get-Item (Join-Path $stageRoot 'CampusCenter.uproject')
$before = @($protected | ForEach-Object { @{ path=$_.FullName; sha256=(Get-FileHash $_.FullName -Algorithm SHA256).Hash } })
& 'C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/Build.bat' CampusCenter Win64 Development '-Project=C:/Users/mikef/AppData/Local/Temp/CCDeskR01/CampusCenter.uproject' -WaitMutex -NoHotReloadFromIDE "-log=$PSScriptRoot/desktop-native-target-r15-ubt.log"
$result = $LASTEXITCODE
foreach ($file in $before) { if ((Get-FileHash -LiteralPath $file.path -Algorithm SHA256).Hash -ne $file.sha256) { throw "Protected configuration changed: $($file.path)" } }
@{ exit_code=$result; protected_configuration_unchanged=$true; receipt=(Join-Path $stageRoot 'Binaries/Win64/CampusCenter.target') } | ConvertTo-Json | Set-Content (Join-Path $PSScriptRoot 'desktop-native-target-r15-result.json')
if ($result -ne 0) { throw "Native target build failed: $result" }
