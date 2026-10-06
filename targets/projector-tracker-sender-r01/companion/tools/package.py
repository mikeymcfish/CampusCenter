"""Stage an xcopy Windows build with private already-installed runtime, no install/download."""
from pathlib import Path
import shutil,json,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[1]
DOTNET=Path(r'C:\Program Files\dotnet')
stage=ROOT/'stage/CampusCenterTracker_R01'
app=ROOT/'src/Tracker.App/bin/Release/net9.0-windows'
assert (app/'CampusCenterTracker.exe').exists()
stage.mkdir(parents=True,exist_ok=True)
shutil.copytree(app,stage/'app',dirs_exist_ok=True,ignore=shutil.ignore_patterns('*.pdb'))
rt=stage/'runtime';rt.mkdir(exist_ok=True)
for name in ['dotnet.exe','LICENSE.txt','ThirdPartyNotices.txt']:shutil.copy2(DOTNET/name,rt/name)
for folder in ['host/fxr/9.0.4','shared/Microsoft.NETCore.App/9.0.4','shared/Microsoft.WindowsDesktop.App/9.0.4']:
    shutil.copytree(DOTNET/folder,rt/folder,dirs_exist_ok=True)
cmd='''@echo off
setlocal
set "DOTNET_ROOT_X64=%~dp0runtime"
set "DOTNET_ROOT=%~dp0runtime"
set "DOTNET_MULTILEVEL_LOOKUP=0"
if not exist "%~dp0runtime\\host\\fxr\\9.0.4\\hostfxr.dll" (
  echo Private runtime missing. Extract the complete portable ZIP first.
  pause
  exit /b 1
)
start "" "%~dp0app\\CampusCenterTracker.exe" --quiet %*
'''
(stage/'Start_Tracker.cmd').write_text(cmd.replace('\n','\r\n'))
(stage/'Start_Tracker_Simulator.cmd').write_text('@echo off\r\ncall "%~dp0Start_Tracker.cmd" --simulate --live %*\r\n')
for f in ['README.md','QA.md','TELEMETRY_CONTRACT.md']:shutil.copy2(ROOT/f,stage/f)
shutil.copytree(ROOT/'qa',stage/'qa',dirs_exist_ok=True)
manifest={str(p.relative_to(stage)).replace('\\','/'):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(stage.rglob('*')) if p.is_file() and p.name!='FILE_MANIFEST.json'}
(stage/'FILE_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
out=ROOT/'deliverables';out.mkdir(exist_ok=True)
with zipfile.ZipFile(out/'CampusCenterTracker_R01_Portable_Windows_x64.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(stage.rglob('*')):
        if p.is_file():z.write(p,str(p.relative_to(stage.parent)))
skip={'bin','obj','stage','deliverables','.dotnet-local','.nuget-local','data','__pycache__'}
with zipfile.ZipFile(out/'CampusCenterTracker_R01_Source_and_QA.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(ROOT.rglob('*')):
        if p.is_file() and not any(a in skip for a in p.relative_to(ROOT).parts):z.write(p,str(p.relative_to(ROOT)))
print(json.dumps([{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in out.glob('*.zip')],indent=2))
