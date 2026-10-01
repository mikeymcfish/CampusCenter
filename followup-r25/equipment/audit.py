import bpy,json,pathlib
from mathutils import Vector
out=pathlib.Path(__file__).parent
def bounds(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box]
 return [[min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]]
rows=[]
for o in bpy.data.objects:
 if any(k in o.name.lower() for k in ('fitness','weight','cardio','rackstation','bleacher','gym','treadmill','dumbbell')) or str(o.get('room','')) in ('218','217'):
  rows.append(dict(name=o.name,type=o.type,bounds=bounds(o),matrix=[list(r) for r in o.matrix_world],vertices=len(o.data.vertices) if o.type=='MESH' else 0,faces=len(o.data.polygons) if o.type=='MESH' else 0,materials=[m.name if m else None for m in o.data.materials] if o.type=='MESH' else [],props={k:str(v) for k,v in o.items()},collections=[c.name for c in o.users_collection]))
(out/'b05_inventory.json').write_text(json.dumps({'blender':bpy.app.version_string,'filepath':bpy.data.filepath,'scenes':[s.name for s in bpy.data.scenes],'units':bpy.context.scene.unit_settings.scale_length,'rows':rows},indent=2))
print('AUDIT_ROWS',len(rows))
