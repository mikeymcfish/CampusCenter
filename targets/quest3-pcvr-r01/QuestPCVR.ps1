param([ValidateSet('Install','Launch','Verify','Rollback')][string]$Action='Launch',[string]$SourceWindows,[string]$TargetWindows,[ValidateSet('RTX2080','VisualBaseline')][string]$Profile='RTX2080',[switch]$Diagnostic)
$ErrorActionPreference='Stop'
$manifest=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'quest-manifest.json') -Raw | ConvertFrom-Json
function FileSha($path){
 $stream=[IO.File]::OpenRead($path);$sha=[Security.Cryptography.SHA256]::Create()
 try{return ([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-','').ToLowerInvariant()}
 finally{$sha.Dispose();$stream.Dispose()}
}
function CheckFiles($root,$rows){
 foreach($row in $rows){
  $path=Join-Path $root $row.path
  if(!(Test-Path -LiteralPath $path -PathType Leaf) -or (FileSha $path) -ne $row.sha256){throw "Hash mismatch or missing: $path"}
 }
}
function CheckRuntime($root){CheckFiles $root $manifest.base_files}
function CheckNotRunning($root){
 $image=[IO.Path]::GetFullPath((Join-Path $root 'CampusCenter/Binaries/Win64/CampusCenter.exe'))
 foreach($p in Get-Process -Name CampusCenter -ErrorAction SilentlyContinue){if($p.Path -eq $image){throw "Close the game in this exact folder first (PID $($p.Id)). No process was stopped."}}
}
function CheckQuest($root){
 CheckRuntime $root
 CheckFiles (Join-Path $root 'CampusCenter/Content/Paks') $manifest.overlay_files
}
if($Action -eq 'Install'){
 if(!$SourceWindows -or !$TargetWindows){throw 'Supply -SourceWindows and a NEW -TargetWindows folder.'}
 $source=[IO.Path]::GetFullPath($SourceWindows);$target=[IO.Path]::GetFullPath($TargetWindows)
 if(Test-Path -LiteralPath $target){throw 'Target already exists. Preserve it; choose a new Quest destination.'}
 if($target.StartsWith($source.TrimEnd('\')+'\',[StringComparison]::OrdinalIgnoreCase) -or $source.StartsWith($target.TrimEnd('\')+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Source and destination must be separate.'}
 if($target.Length -gt 150){throw 'Use a shorter target path for Windows DLL loading.'}
 CheckRuntime $source;CheckNotRunning $source;CheckFiles $PSScriptRoot $manifest.overlay_files
 $expected=@($manifest.base_files | Where-Object path -Like 'CampusCenter/Content/Paks/*' | ForEach-Object {[IO.Path]::GetFileName($_.path)})
 foreach($file in Get-ChildItem -LiteralPath (Join-Path $source 'CampusCenter/Content/Paks') -File){if($file.Name -notin $expected){throw "Unexpected runtime container: $($file.Name). Use the exact managed R29 grip baseline."}}
 New-Item -ItemType Directory -Path $target | Out-Null
 foreach($row in $manifest.base_files){$dest=Join-Path $target $row.path;New-Item -ItemType Directory -Path (Split-Path $dest) -Force | Out-Null;Copy-Item -LiteralPath (Join-Path $source $row.path) -Destination $dest}
 foreach($row in $manifest.overlay_files){Copy-Item -LiteralPath (Join-Path $PSScriptRoot $row.path) -Destination (Join-Path $target ('CampusCenter/Content/Paks/'+$row.path))}
 foreach($name in @('QuestPCVR.ps1','quest-manifest.json','Start_CampusCenter_Quest3_USB_Link.cmd','README.md')){Copy-Item -LiteralPath (Join-Path $PSScriptRoot $name) -Destination (Join-Path $target $name)}
 $state=@{revision=$manifest.revision;target=$target;source=$source;createdUtc=[DateTime]::UtcNow.ToString('o');nativeReplaced=$false}
 $state|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $target 'quest-installed.json') -Encoding UTF8
 CheckQuest $target;Write-Output "Quest copy verified: $target";exit 0
}
if(!$TargetWindows){$TargetWindows=$PSScriptRoot}
$root=[IO.Path]::GetFullPath($TargetWindows)
if(!(Test-Path -LiteralPath (Join-Path $root 'quest-installed.json'))){throw 'Not an installed Quest copy.'}
$state=Get-Content -LiteralPath (Join-Path $root 'quest-installed.json') -Raw|ConvertFrom-Json
if($state.revision -ne $manifest.revision -or $state.target -ne $root){throw 'Quest install identity differs.'}
CheckQuest $root
if($Action -eq 'Verify'){Write-Output 'Quest runtime verified.';exit 0}
CheckNotRunning $root
if($Action -eq 'Rollback'){
 $retired=Join-Path $root ('Quest-overlay-retired-'+[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfff'))
 New-Item -ItemType Directory -Path $retired|Out-Null
 foreach($row in $manifest.overlay_files){Move-Item -LiteralPath (Join-Path $root ('CampusCenter/Content/Paks/'+$row.path)) -Destination (Join-Path $retired $row.path)}
 Move-Item -LiteralPath (Join-Path $root 'quest-installed.json') -Destination (Join-Path $retired 'quest-installed.json')
 Write-Output 'Quest overlay retired; executable, base containers and Vive source unchanged. Use original Vive launcher. Preserve the retired folder.';exit 0
}
$exe=Join-Path $root 'CampusCenter/Binaries/Win64/CampusCenter.exe'
$argsList=@($manifest.map,'-DisablePlugins=MetaHumanCrowdContent','-game','-nosplash','-vr','-windowed','-ResX=1280','-ResY=720')
if($Profile -eq 'RTX2080'){
 $override='-ini:Engine:[SystemSettings]:r.Streaming.PoolSize=3000,[SystemSettings]:r.Streaming.LimitPoolSizeToVRAM=1,[SystemSettings]:r.RayTracing=0,[SystemSettings]:r.Lumen.HardwareRayTracing=0,[SystemSettings]:r.Shadow.Virtual.MaxPhysicalPages=4096,[SystemSettings]:r.Shadow.Virtual.SMRT.RayCountLocal=4,[SystemSettings]:r.Shadow.Virtual.SMRT.SamplesPerRayLocal=4,[SystemSettings]:r.Shadow.Virtual.SMRT.RayCountDirectional=4,[SystemSettings]:r.Lumen.ScreenProbeGather.DownsampleFactor=16,[SystemSettings]:r.Lumen.Reflections.DownsampleFactor=2,[SystemSettings]:vr.PixelDensity=0.7,[SystemSettings]:t.MaxFPS=0'
 $argsList+=('"'+$override+'"');$argsList+='-ExecCmds="r.ScreenPercentage 100"'
}
else{$argsList+='-ExecCmds="r.ScreenPercentage 50"'}
if($Diagnostic){$argsList+='-CampusViveControlLog';$argsList+=('-abslog="'+(Join-Path $env:TEMP 'CampusCenter-Quest3PCVRR01.log')+'"')}
# Disposable project user settings remain in this isolated copy; no shared Saved/config path.
$argsList+=('-UserDir="'+(Join-Path $root 'QuestUserData').Replace('\','/')+'/"')
# This is the authorized interactive review application, with its normal monitor mirror.
$q=Start-Process -FilePath $exe -ArgumentList $argsList -WorkingDirectory $root -WindowStyle Normal -PassThru
Write-Output "Quest PC-VR launched PID $($q.Id), profile $Profile. Headset refresh remains user/runtime controlled."
