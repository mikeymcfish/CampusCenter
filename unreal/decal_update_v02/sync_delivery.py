"""Publish only the validated current map dependencies and review/source artifacts."""
from pathlib import Path
import json,hashlib,shutil,re
root=Path(__file__).resolve().parent.parent
repo=Path('P:/_code/CampusCenter');dest=repo/'unreal';project=root/'unreal_project';R=root/'decal_update_v02'
assert (repo/'.git').is_dir()
report=json.loads((R/'delivery_validation.json').read_text());assert not report['errors']
copied=[];verified=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def copy(s,d):
 h=sha(s)
 if not d.exists() or sha(d)!=h:
  d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(s,d);copied.append(str(d.relative_to(repo)))
 assert sha(d)==h
 verified.append({'path':str(d.relative_to(repo)).replace('\\','/'),'sha256':h,'bytes':s.stat().st_size})
for rel in report['dependency_files']:copy(project/rel,dest/'unreal_project'/rel)
for s in (project/'Config').glob('*.ini'):
 text=re.sub(r'^SecurityToken=.*\n','',s.read_text(encoding='utf-8'),flags=re.M);d=dest/'unreal_project/Config'/s.name;d.parent.mkdir(parents=True,exist_ok=True)
 if not d.exists() or d.read_text(encoding='utf-8')!=text:d.write_text(text,encoding='utf-8');copied.append(str(d.relative_to(repo)))
for name in ['Launch_Unreal.cmd','Launch_Unreal.ps1','Walk_Commons_Dusk.cmd','Edit_Commons_Dusk.cmd']:copy(root/name,dest/name)
for s in R.rglob('*'):
 if not s.is_file() or s.name in ['github_sync.json','github_push.json'] or '__pycache__' in s.parts:continue
 if s.suffix.lower() not in ['.py','.json','.md','.png','.jpg','.glb','.blend']:continue
 copy(s,dest/'decal_update_v02'/s.relative_to(R))
manifest={'map':report['map'],'files':verified,'validation':'decal_update_v02/delivery_validation.json'}
(dest/'DECAL_ASSET_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
readme=dest/'README.md';text=readme.read_text(encoding='utf-8');marker='## Artwork and trophy update — September 25, 2026'
header=(R/'repo_header.md').read_text(encoding='utf-8').rstrip()+'\n\n'
prior=next(v for v in ['## Current architect finish revision','## Previous architect finish revision'] if v in text)
if marker in text:text=text[:text.index(marker)]+header+text[text.index(prior):]
else:text=text.replace(prior,header+prior,1)
text=text.replace('## Current architect finish revision','## Previous architect finish revision',1)
readme.write_text(text,encoding='utf-8')
(R/'github_sync.json').write_text(json.dumps({'repository':str(repo),'files_copied':copied,'verified_files':len(verified)},indent=2))
print('Verified',len(verified),'files; copied',len(copied))
