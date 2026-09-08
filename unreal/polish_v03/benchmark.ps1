$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
$exe=Join-Path $root 'unreal_delivery/Windows/CampusCenter.exe'
$childExe=Join-Path $root 'unreal_delivery/Windows/Engine/Binaries/Win64/UnrealGame.exe'
foreach($map in @('Room_01','Room_02','Room_07')) {
 $log=(Join-Path $PSScriptRoot "benchmark_$map.log").Replace('\','/')
 $args="/Game/Campus/Maps/$map -windowed -ResX=1920 -ResY=1080 -RenderOffscreen -ForceRes -unattended -nosound -nosplash -csvCaptureFrames=1800 -csvGpuStats -ExitAfterCsvProfiling -ExecCmds=`"r.SetRes 1920x1080w,r.ScreenPercentage 100,t.MaxFPS 0,r.VSync 0,t.IdleWhenNotForeground 0,Shot`" -abslog=`"$log`""
 $p=Start-Process $exe -ArgumentList $args -WindowStyle Hidden -PassThru
 Write-Output "BENCHMARK_STARTED $map bootstrap=$($p.Id)"
 $deadline=(Get-Date).AddSeconds(150)
 do {
  Start-Sleep -Seconds 3
  $ended=(Test-Path $log) -and (Select-String -Path $log -Pattern 'CsvProfiler.ExitAfterCsvProfiling' -Quiet)
 } until($ended -or (Get-Date) -gt $deadline)
 if(-not $ended){throw "Benchmark timeout $map; inspect owned runtime before cleanup."}
 Write-Output "BENCHMARK_FINISHED $map"
 Start-Sleep -Seconds 3
}

