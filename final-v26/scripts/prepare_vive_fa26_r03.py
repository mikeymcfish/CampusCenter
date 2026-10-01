from pathlib import Path
import json,hashlib,shutil,datetime
root=Path(__file__).resolve().parent
source=Path(r'C:/Users/mikef/Documents/Codex/2026-09-30/task/CampusCenter-new-plans/downstream/furniture_art_v26_r01/releases/shared_furniture_art_v26_r03')
out=root/'vr-enhancement-v26-r03-preflight';out.mkdir(exist_ok=True)
expected='a311ac1bcecff89ff5e661a244c2d05441112023f095830e851de3a8973c241f'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source/'manifest.json')==expected
m=json.loads((source/'manifest.json').read_text());sums=json.loads((source/'SHA256SUMS.json').read_text())
stage=out/'sealed-release';assert not stage.exists(),'Preserve previously staged release'
for x in sums:
 p=source/x['file'];assert p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],x['file']
 q=stage/x['file'];q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert sha(q)==x['sha256']
shutil.copy2(source/'SHA256SUMS.json',stage/'SHA256SUMS.json');assert sha(source/'manifest.json')==expected and sha(stage/'manifest.json')==expected
project=root/'CampusCenter-vive/unreal/unreal_project'
inv=json.loads((root/'vr-preparation/vive-r15-scene-inventory.json').read_text());retire=[];unresolved=[]
for x in m['explicit_retirements']:
 matches=[a for a in inv['actors'] if a['label']==x['label'] and a['class']=='/Script/Engine.StaticMeshActor' and any(c.get('properties',{}).get('static_mesh')==x['mesh'] for c in a['components'])]
 if len(matches)!=1:unresolved.append({'label':x['label'],'mesh':x['mesh'],'matches':len(matches)})
 else:retire.append({'label':x['label'],'mesh':x['mesh'],'vive_actor_name_for_trace_only':matches[0]['name'],'before_transform':matches[0]['transform'],'before_hidden':matches[0]['hidden']})
existing=[];new=[]
for x in m['dependency_packages']:
 if x['new_namespace']:
  assert sha(stage/x['relative_file'])==x['sha256'];new.append({'package':x['package'],'target_exists':(project/x['relative_file']).exists()})
 else:
  p=project/x['relative_file'];h=sha(p) if p.exists() else None;existing.append({'package':x['package'],'relative_file':x['relative_file'],'exists':p.exists(),'release_sha256':x['sha256'],'vive_sha256':h,'byte_match':h==x['sha256']})
protected=json.loads((root/'vr-preparation/protected-baseline.json').read_text());assert all(sha(root/'CampusCenter-vive'/x['path'])==x['sha256'] for x in protected['files'])
frozen=json.loads((root/'vr-preparation/frozen-vive-r15.json').read_text());assert sha(Path(frozen['map_file']))==frozen['map_sha256']
report={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'release_path':str(source),'manifest_sha256':expected,'release_hashes_verified':len(sums),'staged_release':str(stage),'actor_recipes':len(m['new_actor_recipes']),'retirements':len(m['explicit_retirements']),'retirements_resolved_by_label_mesh':len(retire),'unresolved_retirements':unresolved,'dependencies_in_manifest':len(m['dependency_packages']),'new_namespace_packages':len(new),'new_namespace_target_conflicts':[x for x in new if x['target_exists']],'existing_dependencies':len(existing),'existing_dependency_byte_matches':sum(x['byte_match'] for x in existing),'existing_dependency_differences':[x for x in existing if not x['byte_match']],'protected_vive_files_unchanged':len(protected['files']),'frozen_r15_map_unchanged':True,'proposed_base_map':frozen['map'],'proposed_target_map':'/Game/Campus/Maps/CampusCenter_Vive_FA26_R03','acceptance':'Applicability preparation only; no Vive import, map creation, project overlay, cook or acceptance performed. Await explicit release validation. Differences require target-specific semantic proof before application.'}
(out/'applicability.json').write_text(json.dumps(report,indent=2));(out/'retirement-identities.json').write_text(json.dumps(retire,indent=2));(out/'existing-dependency-comparison.json').write_text(json.dumps(existing,indent=2))
print(json.dumps(report,indent=2))
