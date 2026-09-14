from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).parent
D=Path('P:/_code/CampusCenter/printing/ground_4x_projection_v03')
assert json.loads((R/'validation.json').read_text())['status']=='passed'
assert json.loads((R/'scene_validation.json').read_text())['status']=='passed'
names=['README.md','Projection_Loop_Lossless_RGB.mp4','Projection_Loop_Preview.mp4','Projection_24_Images.zip','Projection_Hero_3x.png','Projection_Base_Top_Down.png','Projection_Base_Playback.png','Projection_Base_Detailed_3x.png','floor_only_mask.png','base_beauty_3x.png','Calibration_25mm_Floor_Only.png','Campus_Center_Lively_Projection.blend','Campus_Center_Detailed_Projection.blend','Fixed_Base_Compositor.blend','population_manifest.json','new_imagegen_prompts.json','walking_imagegen_prompts.json','render_contract.json','detail_report.json','validation.json','scene_validation.json','source_inventory.json','detail_render.py','mask_base.py','populate_projection.py','finish_and_verify.py','verify_scene.py','inspect_source.py','package_delivery.py']
files=[R/p for p in names]
for folder in ['frames','video_frames','imagegen_raw','assets']:files+=sorted((R/folder).glob('*.png'))
D.mkdir(parents=True,exist_ok=True);records=[]
for p in files:
    q=D/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    assert hashlib.sha256(q.read_bytes()).hexdigest()==h
    records.append({'file':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':h})
for root in [R,D]:(root/'DELIVERY_MANIFEST.json').write_text(json.dumps(records,indent=2))
root=D.parents[1]/'README.md';txt=root.read_text()
old='Current floor-only projection: [v02 direct top-down map, 24 Imagegen people frames and six-second loop](printing/ground_4x_projection_v02/README.md). Black walls and exterior; static lighting.'
new='Current floor-only projection: [v03 - 93 students, detailed court and furnishings, 24 fps loop and 24 reference images](printing/ground_4x_projection_v03/README.md). Black walls and exterior; static lighting.'
if old in txt:root.write_text(txt.replace(old,new))
elif new not in txt:root.write_text(txt+'\n\n'+new+'\n')
print(json.dumps({'delivered':str(D),'files_verified':len(records),'total_bytes':sum(r['bytes'] for r in records)},indent=2))
