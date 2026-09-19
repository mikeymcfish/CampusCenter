from pathlib import Path
import json,sys,hashlib
import numpy as np
from PIL import Image
R=Path(__file__).parent;D=R/'print'
sys.path.insert(0,str(R.parent/'projection_furnished_v04/python_packages'))
import trimesh,manifold3d as mf
from print_edits_r08 import regions

def man(m):return mf.Manifold(mf.Mesh(np.asarray(m.vertices,np.float32),np.asarray(m.faces,np.uint32)))
old=man(trimesh.load_mesh(R/'revision_08_before/print/Campus_Center_Ground_Acrylic_1_87p5.stl'))
new=man(trimesh.load_mesh(D/'Campus_Center_Ground_Acrylic_1_87p5.stl'))
cuts=mf.Manifold.batch_boolean([mf.Manifold.cube(tuple(np.array(q['hi'])-q['lo'])).translate(tuple(q['lo'])) for q in regions(R.parent)],mf.OpType.Add)
removed=old-new;added=new-old
assert added.volume()<.1
assert (removed-cuts).volume()<.1
assert (new^cuts).volume()<.1
lower=mf.Manifold.cube((1000,1000,4.8)).translate((-1,-1,0))
assert ((old^lower)-(new^lower)).volume()<.1
oldrows=json.loads((R/'revision_08_before/print/print_validation.json').read_text())['tiles']
newrows=json.loads((D/'print_validation.json').read_text())['tiles']
changed=[b['name'] for a,b in zip(oldrows,newrows) if abs(a['volume_mm3']-b['volume_mm3'])>.1]

# Exact same camera and mask as before; update only the gym raw rendering.
room=R/'rooms/GYM'
mask=Image.open(room/'Room_Mask_1024.png').convert('L')
im=Image.open(room/'topdown_raw.png').convert('RGB')
rgba=im.convert('RGBA');rgba.putalpha(mask);rgba.save(room/'Topdown_Alpha.png')
black=Image.new('RGB',im.size);black.paste(im,(0,0),mask);black.save(room/'Topdown_Black.png')
assert np.array(black)[np.array(mask)==0].max()==0
prompt=room/'H3_Loop_Prompt.txt';s=prompt.read_text(encoding='utf-8')
s=s.replace('No camera motion,','No bleachers: the gym reference matches the revised print with both bleacher banks removed. No camera motion,')
prompt.write_text(s,encoding='utf-8')

note='''\n## r08 print correction\n\nThe innovation-lab patio is open at its free edges. Its platform and adjacent building walls are preserved. Both three-row gym bleacher banks are removed. All six print tiles remain single connected, watertight solids, with no elevated downward-facing faces. The scale, assembly registration, 40 acrylic pane dimensions and 1.85 mm slots remain unchanged. Updated masks, previews and projection videos match this geometry. The full architectural Blender source remains unchanged.\n'''
for p in [R/'README.md',D/'README.md',R/'projection/README.md']:
    s=p.read_text(encoding='utf-8')
    if '## r08 print correction' not in s:p.write_text(s+note,encoding='utf-8')
p=D/'README.md';s=p.read_text().replace('and stair/patio guardrails are not windows and remain as previously modeled.','and stair guardrails are not windows. The patio enclosure is removed in r08.')
p.write_text(s,encoding='utf-8')
report={'revision':'r08','old_print_sha256':hashlib.sha256((R/'revision_08_before/print/Campus_Center_Ground_Acrylic_1_87p5.stl').read_bytes()).hexdigest(),'new_print_sha256':hashlib.sha256((D/'Campus_Center_Ground_Acrylic_1_87p5.stl').read_bytes()).hexdigest(),'bleacher_rows_removed':6,'patio_enclosure_removed':True,'outside_edit_regions_unchanged':True,'floor_and_platform_below_4p8mm_unchanged':True,'added_volume_mm3':added.volume(),'removed_volume_mm3':removed.volume(),'changed_tiles':changed,'scale':'1:87.5','pane_count':40,'physical_print_tested':False}
(R/'revision_08_validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
