"""Read-only saved-scene audit. No blend save, export, geometry edits or new objects."""
from pathlib import Path
import bpy,json,hashlib,math,random,time
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).parent;O=R/'output_v18';O.mkdir(exist_ok=True);Q=O/'views';Q.mkdir(exist_ok=True)
src=R/'output_v18/Campus_Center_Textured.blend';sha=hashlib.sha256(src.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;s.frame_set(1);deps=bpy.context.evaluated_depsgraph_get()
rooms=json.loads((R/'output_3d_v4/room_schedule.json').read_text());items=[];trees={};lookup={}
for ob in s.objects:
 if ob.type!='MESH':continue
 p=[ob.matrix_world@Vector(v) for v in ob.bound_box];lo=[min(v[i] for v in p) for i in range(3)];hi=[max(v[i] for v in p) for i in range(3)]
 row=dict(name=ob.name,lo=lo,hi=hi,collections=[c.name for c in ob.users_collection],hidden=ob.hide_render or any(c.hide_render for c in ob.users_collection),vertices=len(ob.data.vertices),faces=len(ob.data.polygons),props={k:str(ob[k]) for k in ob.keys()});items.append(row);lookup[ob.name]=row
def tree(name):
 if name not in trees:
  ob=bpy.data.objects[name];ev=ob.evaluated_get(deps);me=ev.to_mesh();trees[name]=BVHTree.FromPolygons([ob.matrix_world@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons]);ev.to_mesh_clear()
 return trees[name]
walls=[r for r in items if any(c in ['GROUND','UPPER','GYM','V6_ARCHITECTURE','V8_ARCHITECTURE'] for c in r['collections']) and not r['hidden'] and any(x in r['name'].lower() for x in ['wall','partition','column','pier','_end']) and r['hi'][2]-r['lo'][2]>.8 and not any(x in r['name'].lower() for x in ['trim','gasket','sign','wood_base','door','ceiling'])]
floors=[r for r in items if not r['hidden'] and any(x in r['name'].lower() for x in ['slab','floor','landing','tread','patio','terrace']) and r['hi'][2]-r['lo'][2]<.8]
def downward(x,y,z,rows,ignore='',maxdist=5):
 best=None
 for r in rows:
  if r['name']==ignore or r['hidden'] or not(r['lo'][0]-.001<=x<=r['hi'][0]+.001 and r['lo'][1]-.001<=y<=r['hi'][1]+.001) or r['lo'][2]>z:continue
  p,n,i,d=tree(r['name']).ray_cast(Vector((x,y,z)),Vector((0,0,-1)),maxdist)
  if p is not None and (best is None or d<best['distance']):best={'object':r['name'],'distance':d,'height':p.z,'normal_z':n.z}
 return best
def room_for(r):
 x=(r['lo'][0]+r['hi'][0])/2;y=(r['lo'][1]+r['hi'][1])/2;z=r['lo'][2];floor='UPPER' if z>3.9 else 'GROUND'
 candidates=[q for q in rooms if q['floor']==floor and q['number']!='GYM']
 return min(candidates,key=lambda q:(q['center_mm'][0]/1000-x)**2+(q['center_mm'][1]/1000-y)**2)['number']
# Floor-standing furniture and equipment: bottom-of-object contact with external support.
targets=[r for r in items if not r['hidden'] and (any(c in ['V5_FURNITURE','V6_FURNITURE','V8_FURNITURE','V8_EQUIPMENT','V9 Lab Technology','V9 Manufacturer CAD Equipment','V15 Plan furniture','V15 Cafe equipment','V15 Lockers','V6_FIXTURES','V8_FIXTURES','V15 Plumbing fixtures'] for c in r['collections']) or r['name'].startswith('Student_'))]
support_flags=[];support_samples=[]
for r in targets:
 if r['hi'][2]-r['lo'][2]<.12:continue
 ob=bpy.data.objects[r['name']];zs=r['lo'][2];points=[]
 for v in ob.data.vertices:
  p=ob.matrix_world@v.co
  if p.z<zs+.008:points.append(p)
 if not points:continue
 picks=points[::max(1,len(points)//8)][:12];hits=[downward(p.x,p.y,zs+.015,items,r['name'],maxdist=5) for p in picks]
 valid=[h for h in hits if h];gap=min(h['distance']-.015 for h in valid) if valid else None
 row={'object':r['name'],'room_nearest':room_for(r),'bottom_z':zs,'min_support_gap_m':gap,'support':min(valid,key=lambda h:h['distance']) if valid else None}
 support_samples.append(row)
 if gap is None or gap>.10:support_flags.append(row)
print('SUPPORT_DONE',len(targets),len(support_flags),flush=True)
# Narrow phase surface intersections: furniture/people against actual wall/column meshes.
intersections=[]
for r in targets:
 if r['hi'][2]-r['lo'][2]<.2:continue
 for w in walls:
  if r['name']==w['name'] or any(min(r['hi'][k],w['hi'][k])-max(r['lo'][k],w['lo'][k])<.015 for k in range(3)):continue
  overlap=tree(r['name']).overlap(tree(w['name']))
  if overlap:intersections.append({'object':r['name'],'wall':w['name'],'room_nearest':room_for(r),'triangle_pairs':len(overlap),'bbox_overlap_m':[min(r['hi'][k],w['hi'][k])-max(r['lo'][k],w['lo'][k]) for k in range(3)]})

(O/'refined_checks.json').write_text(json.dumps(dict(support_flags=support_flags,intersections=intersections),indent=2))
print('REFINED_DONE',len(support_flags),len(intersections),flush=True)

samples=json.loads((O/'walkthrough_route.json').read_text())['samples'];hits=[]
for frame in range(0,len(samples),6):
 p=Vector(samples[frame]['p']);names=set()
 for r in items:
  if r['hidden'] or any(c in ['ROOM_LABELS','PRESENTATION'] for c in r['collections']):continue
  for zoffset in [0,.75]:
   q=p-Vector((0,0,zoffset))
   if any(q[k]<r['lo'][k]-.16 or q[k]>r['hi'][k]+.16 for k in range(3)):continue
   nearest=tree(r['name']).find_nearest(q,.16)
   if nearest[0] is not None:names.add(r['name'])
 if names:hits.append(dict(frame=frame+1,segment=samples[frame]['segment'],p=list(p),objects=sorted(names)))
(O/'route_collisions.json').write_text(json.dumps(hits,indent=2));print('ROUTE_COLLISIONS',len(hits),flush=True)
