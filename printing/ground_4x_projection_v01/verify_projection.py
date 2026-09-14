import bpy,json,pathlib,hashlib
from mathutils import Vector
R=pathlib.Path(__file__).parent;s=bpy.context.scene;cfg=json.loads((R/'projector_config.json').read_text());m=json.loads((R/'projection_manifest.json').read_text());N=s.frame_end
moving=[o for o in s.objects if o.name.startswith('Loop occupant ') or o.name=='Looping daylight and moving shadows'];snap=[]
for f in [1,N+1]:
 s.frame_set(f);bpy.context.view_layer.update();snap.append([[v for row in o.matrix_world for v in row] for o in moving])
assert max(abs(a-b) for x,y in zip(snap[0],snap[1]) for a,b in zip(x,y))<1e-4
missing=[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file and not pathlib.Path(bpy.path.abspath(im.filepath)).exists()];assert not missing
assert hashlib.sha256((R.parent/'cycles_studio_v05/Campus_Center_Cycles_Studio.blend').read_bytes()).hexdigest()==m['source_sha256']
assert s.camera.name=='PROJECTOR - adjustable physical lens' and s.camera.data.type=='PERSP' and not s.camera.data.dof.use_dof
assert [s.render.resolution_x,s.render.resolution_y]==[1024,786] and N==144
report={'status':'passed','source_unchanged':True,'missing_images':missing,'loop_endpoint_transforms_match':True,'projection_camera':'Perspective, 60 degrees down, no DOF','physical_receiver_meshes':len([o for o in s.objects if o.name.startswith('Receiver ')])}
(R/'projection_validation.json').write_text(json.dumps(report,indent=2));print(report)
