"""Publish validated map dependencies and four-round review evidence only."""
from pathlib import Path
import json,hashlib,shutil,re
root=Path(__file__).resolve().parent.parent
repo=Path('P:/_code/CampusCenter');dest=repo/'unreal';project=root/'unreal_project';R=root/'ground_floor_review_v03'
assert (repo/'.git').is_dir()
report=json.loads((R/'delivery_validation.json').read_text());assert not report['errors']
reviews=[json.loads((R/('critic_round_'+str(i))/'review.json').read_text()) for i in range(1,5)]
assert len(reviews)==4
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
    text=re.sub(r'^SecurityToken=.*\n','',s.read_text(encoding='utf-8'),flags=re.M);d=dest/'unreal_project/Config'/s.name
    if not d.exists() or d.read_text(encoding='utf-8')!=text:d.write_text(text,encoding='utf-8');copied.append(str(d.relative_to(repo)))
    assert d.read_text(encoding='utf-8')==text
    verified.append({'path':str(d.relative_to(repo)).replace('\\','/'),'sha256':sha(d),'bytes':d.stat().st_size})
for name in ['Launch_Unreal.cmd','Launch_Unreal.ps1','Walk_Commons_Dusk.cmd','Edit_Commons_Dusk.cmd']:copy(root/name,dest/name)
for s in R.rglob('*'):
    if not s.is_file() or s.name in ['github_sync.json','github_push.json'] or '__pycache__' in s.parts:continue
    if any(part.startswith('technical_attempt') for part in s.parts):continue
    if s.suffix.lower() not in ['.py','.json','.md','.html','.png','.jpg']:continue
    copy(s,dest/'ground_floor_review_v03'/s.relative_to(R))
# Preserve full-resolution review images in LFS, scoped to this new evidence directory.
attrs=repo/'.gitattributes';text=attrs.read_text(encoding='utf-8');rule='unreal/ground_floor_review_v03/**/*.png filter=lfs diff=lfs merge=lfs -text'
if rule not in text:attrs.write_text(text.rstrip()+'\n\n'+rule+'\n',encoding='utf-8')
(dest/'GROUND_FLOOR_ASSET_MANIFEST.json').write_text(json.dumps({'map':report['map'],'files':verified,'validation':'ground_floor_review_v03/delivery_validation.json'},indent=2))
readme=dest/'README.md';text=readme.read_text(encoding='utf-8');marker='## Ground-floor review'
header=(R/'repo_header.md').read_text(encoding='utf-8').rstrip()+'\n\n'
prior='## Artwork and trophy update'
assert prior in text
if marker in text:text=text[:text.index(marker)]+header+text[text.index(prior):]
else:text=text.replace(prior,header+prior,1)
text=text.replace('The current launchers open `/Game/Campus/Maps/CampusCenter_ArchitectDecals_v04`','This prior revision used `/Game/Campus/Maps/CampusCenter_ArchitectDecals_v04`')
readme.write_text(text,encoding='utf-8')
readme=repo/'README.md';text=readme.read_text(encoding='utf-8')
text=re.sub(r'^\*\*Current Unreal walkthrough.*$', '**Current Unreal walkthrough (September 25, 2026):** [full ground-floor review and latest revision](unreal/README.md). Four independent critic rounds cover 31 ground-floor rooms/zones. Launch with `unreal/Launch_Unreal.cmd` using Unreal Engine 5.8.2. Furniture, supplied artwork/trophy decals and the Blender master are preserved. See the final review for the score and remaining issues.',text,flags=re.M)
readme.write_text(text,encoding='utf-8')
(R/'github_sync.json').write_text(json.dumps({'repository':str(repo),'files_copied':copied,'verified_files':len(verified)},indent=2))
print('Verified',len(verified),'files; copied',len(copied))
