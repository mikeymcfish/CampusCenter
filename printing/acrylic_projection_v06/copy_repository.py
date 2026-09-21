from pathlib import Path
import shutil,hashlib,json
R=Path(__file__).parent;repo=Path('P:/_code/CampusCenter');dest=repo/'printing/acrylic_projection_v06';dest.mkdir(parents=True,exist_ok=True)
omit={'topdown_raw.png','topdown_pilot_raw.png','Topdown_Alpha_pilot.png','Topdown_Black_pilot.png','Pilot_Contact_Sheet.jpg','pilot_render_report.json','pilot_mask_validation.json','room_id_map.npz'}
files=[]
for folder in ['print','rooms','projection','cglide']:
 for p in (R/folder).rglob('*'):
  if p.is_file() and p.name not in omit and p.suffix!='.blend1':files.append(p)
for pattern in ['*.py','*.cjs','*.cmd','*.zip']:
 files.extend(R.glob(pattern))
for name in ['README.md','delivery_validation.json','scene_inventory.json','revision_07_validation.json','revision_08_validation.json']:files.append(R/name)
records=[]
for p in files:
 relative=p.relative_to(R);target=dest/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);src_hash=hashlib.sha256(p.read_bytes()).hexdigest();assert hashlib.sha256(target.read_bytes()).hexdigest()==src_hash;records.append({'path':relative.as_posix(),'bytes':target.stat().st_size,'sha256':src_hash})
(dest/'ASSET_MANIFEST.json').write_text(json.dumps({'source_workspace':str(R),'files_verified':len(records),'files':records},indent=2))
readme=repo/'README.md';text=readme.read_text(encoding='utf-8');line='**Latest ground-floor print and projection package:** [Acrylic slots, 31 room references, and interactive Projection Studio v06](printing/acrylic_projection_v06/README.md). Includes six print pieces, 1/16-inch acrylic templates, H3 prompts, alignment and geometry-based animation examples.\n\n'
if line not in text:
 split=text.find('\n\n');text=text[:split+2]+line+text[split+2:];readme.write_text(text,encoding='utf-8')
attr=repo/'.gitattributes';text=attr.read_text(encoding='utf-8')
for ext in ['mp4','zip','npz']:
 if not any(x.startswith('*.'+ext+' ') for x in text.splitlines()):text+='\n*.'+ext+' filter=lfs diff=lfs merge=lfs -text\n'
attr.write_text(text,encoding='utf-8')
report={'destination':str(dest),'verified_files':len(records),'total_bytes':sum(x['bytes'] for x in records),'readme_link_added':True,'git_lfs_patterns':['mp4','zip','npz'],'committed_or_pushed':False};(R/'repository_delivery.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
