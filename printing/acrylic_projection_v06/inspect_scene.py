import bpy,json,pathlib,hashlib
from mathutils import Vector
R=pathlib.Path(__file__).parent;s=bpy.context.scene;s.frame_set(1)
rows=[]
for o in s.objects:
 if o.type!='MESH':continue
 v=[o.matrix_world@Vector(p) for p in o.bound_box]
 rows.append({'name':o.name,'bounds':[[min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)]],'collections':[c.name for c in o.users_collection],'hidden':o.hide_render,'materials':[m.name if m else None for m in o.data.materials]})
images=[{'name':i.name,'packed':bool(i.packed_file),'path':i.filepath,'size':list(i.size)} for i in bpy.data.images if i.source=='FILE']
src=R.parent/'cycles_studio_v05/Campus_Center_Cycles_Studio.blend'
(R/'scene_inventory.json').write_text(json.dumps({'source':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'blender_version':bpy.app.version_string,'objects':rows,'images':images,'render_engine':s.render.engine,'camera':s.camera.name,'collections':[c.name for c in bpy.data.collections]},indent=2))
print('SCENE_INVENTORY',len(rows),len(images),flush=True)
