import bpy,json,pathlib,hashlib
from mathutils import Vector
R=pathlib.Path(__file__).parent;s=bpy.context.scene
rows=[]
for o in s.objects:
 if o.type!='MESH' or o.hide_render:continue
 pts=[o.matrix_world@Vector(p) for p in o.bound_box];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
 rows.append({'name':o.name,'lo':lo,'hi':hi,'materials':[m.name if m else None for m in o.data.materials],'collections':[c.name for c in o.users_collection]})
(R/'source_inventory.json').write_text(json.dumps({'source':bpy.data.filepath,'sha256':hashlib.sha256(pathlib.Path(bpy.data.filepath).read_bytes()).hexdigest(),'objects':rows,'camera':{'loc':list(s.camera.location),'rotation':list(s.camera.rotation_euler),'ortho_scale':s.camera.data.ortho_scale}},indent=2))
print('VISIBLE',len(rows))
for x in rows:
 if any(t in x['name'].lower() for t in ['table','desk','chair','locker','counter','bench','sink']):print(x['name'],[round(v,2) for v in x['lo']],[round(v,2) for v in x['hi']],x['materials'])
