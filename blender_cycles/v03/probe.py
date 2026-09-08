import bpy,json,pathlib,hashlib
from mathutils import Vector
R=pathlib.Path(__file__).parent;s=bpy.context.scene
rows=[]
for o in s.objects:
 if o.type!='MESH':continue
 p=[o.matrix_world@Vector(v) for v in o.bound_box]
 rows.append({'name':o.name,'matrix':list(sum((list(r) for r in o.matrix_world),[])),'verts':len(o.data.vertices),'faces':len(o.data.polygons),'materials':[m.name if m else None for m in o.data.materials],'hidden':o.hide_render,'bounds':[[min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]]})
(R/'preflight.json').write_text(json.dumps({'sha256':hashlib.sha256((R/'Source_Copy.blend').read_bytes()).hexdigest(),'objects':rows,'engine':s.render.engine,'samples':s.cycles.samples,'camera':s.camera.name,'frames':[s.frame_start,s.frame_end]},indent=2))
print('PREFLIGHT_COMPLETE',len(rows))
