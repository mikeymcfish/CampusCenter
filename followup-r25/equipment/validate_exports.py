import bpy,json,pathlib,hashlib,struct,math,bmesh
from mathutils import Vector
O=pathlib.Path(__file__).parent;m=json.loads((O/'replacement_manifest.json').read_text());results=[]
def bb(obs):
 bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();v=[o.matrix_world@p.co for o in obs for p in o.evaluated_get(deps).data.vertices];return [[min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)]]
# Reopened editable scene: validate donor geometry against isolated B05 source library.
donor_names=['RE07_PH02_Fitness218_'+n+'_0' for n in ('010','012','014','016','018','035','036')]
current={n:bpy.data.objects[n] for n in donor_names}
with bpy.data.libraries.load(str(O/'audit_b05.blend'),link=False) as (src,dst):dst.objects=list(donor_names)
donors=[]
for orig in dst.objects:bpy.context.scene.collection.objects.link(orig)
bpy.context.view_layer.update()
for name,orig in zip(donor_names,dst.objects):
 now=current[name];same=len(now.data.vertices)==len(orig.data.vertices) and len(now.data.polygons)==len(orig.data.polygons) and all((now.matrix_world@v.co-orig.matrix_world@w.co).length<1e-6 for v,w in zip(now.data.vertices,orig.data.vertices));donors.append({'object':name,'world_geometry_equal_B05':same,'vertices':len(now.data.vertices),'faces':len(now.data.polygons)})
(O/'donor_validation_diagnostic.json').write_text(json.dumps(donors,indent=2))
assert all(d['world_geometry_equal_B05'] for d in donors),donors
support=[]
for s in m['rack_support']:
 col=bpy.data.collections[s['rack_id']];shaft=current[s['donor_bench']];verts=[shaft.matrix_world@v.co for v in shaft.data.vertices];shaftpoints=[v for v in verts if v.z>5 and abs(v.z-s['shaft_yz'][1])<=.017]
 xmin,xmax=min(v.x for v in shaftpoints),max(v.x for v in shaftpoints)
 ledges=[o for o in col.objects if 'JcupLedge' in o.name];checks=[]
 for o in ledges:
  b=bb([o]);checks.append(b[0][0]<xmax and b[1][0]>xmin and b[0][1]<=s['shaft_yz'][0]<=b[1][1] and abs(b[1][2]-(s['shaft_yz'][1]-.016))<.001)
 support.append({'rack':s['rack_id'],'both_ledges_contact_shaft':all(checks),'ledge_count':len(ledges)})
assert all(s['both_ledges_contact_shaft'] and s['ledge_count']==2 for s in support)
standalone=[{'id':n,'max_world_z':max((o.matrix_world@v.co).z for v in o.data.vertices),'no_loaded_bar_geometry':max((o.matrix_world@v.co).z for v in o.data.vertices)<5} for n,o in current.items() if n.endswith(('035_0','036_0'))]
assert all(s['no_loaded_bar_geometry'] for s in standalone)
sourcebounds={r['id']:bb(list(bpy.data.collections[r['id']].objects)) for r in m['replacements']}
runtimebounds={r['file']:bb([bpy.data.objects[n] for n in r['source_parts']]) for r in m.get('runtime_joined_exports',[])}
def touches(a,b):
 x,y=bb([a]),bb([b]);return all(min(x[1][axis],y[1][axis])-max(x[0][axis],y[0][axis])>=-.00001 for axis in range(3))
mechanical=[]
for k in range(3,9):
 prefix=f'EQ27_PH02_Fitness218_{k:03d}_';checks=[]
 for side in (-1,1):
  for end in ('Rear','Front'):
   riser=bpy.data.objects[prefix+'LevelingRiser'+end+str(side)];checks += [touches(riser,bpy.data.objects[prefix+'Foot'+end+str(side)]),touches(riser,bpy.data.objects[prefix+'SideStep'+str(side)])]
 for j in (0,1):
  cross=bpy.data.objects[prefix+'DeckCrossmember'+str(j)];checks += [touches(cross,bpy.data.objects[prefix+'BeltDeck'])]+[touches(cross,bpy.data.objects[prefix+'SideStep'+str(s)]) for s in (-1,1)]
 mechanical.append({'assembly':prefix[:-1],'treadmill_feet_and_deck_supported':all(checks)})
for num in ('027','029','030'):
 prefix='EQ27_PH02_Fitness218_'+num+'_';post=bpy.data.objects[prefix+('SeatSupport' if num=='027' else 'SeatPost')];cross=bpy.data.objects[prefix+'SeatBaseCrossmember'];seat=bpy.data.objects[prefix+'Seat'];checks=[touches(post,cross),touches(post,seat)]+[touches(cross,bpy.data.objects[prefix+'BaseRail'+str(s)]) for s in (-1,1)];mechanical.append({'assembly':prefix[:-1],'seat_post_connected_to_base_and_pad':all(checks)})
assert all(all(val for key,val in r.items() if key!='assembly') for r in mechanical),mechanical
for path in sorted((O/'exports').glob('*.glb')):
 for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
 bpy.ops.import_scene.gltf(filepath=str(path));obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];actual=bb(obs)
 if path.name.endswith('_RuntimeJoined.glb'):expected=runtimebounds[path.name];count=1
 elif path.name.startswith('EQ27_'):expected=sourcebounds[path.stem.replace('_World','')];count=len(next(r for r in m['replacements'] if r['id']==path.stem.replace('_World',''))['parts'])
 elif path.name.startswith('Equipment_'):
  expected=[[min(b[i][axis] for b in sourcebounds.values()) if i==0 else max(b[i][axis] for b in sourcebounds.values()) for axis in range(3)] for i in range(2)];count=sum(r['parts_count'] for r in m['replacements'])
 else:expected=None;count=len(m['complete_legacy_export_parts'])
 mismatch=max(abs(actual[i][a]-expected[i][a]) for i in range(2) for a in range(3)) if expected else None
 valid=count==len(obs) and (mismatch is None or mismatch<.002)
 results.append({'file':path.name,'mesh_count':len(obs),'expected_mesh_count':count,'bounds_m':actual,'max_bound_error_m':mismatch,'roundtrip_pass':valid,'materials':sorted({mat.name.split('.')[0] for o in obs for mat in o.data.materials}),'bytes':path.stat().st_size})
 assert valid,results[-1]
(O/'validation.json').write_text(json.dumps({'editable_source_reopened':True,'donor_checks':donors,'rack_support_checks':support,'mechanical_support_checks':mechanical,'standalone_checks':standalone,'exports':results,'native_unreal_collision':'Pending isolated integration; policy documented, no runtime verification'},indent=2));print('VALIDATION_OK',len(results))
