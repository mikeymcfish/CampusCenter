import os as _publication_os
def _publication_path(name, suffix):
 root=_publication_os.environ[name]
 return root.replace('\\','/').rstrip('/')+'/'+suffix

from pathlib import Path
import json,hashlib,os,shutil
root=Path(__file__).resolve().parent
source=Path(_publication_path('CC_REVIEW_ROOT', 'CampusCenter_Quest3_PC_VR_R01/Runtime/Windows'))
target=Path(_publication_path('CC_REVIEW_ROOT', 'CampusCenter_ProjectorSender_R01/Runtime/Windows'))
manifest=json.loads((root.parent/'quest3-pcvr-r01/payload/quest-manifest.json').read_text())
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()
assert not target.exists(),'Refuse existing target; preserve originals'
rows=list(manifest['base_files'])+[dict(path='CampusCenter/Content/Paks/'+r['path'],sha256=r['sha256']) for r in manifest['overlay_files']]
for row in rows:assert sha(source/row['path'])==row['sha256'],row['path']
native='CampusCenter/Binaries/Win64/CampusCenter.exe'
new=root/'project/Binaries/Win64/CampusCenter.exe'
proof=dict(source=str(source),target=str(target),base_native_sha256=sha(source/native),new_native_sha256=sha(new),base_files=rows,unchanged=[])
for row in rows:
    dst=target/row['path'];dst.parent.mkdir(parents=True,exist_ok=True)
    if row['path']==native:shutil.copy2(new,dst)
    else:
        os.link(source/row['path'],dst) # Immutable base only; never write these linked files.
        assert sha(dst)==row['sha256'];proof['unchanged'].append(row['path'])
(root/'runtime-staging-proof.json').write_text(json.dumps(proof,indent=2))
print(json.dumps(dict(target=str(target),files=len(rows),new_native=proof['new_native_sha256'])))
