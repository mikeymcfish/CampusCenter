param(
 [ValidateSet('Install','Verify','Launch','Rollback')][string]$Action='Verify',
 [string]$SourceWindows,[string]$TargetWindows,
 [ValidateSet('Vive','Quest')][string]$Mode='Vive',
 [ValidateSet('RTX2080','VisualBaseline')][string]$QuestProfile='RTX2080',
 [switch]$EnableSender,[switch]$Diagnostic
)
$ErrorActionPreference='Stop'
$manifest=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'sender-manifest.json') -Raw | ConvertFrom-Json
$nativePath='CampusCenter/Binaries/Win64/CampusCenter.exe'
function FileSha($path){
 $stream=[IO.File]::OpenRead($path);$sha=[Security.Cryptography.SHA256]::Create()
 try{return ([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-','').ToLowerInvariant()}
 finally{$sha.Dispose();$stream.Dispose()}
}
function Under($root,$relative){
 $path=[IO.Path]::GetFullPath((Join-Path $root $relative));$prefix=[IO.Path]::GetFullPath($root).TrimEnd('\')+'\'
 if(!$path.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase)){throw 'Path escapes the exact target.'};return $path
}
function CheckFiles($root,$rows){foreach($row in $rows){$path=Under $root $row.path;if(!(Test-Path -LiteralPath $path -PathType Leaf) -or (FileSha $path) -ne $row.sha256){throw "Missing or changed file: $path"}}}
function NotRunning($root){$image=Under $root $nativePath;foreach($p in Get-Process -Name CampusCenter -ErrorAction SilentlyContinue){if($p.Path -eq $image){throw "Close this exact game first (PID $($p.Id)). No process was stopped."}}}
function CheckPaks($root,$quest,$installed){
 $allowed=@($manifest.base_files|Where-Object path -Like 'CampusCenter/Content/Paks/*'|ForEach-Object {[IO.Path]::GetFileName($_.path)})
 if($quest){$allowed+=@($manifest.optional_quest_files|ForEach-Object {[IO.Path]::GetFileName($_.path)})}
 if($installed){$allowed+=@($manifest.overlay_files|ForEach-Object {$_.path})}
 foreach($f in Get-ChildItem -LiteralPath (Under $root 'CampusCenter/Content/Paks') -File){if($f.Name -notin $allowed){throw "Unrecognized container: $($f.Name). Preserve it; installation/launch stopped."}}
}
function CheckInstalled($root,$state){
 if($state.revision -ne $manifest.revision -or $state.target -ne $root){throw 'Install identity differs; preserve the folder.'}
 CheckFiles $root @($manifest.base_files|Where-Object path -NE $nativePath)
 if((FileSha (Under $root $nativePath)) -ne $manifest.target_exe_sha256){throw 'Native sender hash differs.'}
 CheckFiles (Under $root 'CampusCenter/Content/Paks') $manifest.overlay_files
 if($state.quest){CheckFiles $root $manifest.optional_quest_files}
 CheckPaks $root $state.quest $true
}
if($Action -eq 'Install'){
 if(!$SourceWindows -or !$TargetWindows){throw 'Supply an existing grip-enabled R29 -SourceWindows and a NEW -TargetWindows.'}
 $source=[IO.Path]::GetFullPath($SourceWindows);$target=[IO.Path]::GetFullPath($TargetWindows)
 if(Test-Path -LiteralPath $target){throw 'Destination already exists; no overwrite permitted.'}
 if($target.StartsWith($source.TrimEnd('\')+'\',[StringComparison]::OrdinalIgnoreCase) -or $source.StartsWith($target.TrimEnd('\')+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Source and new destination must be separate.'}
 if($target.Length -gt 150){throw 'Use a shorter target path for Windows DLL loading.'}
 CheckFiles $source $manifest.base_files;NotRunning $source
 $questCount=@($manifest.optional_quest_files|Where-Object {Test-Path -LiteralPath (Under $source $_.path)}).Count
 if($questCount -ne 0 -and $questCount -ne $manifest.optional_quest_files.Count){throw 'Partial Quest overlay; preserve and inspect source.'}
 $quest=$questCount -gt 0;if($quest){CheckFiles $source $manifest.optional_quest_files};CheckPaks $source $quest $false
 CheckFiles $PSScriptRoot $manifest.chunks;CheckFiles $PSScriptRoot $manifest.overlay_files
 $helper=Join-Path $PSScriptRoot 'ApplySenderDelta.exe'
 if((FileSha $helper) -ne $manifest.helper_sha256){throw 'Native delta helper hash differs.'}
 New-Item -ItemType Directory -Path $target|Out-Null
 foreach($row in $manifest.base_files){if($row.path -eq $nativePath){continue};$to=Under $target $row.path;New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($to)) -Force|Out-Null;Copy-Item -LiteralPath (Under $source $row.path) -Destination $to}
 if($quest){foreach($row in $manifest.optional_quest_files){Copy-Item -LiteralPath (Under $source $row.path) -Destination (Under $target $row.path)}}
 $backup=Under $target 'ProjectorSenderBaseline/CampusCenter.exe';New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($backup))|Out-Null
 Copy-Item -LiteralPath (Under $source $nativePath) -Destination $backup
 $native=Under $target $nativePath;New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($native)) -Force|Out-Null
 & $helper $PSScriptRoot $backup $native;if($LASTEXITCODE -ne 0){throw 'Native reconstruction failed. Preserve the incomplete new folder; source is unchanged.'}
 foreach($row in $manifest.overlay_files){Copy-Item -LiteralPath (Join-Path $PSScriptRoot $row.path) -Destination (Under $target ('CampusCenter/Content/Paks/'+$row.path))}
 foreach($file in @('ProjectorSender.ps1','sender-manifest.json','Start_Vive_Projector.cmd','Start_Quest_Projector.cmd')){Copy-Item -LiteralPath (Join-Path $PSScriptRoot $file) -Destination (Under $target $file)}
 $state=[pscustomobject]@{revision=$manifest.revision;source=$source;target=$target;quest=$quest;utc=[DateTime]::UtcNow.ToString('o')}
 $state|ConvertTo-Json|Set-Content -LiteralPath (Under $target 'projector-sender-installed.json') -Encoding UTF8
 CheckInstalled $target $state;Write-Output "Projector sender copy verified: $target";exit 0
}
if(!$TargetWindows){$TargetWindows=$PSScriptRoot};$root=[IO.Path]::GetFullPath($TargetWindows)
$state=Get-Content -LiteralPath (Under $root 'projector-sender-installed.json') -Raw|ConvertFrom-Json
CheckInstalled $root $state
if($Action -eq 'Verify'){Write-Output 'Projector sender runtime verified.';exit 0}
NotRunning $root
if($Action -eq 'Rollback'){
 $backup=Under $root 'ProjectorSenderBaseline/CampusCenter.exe'
 if((FileSha $backup) -ne $manifest.base_exe_sha256){throw 'Baseline native backup differs; no rollback performed.'}
 $retired=Under $root ('ProjectorSenderRetired-'+[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfff'));New-Item -ItemType Directory -Path $retired|Out-Null
 Move-Item -LiteralPath (Under $root $nativePath) -Destination (Join-Path $retired 'CampusCenter.sender.exe')
 Copy-Item -LiteralPath $backup -Destination (Under $root $nativePath)
 foreach($row in $manifest.overlay_files){Move-Item -LiteralPath (Under $root ('CampusCenter/Content/Paks/'+$row.path)) -Destination (Join-Path $retired $row.path)}
 Move-Item -LiteralPath (Under $root 'projector-sender-installed.json') -Destination (Join-Path $retired 'projector-sender-installed.json')
 CheckFiles $root $manifest.base_files;if($state.quest){CheckFiles $root $manifest.optional_quest_files}
 Write-Output 'Baseline native and original containers verified. Sender overlay retired; use the original launcher. Preserve the retired folder.';exit 0
}
if($Mode -eq 'Quest' -and !$state.quest){throw 'Quest launch requires the existing verified Quest Touch overlay in the source; it was not invented or added by this patch.'}
$arguments=$manifest.vive_inherited_arguments
if($Mode -eq 'Quest'){
 $arguments=$manifest.map+' -DisablePlugins=MetaHumanCrowdContent -game -nosplash -vr -windowed -ResX=1280 -ResY=720'
 if($QuestProfile -eq 'RTX2080'){
  $override='-ini:Engine:[SystemSettings]:r.Streaming.PoolSize=3000,[SystemSettings]:r.Streaming.LimitPoolSizeToVRAM=1,[SystemSettings]:r.RayTracing=0,[SystemSettings]:r.Lumen.HardwareRayTracing=0,[SystemSettings]:r.Shadow.Virtual.MaxPhysicalPages=4096,[SystemSettings]:r.Shadow.Virtual.SMRT.RayCountLocal=4,[SystemSettings]:r.Shadow.Virtual.SMRT.SamplesPerRayLocal=4,[SystemSettings]:r.Shadow.Virtual.SMRT.RayCountDirectional=4,[SystemSettings]:r.Lumen.ScreenProbeGather.DownsampleFactor=16,[SystemSettings]:r.Lumen.Reflections.DownsampleFactor=2,[SystemSettings]:vr.PixelDensity=0.7,[SystemSettings]:t.MaxFPS=0'
  $arguments+=' "'+$override+'" -ExecCmds="r.ScreenPercentage 100"'
 }else{$arguments+=' -ExecCmds="r.ScreenPercentage 50"'}
}
if($EnableSender){$arguments+=' -EnablePlugins=OSC -CampusProjector'}
$arguments+=' -UserDir="'+(Under $root 'ProjectorUserData').Replace('\','/')+'/"'
if($Diagnostic){$arguments+=' -abslog="'+(Under $root 'ProjectorUserData/Saved/Logs/ProjectorSender.log')+'"'}
$game=Start-Process -FilePath (Under $root $nativePath) -ArgumentList $arguments -WorkingDirectory $root -WindowStyle Normal -PassThru
Write-Output "CampusCenter PID $($game.Id); sender opt-in=$EnableSender. Existing runtime/settings unchanged. Headset/projector acceptance remains pending."
