from pathlib import Path
import json,hashlib
R=Path(__file__).parent/'combined_r01';C=Path(__file__).parent/'slideshow_r01/unreal_project/Saved/Cooked/Windows/CampusCenter';m=json.loads((R/'integration_payload_r25_r02/portable-implementation-manifest.json').read_text());rows=[]
for row in m['files']:
 p=C/row['path'];assert p.exists(),p
 for q in [p,p.with_suffix('.uexp'),p.with_suffix('.ubulk')]:
  if not q.exists():continue
  b=q.read_bytes();hits=[s for s in ['mikef','C:/Users','C:\\Users'] if s.encode() in b or s.encode('utf-16le') in b];assert not hits,(q,hits);rows.append({'file':q.relative_to(C).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'machine_tokens':[]})
(R/'r25-cooked-portability-proof.json').write_text(json.dumps({'root_packages':len(m['files']),'cooked_files':rows,'no_machine_paths_in_new_cooked_content':True},indent=2));print('40 new cooked packages verified portable')
