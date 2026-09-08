from pathlib import Path
import shutil,hashlib,json
R=Path(__file__).parent;D=Path('P:/_code/CampusCenter/blender_cycles/v05');D.mkdir(parents=True,exist_ok=True)
assert json.loads((R/'scene_validation.json').read_text())['status']=='passed'
assert json.loads((R/'image_validation.json').read_text())['status']=='passed'
files=[R/x for x in ['Campus_Center_Cycles_Studio.blend','README.md','PROMPTS.md','build.py','verify.py','probe.py','render_stills.py','validate_images.py','deliver.py','preflight.json','build_report.json','scene_validation.json','image_validation.json']]
files+=[R/'render_contract.json']+list((R/'assets').glob('*.png'))+list((R/'stills').glob('*'))
for p in files:
 q=D/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
 assert hashlib.sha256(p.read_bytes()).digest()==hashlib.sha256(q.read_bytes()).digest()
readme=D.parents[1]/'README.md';text=readme.read_text();link='\nLatest Blender revision: [Cycles Studio v05 - student artwork, larger banners and modern fireplace](blender_cycles/v05/README.md).\n'
if 'blender_cycles/v05/README.md' not in text:readme.write_text(text+link)
report={'destination':str(D),'files_verified':len(files)};(R/'delivery.json').write_text(json.dumps(report,indent=2));print(report)
