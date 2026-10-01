$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path $PSScriptRoot
$projectRoot = Join-Path $taskRoot 'CampusCenter-vive/unreal/unreal_project'
$shortRoot = 'C:/Users/mikef/AppData/Local/Temp/CCViveR15'
$archive = Join-Path $taskRoot 'CampusCenter-vive/review_build_vive_openxr_r07_r01'
if (Test-Path -LiteralPath $archive) { throw 'Preserve existing archive; choose a new version.' }
if (Test-Path -LiteralPath $shortRoot) {
 $junction = Get-Item -LiteralPath $shortRoot
 if ($junction.LinkType -ne 'Junction' -or [IO.Path]::GetFullPath((@($junction.Target)[0])) -ne [IO.Path]::GetFullPath($projectRoot)) { throw 'Unexpected short project path; do not overwrite it.' }
} else {
 New-Item -ItemType Junction -Path $shortRoot -Target $projectRoot | Out-Null
}
$frozen = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'frozen-final.json') -Raw | ConvertFrom-Json
if ((Get-FileHash -LiteralPath $frozen.map_file -Algorithm SHA256).Hash.ToLowerInvariant() -ne $frozen.map_sha256) { throw 'Frozen map changed.' }
$protected = @(Get-ChildItem -LiteralPath (Join-Path $projectRoot 'Config') -File -Recurse)
$protected += Get-Item -LiteralPath (Join-Path $projectRoot 'CampusCenter.uproject')
$backupRoot = Join-Path $PSScriptRoot 'package-source-config-snapshot-recovery-r02'
$before = @($protected | ForEach-Object {
 $relative = [IO.Path]::GetRelativePath($projectRoot,$_.FullName)
 $backupFile = Join-Path $backupRoot $relative
 New-Item -ItemType Directory -Path (Split-Path $backupFile) -Force | Out-Null
 Copy-Item -LiteralPath $_.FullName -Destination $backupFile
 @{path=$_.FullName;sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash;backup=$backupFile}
})
$before | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'vive-package-protected-files-recovery-r02.json') -Encoding utf8
$env:uebp_LogFolder = Join-Path $PSScriptRoot 'vive-eq27-uat-logs-recovery-r02'
$env:uebp_FinalLogFolder = $env:uebp_LogFolder
$env:uebp_EngineSavedFolder = Join-Path $PSScriptRoot 'vive-eq27-uat-generated-recovery-r02'
$uat = 'C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/RunUAT.bat'
& $uat BuildCookRun "-project=$shortRoot/CampusCenter.uproject" -noP4 -platform=Win64 -clientconfig=Development -build -cook -stage -pak -archive "-archivedirectory=$archive" "-map=$($frozen.map)+$($frozen.baseline_map)+/Game/Campus/Maps/CampusCenter_StandardAssets_v07" "-stagingdirectory=$PSScriptRoot/staging-r07-r01" -nocompileeditor -installed -unattended '-unrealexe=UnrealEditor-Cmd.exe' "-AdditionalCookerOptions=-DisablePlugins=MetaHumanCrowdContent -DDC=CommonsLocal -ShaderWorkingDir=$shortRoot/Intermediate/ShaderWork"
$buildExit=$LASTEXITCODE
$automaticRewrites=@()
foreach ($row in $before) {
 if ((Get-FileHash -LiteralPath $row.path -Algorithm SHA256).Hash -ne $row.sha256) {
  $automaticRewrites += $row.path
  Copy-Item -LiteralPath $row.backup -Destination $row.path -Force
 }
 if ((Get-FileHash -LiteralPath $row.path -Algorithm SHA256).Hash -ne $row.sha256) { throw 'Source configuration restoration failed.' }
}
if ((Get-FileHash -LiteralPath $frozen.map_file -Algorithm SHA256).Hash.ToLowerInvariant() -ne $frozen.map_sha256) { throw 'Frozen map changed during build.' }
$receipt=Join-Path $projectRoot 'Binaries/Win64/CampusCenter.target'
@{exit_code=$buildExit;map=$frozen.map;map_sha256=$frozen.map_sha256;archive=$archive;receipt=$receipt;receipt_exists=(Test-Path -LiteralPath $receipt);source_configuration_restored=$true;automatic_config_rewrites=$automaticRewrites;headset_operation='unverified';status='Build/cook/stage only; packaged smoke test and visual verification required.'} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'package-final.json') -Encoding utf8
if ($buildExit -ne 0) { throw "Vive BuildCookRun failed: $buildExit" }
if (-not (Test-Path -LiteralPath $receipt)) { throw 'Native target receipt missing despite UAT success.' }
