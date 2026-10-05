[CmdletBinding()]
param([switch]$PrepareOnly,[switch]$VerifyOnly,[switch]$RollbackQuest,[switch]$EnableQuest,[ValidateSet('VisualBaseline','RTX2080')][string]$Profile='VisualBaseline',[switch]$Diagnostic)
$ErrorActionPreference='Stop';Set-StrictMode -Version Latest
[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12
Add-Type -AssemblyName System.IO.Compression.FileSystem
$repoRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$pins=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'CampusCenter-Quest3PCVRR01-downloads.json') -Raw | ConvertFrom-Json
$root=Join-Path $repoRoot '.cc/r29/q';$payload=Join-Path $root 'payload';$windows=Join-Path $root 'w/Windows';$mode=Join-Path $root 'quest-mode.txt';$source=Join-Path $repoRoot '.cc/r29/qb/g/Windows';$lock=$null
$windows=[IO.Path]::GetFullPath($windows);$source=[IO.Path]::GetFullPath($source)
function QHash([string]$Path){$s=[IO.File]::OpenRead($Path);$h=[Security.Cryptography.SHA256]::Create();try{return ([BitConverter]::ToString($h.ComputeHash($s))).Replace('-','').ToLowerInvariant()}finally{$s.Dispose();$h.Dispose()}}
function QMatches([string]$Path,$Pin){return (Test-Path -LiteralPath $Path -PathType Leaf) -and (Get-Item -LiteralPath $Path).Length -eq [long]$Pin.bytes -and (QHash $Path) -eq $Pin.sha256}
function QPreserve([string]$Path){$full=[IO.Path]::GetFullPath($Path);$prefix=[IO.Path]::GetFullPath($root).TrimEnd('\')+'\';if(-not $full.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase)){throw 'Refusing to move outside the Quest cache.'};if(Test-Path -LiteralPath $full){Move-Item -LiteralPath $full -Destination ($full+'.preserved.'+[Guid]::NewGuid().ToString('N'))}}
function QCheckNotRunning{foreach($p in @(Get-Process CampusCenter -ErrorAction SilentlyContinue)){if($p.Path -and $p.Path.StartsWith($windows+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Close the Quest game first. No process was stopped.'}}}
function QPayload{
 $archive=Join-Path $root $pins.patch.name
 if(-not (QMatches $archive $pins.patch)){
  if($VerifyOnly){throw 'Quest package cache is missing or invalid. Run normally to prepare it.'}
  QPreserve $archive;$partial=$archive+'.partial';QPreserve $partial
  $request=[Net.HttpWebRequest]::Create($pins.patch.url);$request.Timeout=60000;$request.ReadWriteTimeout=60000;$response=$request.GetResponse()
  try{$inputStream=$response.GetResponseStream();$outputStream=[IO.File]::Create($partial);try{$inputStream.CopyTo($outputStream)}finally{$inputStream.Dispose();$outputStream.Dispose()}}finally{$response.Dispose()}
  if(-not (QMatches $partial $pins.patch)){throw 'Quest package hash mismatch; nothing will install.'};Move-Item -LiteralPath $partial -Destination $archive
 }
 $expected=@{};foreach($entry in $pins.entries){$expected[$entry.path]=$entry}
 if(Test-Path -LiteralPath $payload){
  foreach($entry in $pins.entries){if(-not (QMatches (Join-Path $payload $entry.path) $entry)){throw 'Quest payload was altered; preserve it for review.'}}
  foreach($file in @(Get-ChildItem -LiteralPath $payload -Recurse -File)){if(-not $expected.ContainsKey($file.FullName.Substring($payload.Length+1).Replace('\','/'))){throw 'Unknown Quest payload file; no installer will run.'}}
  return
 }
 if($VerifyOnly){throw 'Quest installer cache is not prepared.'}
 $stage=$payload+'.partial';QPreserve $stage;New-Item -ItemType Directory -Path $stage | Out-Null;$prefix=[IO.Path]::GetFullPath($stage).TrimEnd('\')+'\';$seen=@{}
 $zip=[IO.Compression.ZipFile]::OpenRead($archive)
 try{
  if($zip.Entries.Count -ne $expected.Count){throw 'Unexpected Quest ZIP entry count.'}
  foreach($entry in $zip.Entries){
   if(-not $expected.ContainsKey($entry.FullName) -or $seen.ContainsKey($entry.FullName)){throw 'Unexpected Quest ZIP entry.'};$seen[$entry.FullName]=$true
   $target=[IO.Path]::GetFullPath((Join-Path $stage $entry.FullName));if(-not $target.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase)){throw 'Unsafe Quest ZIP path.'}
   New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($target)) -Force | Out-Null
   $inputStream=$entry.Open();$outputStream=[IO.File]::Create($target);try{$inputStream.CopyTo($outputStream)}finally{$inputStream.Dispose();$outputStream.Dispose()}
   if(-not (QMatches $target $expected[$entry.FullName])){throw 'Quest payload hash mismatch.'}
  }
 }finally{$zip.Dispose()}
 Move-Item -LiteralPath $stage -Destination $payload
}
function QVerifyRuntime{
 foreach($entry in $pins.base_files){if(-not (QMatches (Join-Path $windows $entry.path) $entry)){throw ('Quest base hash mismatch: '+$entry.path)}}
 foreach($entry in $pins.overlays){if(-not (QMatches (Join-Path $windows ('CampusCenter/Content/Paks/'+$entry.path)) $entry)){throw ('Quest overlay hash mismatch: '+$entry.path)}}
 $expected=@{};foreach($entry in $pins.base_files){$expected[$entry.path]=$true};foreach($entry in $pins.overlays){$expected['CampusCenter/Content/Paks/'+$entry.path]=$true}
 foreach($name in @('QuestPCVR.ps1','quest-manifest.json','Start_CampusCenter_Quest3_USB_Link.cmd','README.md')){
  $pin=$pins.entries | Where-Object path -EQ $name
  if(-not (QMatches (Join-Path $windows $name) $pin)){throw 'Installed Quest launcher/manifest was altered.'};$expected[$name]=$true
 }
 $identityPath=Join-Path $windows 'quest-installed.json';if(-not (Test-Path -LiteralPath $identityPath)){throw 'Quest overlay is not installed.'}
 $identity=Get-Content -LiteralPath $identityPath -Raw | ConvertFrom-Json
 if($identity.revision -ne $pins.revision -or $identity.target -ne $windows -or $identity.source -ne $source -or $identity.nativeReplaced -ne $false){throw 'Quest install identity differs.'};$expected['quest-installed.json']=$true
 foreach($file in @(Get-ChildItem -LiteralPath $windows -Recurse -File)){
  $relative=$file.FullName.Substring($windows.Length+1).Replace('\','/')
  if(-not $expected.ContainsKey($relative) -and $relative -notmatch '^(CampusCenter|Engine)/Saved/' -and $relative -notmatch '^QuestUserData/'){throw ('Unknown Quest runtime file preserved: '+$relative)}
 }
}
function QInvoke([string]$Action){
 $arguments=@('-NoProfile','-File',(Join-Path $payload 'QuestPCVR.ps1'),'-Action',$Action,'-TargetWindows',$windows)
 if($Action -eq 'Install'){$arguments+=@('-SourceWindows',$source)}
 if($Action -eq 'Launch'){$arguments+=@('-Profile',$Profile);if($Diagnostic){$arguments+='-Diagnostic'}}
 & powershell.exe @arguments
 if($LASTEXITCODE -ne 0){throw "Quest $Action stopped (exit $LASTEXITCODE). Existing caches were preserved."}
}
try{
 if($RollbackQuest -and $EnableQuest){throw 'Choose rollback or enable, not both.'};if($VerifyOnly -and ($RollbackQuest -or $EnableQuest)){throw 'VerifyOnly does not change Quest mode.'}
 New-Item -ItemType Directory -Path $root -Force | Out-Null;$lock=[IO.File]::Open((Join-Path $root 'setup.lock'),[IO.FileMode]::OpenOrCreate,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None)
 QPayload
 $disabled=(Test-Path -LiteralPath $mode) -and ((Get-Content -LiteralPath $mode -Raw).Trim() -eq 'disabled')
 if($RollbackQuest){QCheckNotRunning;QVerifyRuntime;QInvoke 'Rollback';[IO.File]::WriteAllText($mode,'disabled');Write-Host 'Quest overlay rolled back. Vive and desktop are unchanged; use -EnableQuest to create a fresh Quest copy.';exit 0}
 if($disabled -and -not $EnableQuest){throw 'Quest was rolled back and remains disabled. Use -EnableQuest to prepare a new copy; the retired copy is preserved.'}
 if($EnableQuest -and (Test-Path -LiteralPath (Join-Path $root 'w'))){
  QCheckNotRunning
  if(Test-Path -LiteralPath (Join-Path $windows 'quest-installed.json')){QVerifyRuntime;throw 'Quest is already installed. Run normally; no re-enable is needed.'}
  if(-not $disabled){throw 'Unknown Quest target will not be replaced.'}
  QPreserve (Join-Path $root 'w')
 }
 if(-not (Test-Path -LiteralPath $windows)){
  if($VerifyOnly){throw 'Quest runtime is not prepared.'}
  Write-Host 'Preparing a separate verified R29 grip baseline for Quest; existing Vive caches stay intact.'
  & powershell.exe -NoProfile -File (Join-Path $PSScriptRoot 'Run-CampusCenter.ps1') -Build Vive -RuntimeTarget QuestBase -PrepareOnly
  if($LASTEXITCODE -ne 0){throw 'Separate Quest grip baseline preparation stopped.'}
  QInvoke 'Install';[IO.File]::WriteAllText($mode,'enabled')
 }
 QVerifyRuntime
 if($PrepareOnly -or $VerifyOnly){Write-Host 'Quest PC-VR prepared and verified; game not launched. Link/Touch hardware acceptance remains unverified.';exit 0}
 Write-Host 'Enter USB Link with Quest 3 and use the operator-selected OpenXR runtime. This launcher does not install Meta software or change the runtime.'
 QInvoke 'Launch'
}catch{Write-Error -ErrorAction Continue $_.Exception.Message;exit 1}finally{if($null -ne $lock){$lock.Dispose()}}
