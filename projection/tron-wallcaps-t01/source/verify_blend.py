import bpy,json,numpy as np,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'source'))
from inspect_receiver import parse_obj,sha,OBJ,ORIGINAL_SRC
path=ROOT/'deliverables/Tron_UV02_Receiver_Preview.blend'
bpy.ops.wm.open_mainfile(filepath=str(path));v,u,parts=parse_obj(OBJ);checks=[]
for ob in bpy.context.scene.objects:
    if ob.type!='MESH':continue
    p=parts[ob.name];f=np.array([x.vertices[:] for x in ob.data.polygons]);w=np.array([ob.matrix_world@x.co for x in ob.data.vertices]);uv=np.array([x.uv[:] for x in ob.data.uv_layers.active.data]).reshape(-1,3,2)
    ce=float(abs(w[f]-v[p['f']]).max());ue=float(abs(uv-u[p['ft']]).max());assert ce<.0001 and ue<1e-6
    checks.append({'part':ob.name,'faces':len(f),'world_error_mm':ce,'UV_error_pixels':ue*8192})
assert len(checks)==4
report={'saved_blend_reopened':True,'parts':checks,'scene_camera':bpy.context.scene.camera.name,'packed_images':[x.name for x in bpy.data.images if x.packed_file], 'source_receiver_still_matches_copy':sha(ORIGINAL_SRC/OBJ.name)==sha(OBJ),'original_receiver_sha256':sha(ORIGINAL_SRC/OBJ.name),'geometry_and_UV_unchanged':True,'physical_projection_test':False}
(ROOT/'qa/Saved_Project_Reopen_QA.json').write_text(json.dumps(report,indent=2));print('SAVED PROJECT REOPEN PASS',flush=True)
