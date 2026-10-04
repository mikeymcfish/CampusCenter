@echo off
setlocal
cd /d "%~dp0"
if not exist "%~dp0CampusCenter\Binaries\Win64\CampusCenter.exe" (
 echo Place this launcher in the existing Windows build folder beside CampusCenter.exe.
 exit /b 2
)
"%~dp0CampusCenter\Binaries\Win64\CampusCenter.exe" /Game/Campus/Maps/CampusCenter_Vive_R29_TrophyTrainerGymCorrections_r02 -DisablePlugins=MetaHumanCrowdContent -game -vr -fullscreen -ResX=1920 -ResY=1080 -nosplash "-ini:Engine:[SystemSettings]:r.Streaming.PoolSize=2000,[SystemSettings]:r.Streaming.LimitPoolSizeToVRAM=1,[SystemSettings]:r.RayTracing=0,[SystemSettings]:r.Lumen.HardwareRayTracing=0,[SystemSettings]:r.Shadow.Virtual.MaxPhysicalPages=4096,[SystemSettings]:r.Shadow.Virtual.SMRT.RayCountLocal=2,[SystemSettings]:r.Shadow.Virtual.SMRT.SamplesPerRayLocal=4,[SystemSettings]:r.Shadow.Virtual.SMRT.RayCountDirectional=2,[SystemSettings]:r.Shadow.Virtual.SMRT.SamplesPerRayDirectional=4,[SystemSettings]:r.Lumen.ScreenProbeGather.DownsampleFactor=32,[SystemSettings]:r.Lumen.Reflections.DownsampleFactor=2,[SystemSettings]:vr.PixelDensity=0.65,[SystemSettings]:t.MaxFPS=0" -ExecCmds="r.ScreenPercentage 50,stat fps" -LogCmds="LogHMD Verbose" %*
endlocal
