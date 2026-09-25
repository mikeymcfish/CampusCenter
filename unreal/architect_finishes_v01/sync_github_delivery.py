"""Copy the validated map dependency closure into the existing Git delivery repo."""
from pathlib import Path
import json,hashlib,shutil,re
root=Path(__file__).resolve().parent.parent
repo=Path('P:/_code/CampusCenter')
assert (repo/'.git').is_dir()
dest=repo/'unreal'; project=root/'unreal_project'
report=json.loads((root/'architect_finishes_v01/delivery_validation.json').read_text())
assert not report['errors']
copied=[]
def copy(s,d):
 if d.exists() and hashlib.sha256(s.read_bytes()).digest()==hashlib.sha256(d.read_bytes()).digest():return
 d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(s,d);copied.append(str(d.relative_to(repo)))
for rel in report['dependency_files']:copy(project/rel,dest/'unreal_project'/rel)
for s in (project/'Config').glob('*.ini'):
 text=s.read_text();text=re.sub(r'^SecurityToken=.*\n','',text,flags=re.M)
 d=dest/'unreal_project/Config'/s.name;d.parent.mkdir(parents=True,exist_ok=True)
 if not d.exists() or d.read_text()!=text:d.write_text(text);copied.append(str(d.relative_to(repo)))
copy(project/'CampusCenter.uproject',dest/'unreal_project/CampusCenter.uproject')
for s in (project/'Plugins').rglob('*'):
 if s.is_file() and s.suffix!='.pdb' and 'Intermediate' not in s.parts:
  copy(s,dest/'unreal_project'/s.relative_to(project))
for name in ['Launch_Unreal.cmd','Launch_Unreal.ps1','Walk_Commons_Dusk.cmd','Edit_Commons_Dusk.cmd']:
 copy(root/name,dest/name)
for pattern in ['*architect*.py','critic_capture_views.py','clear_dusk_banner_wall_v03.py']:
 for s in project.glob(pattern):copy(s,dest/'unreal_project'/s.name)
for pattern in ['*.py','*.json','README.md','Architect_Finishes_v05.glb']:
 for s in (root/'architect_finishes_v01').glob(pattern):
  if s.name.startswith('unreal_capture_complete') or s.name=='github_sync.json':continue
  copy(s,dest/'architect_finishes_v01'/s.name)
for folder in (root/'architect_finishes_v01').glob('critic_round_*'):
 if folder.is_dir():
  for s in folder.iterdir():
   if s.suffix in ['.png','.json','.md']:copy(s,dest/'architect_finishes_v01'/folder.name/s.name)
for sub,names in {'common_area':['CREDITS.md','manifest.json','assets.csv'],
 'ilab_v06':['README.md','furniture_manifest.json','technology_manifest.json']}.items():
 for name in names:
  s=root/'realism_assets'/sub/name
  if s.is_file():copy(s,dest/'asset_provenance'/sub/name)
(root/'architect_finishes_v01/github_sync.json').write_text(json.dumps({'repository':str(repo),'files_copied':copied},indent=2))
print('Copied',len(copied),'files into',repo)
