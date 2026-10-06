import os as _publication_os
def _publication_path(name, suffix):
 root=_publication_os.environ[name]
 return root.replace('\\','/').rstrip('/')+'/'+suffix

from pathlib import Path
import json,hashlib,subprocess,shutil
r=Path(__file__).resolve().parent
baseline=r/'base-pak-metadata/CampusCenter/Plugins/CampusCenter.upluginmanifest'
old=json.loads(baseline.read_text());new=json.loads(baseline.read_text())
osc=Path(_publication_path('CC_UE_ROOT', 'Engine/Plugins/Runtime/OSC/OSC.uplugin'))
assert not any(x['File'].endswith('/OSC.uplugin') for x in new['Contents'])
new['Contents'].append(dict(File='../../../Engine/Plugins/Runtime/OSC/OSC.uplugin',Descriptor=json.loads(osc.read_text())))
assert new['Contents'][:-1]==old['Contents']
out=r/'metadata-overlay';out.mkdir(exist_ok=True)
manifest=out/'CampusCenter.upluginmanifest';manifest.write_text(json.dumps(new,indent=2))
response=out/'response.txt';response.write_text('"'+str(manifest)+'" "../../../CampusCenter/Plugins/CampusCenter.upluginmanifest"\n')
pak=out/'CampusCenter-ProjectorSenderR01_3_P.pak'
assert not pak.exists()
run=subprocess.run([_publication_path('CC_UE_ROOT', 'Engine/Binaries/Win64/UnrealPak.exe'),str(pak),'-Create='+str(response),'-compress'],capture_output=True,text=True)
(out/'build.log').write_text(run.stdout+run.stderr)
assert run.returncode==0 and pak.exists()
proof=dict(baseline_sha256=hashlib.sha256(baseline.read_bytes()).hexdigest(),original_entries_preserved=len(old['Contents']),added_entry=new['Contents'][-1]['File'],pak_bytes=pak.stat().st_size,pak_sha256=hashlib.sha256(pak.read_bytes()).hexdigest(),only_packaged_path='../../../CampusCenter/Plugins/CampusCenter.upluginmanifest')
(out/'proof.json').write_text(json.dumps(proof,indent=2))
print(json.dumps(proof))
