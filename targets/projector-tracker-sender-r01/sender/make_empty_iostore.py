import os as _publication_os
def _publication_path(name, suffix):
 root=_publication_os.environ[name]
 return root.replace('\\','/').rstrip('/')+'/'+suffix

from pathlib import Path
import subprocess,json,hashlib
r=Path(__file__).resolve().parent;out=r/'metadata-overlay'
cook=Path(_publication_path('CC_REVIEW_ROOT', 'CampusCenter_Quest3_PC_VR_R01/Cooked/Windows'))
meta=cook/'CampusCenter/Metadata'
response=out/'empty-response.txt';response.write_text('')
commands=out/'empty-commands.txt';commands.write_text('-Output="'+str(out/'CampusCenter-ProjectorSenderR01_3_P.utoc')+'" -ContainerName=CampusCenter-ProjectorSenderR01 -ResponseFile="'+str(response)+'"\n')
args=[_publication_path('CC_UE_ROOT', 'Engine/Binaries/Win64/UnrealPak.exe'),str(r/'project/CampusCenter.uproject'),'-CreateGlobalContainer='+str(out/'unused-global.utoc'),'-PackageStoreManifest='+str(meta/'packagestore.manifest'),'-CookedDirectory='+str(cook),'-Commands='+str(commands),'-ScriptObjects='+str(meta/'scriptobjects.bin'),'-compressionformats=Oodle','-platform=Windows','-unattended']
run=subprocess.run(args,capture_output=True,text=True)
(out/'empty-iostore.log').write_text(run.stdout+run.stderr)
assert run.returncode==0,run.returncode
rows=[dict(path=p.name,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in out.glob('CampusCenter-ProjectorSenderR01_3_P.*')]
(out/'overlay-files.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows))
