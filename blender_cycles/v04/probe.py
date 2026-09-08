import bpy,json,pathlib,hashlib
from mathutils import Vector
R=pathlib.Path(__file__).parent;s=bpy.context.scene;s.frame_set(1);rows=[]
for o in s.objects:
 if o.type!='MESH':continue
 p=[o.matrix_world@Vector(v) for v in o.bound_box]
 rows.append({'name':o.name,'matrix':list(sum((list(r) for r in o.matrix_basis),[])),'verts':len(o.data.vertices),'faces':len(o.data.polygons),'materials':[m.name if m else None for m in o.data.materials],'hidden':o.hide_render,'bounds':[[min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]]})
mats={}
for name in ['Gray thin brick','Warm ivory facade brick','Natural oak','Warm white plaster','V02 Light blue matte interior paint']:
 m=bpy.data.materials.get(name)
 if m:mats[name]=[{'name':n.name,'type':n.type,'image':n.image.filepath if n.type=='TEX_IMAGE' and n.image else None} for n in m.node_tree.nodes]
(R/'preflight.json').write_text(json.dumps({'sha256':hashlib.sha256((R/'Source_Copy.blend').read_bytes()).hexdigest(),'objects':rows,'materials':mats,'engine':s.render.engine,'samples':s.cycles.samples,'camera':s.camera.name,'frames':[s.frame_start,s.frame_end]},indent=2));print('PREFLIGHT_COMPLETE',len(rows))
