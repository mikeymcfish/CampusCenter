from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).parent;O=R/'output_v18';bpy.ops.wm.open_mainfile(filepath=str(O/'Campus_Center_Textured.blend'));s=bpy.context.scene
bpy.data.objects['V15_Janitor_washer'].location.y+=.55
bpy.data.objects['V15_Janitor_dryer'].location+=Vector((0,1.35,.9))
ob=bpy.data.objects['V15_Commons_round_dining_2'];base=ob.location.copy();bpy.context.view_layer.update()
def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])
def box(o):
 pts=[o.matrix_world@Vector(v) for v in o.bound_box];return ([min(p[k] for p in pts) for k in range(3)],[max(p[k] for p in pts) for k in range(3)])
lo,hi=box(ob);people=[p for p in s.objects if p.name.startswith('Student_') and all(lo[k]-.1<p.location[k]<hi[k]+.1 for k in [0,1]) and p.location.z<2]
others=[o for o in s.objects if o.type=='MESH' and o!=ob and not o.hide_render and (o.name.startswith('V15_Commons_') or o.name=='V8_DETAIL_Commons_plan_columns')];trees={o.name:tree(o) for o in others};chosen=None
for dy in [-1.4,-1.6,-1.8,-2.0]:
 ob.location=base+Vector((1.4,dy,0));bpy.context.view_layer.update();t=tree(ob);hits=[o.name for o in others if t.overlap(trees[o.name])]
 if not hits:chosen=(1.4,dy,0);break
assert chosen is not None
for p in people:p.location+=Vector(chosen)
a=json.loads((O/'changes.json').read_text());a['final_polish']={'laundry':'Washer moved clear of mop sink; dryer stacked on washer','dining_additional_translation':chosen,'associated_students':[p.name for p in people]};(O/'changes.json').write_text(json.dumps(a,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Campus_Center_Textured.blend'));print('POLISH_SAVED',chosen,flush=True)
