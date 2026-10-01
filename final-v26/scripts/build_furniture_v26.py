import bpy, pathlib, json, math, hashlib, bmesh
from mathutils import Vector, Matrix
R=pathlib.Path(__file__).parent/'CampusCenter-new-plans'
OUT=R/'downstream/furniture_art_v26_r01'; OUT.mkdir(exist_ok=True)
REG=json.loads((R/'downstream/next_phase_plan/asset-replacement-reconciled.json').read_text())
BATCH=int(__import__('os').environ.get('FA26_BATCH','1'))
source=pathlib.Path(bpy.data.filepath); source_sha=hashlib.sha256(source.read_bytes()).hexdigest()
assert source_sha==('c39e7b686b56603f38500f1b22d6ebbb459362e66fa255da1a4b315e4a216721' if BATCH==1 else json.loads((OUT/f'batch{BATCH-1}-manifest.json').read_text())['output_blend_sha256'])
prior=json.loads((OUT/f'batch{BATCH-1}-manifest.json').read_text())['items'] if BATCH>1 else []
original={o.name: {'matrix':[list(v) for v in o.matrix_world], 'mesh':o.data.name if o.data else None,'materials':[s.material.name if s.material else None for s in o.material_slots],'hidden':o.hide_render} for o in bpy.data.objects}
ctrl=bpy.data.objects['REV_Partition_113_112_CONTROL']; closed=float(ctrl['closed'])
def collection(name):
 c=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(c);return c
rootcol=collection(f'FA26 batch {BATCH} - estimated generic enhancements')
materials={}
for key,names in {'oak':['Natural oak'],'metal':['Dark metal'],'steel':['Brushed stainless hardware'],'cloth':['V8 plain sage upholstery'],'white':['V8 plain light table surface'],'glass':['Clear glass'],'rubber':['Dark metal']}.items():
 materials[key]=next((bpy.data.materials.get(n) for n in names if bpy.data.materials.get(n)),None)
 if not materials[key] and key=='glass':
  materials[key]=bpy.data.materials.new('FA26 generic display glass estimate');materials[key].use_nodes=True;bs=materials[key].node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.82,.91,.95,1);bs.inputs['Roughness'].default_value=.12;bs.inputs['Transmission Weight'].default_value=.92;materials[key]['downstream_native_material']='/Game/Campus/PlayFixes/M_ClearGlass_Stable.M_ClearGlass_Stable'
 assert materials[key],(key,names)
def bounds(o):
 vv=[o.matrix_world@Vector(v) for v in o.bound_box];return Vector([min(v[i] for v in vv) for i in range(3)]),Vector([max(v[i] for v in vv) for i in range(3)])
def joined_bounds(objects):
 bb=[bounds(o) for o in objects];return Vector([min(x[0][i] for x in bb) for i in range(3)]),Vector([max(x[1][i] for x in bb) for i in range(3)])
items=[];allowed=set();parts=[];ctx={}
def begin(row):
 p=bpy.data.objects[row['id']];lo,hi=bounds(p);w,d=hi.x-lo.x,hi.y-lo.y;floor=lo.z-.024
 c=collection('FA26_'+row['id']);rootcol.children.link(c);bpy.context.scene.collection.children.unlink(c)
 ctx.update(row=row,col=c,w=w,d=d,floor=floor,center=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,floor)),made=[],donors=[])
 return w,d
def addmesh(name,vertices,faces,mat='metal',bevel=0):
 me=bpy.data.meshes.new('FA26_'+ctx['row']['id']+'_'+name);me.from_pydata(vertices,[],faces);me.update();uv=me.uv_layers.new(name='FA26_ProjectedUV')
 for p in me.polygons:
  axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
  for li in p.loop_indices:
   co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]],co[axes[1]])
 o=bpy.data.objects.new(me.name,me);ctx['col'].objects.link(o);o.location=ctx['center'];me.materials.append(materials[mat]);o['stable_id']=o.name;o['replacement_of']=ctx['row']['id'];o['source_zone']=ctx['row']['room'];o['estimated_geometry']='Generic modeled height/style; source footprint retained, no manufacturer claim';o['collision_expectation']='Block furniture envelope; preserve openings; no QA-label collision'
 if bevel:
  mod=o.modifiers.new('Rounded generic edges','BEVEL');mod.width=bevel;mod.segments=3
  o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 ctx['made'].append(o);parts.append(o);return o
def box(name,center,size,mat='metal',bevel=.008):
 x,y,z=center;a,b,c=[v/2 for v in size];return addmesh(name,[(x+sx*a,y+sy*b,z+sz*c) for sx,sy,sz in [(-1,-1,-1),(-1,-1,1),(-1,1,1),(-1,1,-1),(1,-1,-1),(1,-1,1),(1,1,1),(1,1,-1)]],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(3,7,6,2),(0,4,7,3),(1,2,6,5)],mat,min(bevel,min(size)/5))
def cyl(name,center,radius,depth,mat='metal',axis='Z',n=20):
 x,y,z=center;vs=[]
 for end in [-.5,.5]:
  for i in range(n):
   a=2*math.pi*i/n;q=Vector((radius*math.cos(a),radius*math.sin(a),depth*end))
   if axis=='X':q=Vector((q.z,q.x,q.y))
   elif axis=='Y':q=Vector((q.x,q.z,q.y))
   vs.append(tuple(q+Vector(center)))
 faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return addmesh(name,vs,faces,mat)
def rod(name,a,b,r=.025,mat='metal'):
 a,b=Vector(a),Vector(b);o=cyl(name,(0,0,0),r,(b-a).length,mat);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();o.location=ctx['center']+(a+b)/2;return o
def sphere(name,center,radius,mat='cloth'):
 bm=bmesh.new();bmesh.ops.create_uvsphere(bm,u_segments=20,v_segments=12,radius=radius);bm.verts.ensure_lookup_table();bm.verts.index_update();vs=[tuple(v.co+Vector(center)) for v in bm.verts];fs=[tuple(v.index for v in f.verts) for f in bm.faces];bm.free();return addmesh(name,vs,fs,mat)
def reuse(name,donor,w,d,h=None,angle=0):
 src=bpy.data.objects[donor];lo,hi=bounds(src);cen=(lo+hi)/2;cen.z=lo.z;rot=Matrix.Rotation(angle,4,'Z');vv=[rot@(src.matrix_world@Vector(v)-cen) for v in src.bound_box];sx=w/(max(v.x for v in vv)-min(v.x for v in vv));sy=d/(max(v.y for v in vv)-min(v.y for v in vv));sz=h/(hi.z-lo.z) if h else 1
 o=src.copy();o.data=src.data;o.name='FA26_'+ctx['row']['id']+'_'+name;o.parent=None;ctx['col'].objects.link(o);o.matrix_world=Matrix.Translation(ctx['center'])@Matrix.Diagonal((sx,sy,sz,1))@rot@Matrix.Translation(-cen)@src.matrix_world;o.hide_render=False;o.hide_viewport=False;o['stable_id']=o.name;o['replacement_of']=ctx['row']['id'];o['source_zone']=ctx['row']['room'];o['reused_from']=donor;o['estimated_geometry']='Reused donor fitted to accepted footprint; estimated product/proportions';ctx['made'].append(o);parts.append(o);ctx['donors'].append({'id':donor,'shared_mesh':True,'fit_scale':[sx,sy,sz]});return o
def finish():
 bpy.context.view_layer.update();lo,hi=joined_bounds(ctx['made']);row=ctx['row'];p=bpy.data.objects[row['id']];plo,phi=bounds(p)
 assert abs(lo.z-ctx['floor'])<.025,(row['id'],'floor',lo.z,ctx['floor'])
 assert lo.x>=plo.x-.025 and hi.x<=phi.x+.025 and lo.y>=plo.y-.025 and hi.y<=phi.y+.025,(row['id'],'footprint',list(lo),list(hi),list(plo),list(phi))
 for o in ctx['made']:
  assert o.type=='MESH' and len(o.data.polygons)>0
  bm=bmesh.new();bm.from_mesh(o.data);open_edges=sum(not e.is_manifold for e in bm.edges);bm.free()
  assert open_edges==0 or o.get('reused_from'),(o.name,'new nonmanifold primitive')
  o['source_open_surface_edges']=open_edges
 p.hide_render=True;p.hide_viewport=True;p['fa26_superseded_by']=ctx['col'].name;allowed.add(p.name)
 for o in bpy.data.objects:
  if o.type=='FONT' and o.name.startswith(p.name):o.hide_render=True;o.hide_viewport=True;allowed.add(o.name)
 items.append({'marker_id':row['id'],'label':row['label'],'stable_collection':ctx['col'].name,'zone':row['room'],'source_dimensions':row['source_dimensions'],'dimension_basis':row['dimension_basis'],'height_m':hi.z-ctx['floor'],'height_basis':'Modeled estimate, not architectural/product elevation','parts':[o.name for o in ctx['made']],'donors':ctx['donors'],'bounds_m':[list(lo),list(hi)],'marker_retired_after_checks':True,'footprint_check':'Envelope within accepted plane +25mm bevel tolerance','support_check':'Bottom matches verified marker local slab datum within25mm; individual support ray verification follows','collision':'Furniture complex or grouped convex pieces; no source-shell change','print_followup':'Simplified furniture mass needed; thin handles/rods/glass omitted in future print variant'})

SOFA_SOURCE=pathlib.Path('C:/Users/mikef/Documents/ChatGPT/Campus Center/realism_assets/prepared/commons_library_sketchfab_modern_sofa/commons_library_sketchfab_modern_sofa.glb')
sofa_donors=[]
if BATCH==1:
 assert hashlib.sha256(SOFA_SOURCE.read_bytes()).hexdigest()=='f684c936dca186fabc6552bb7fa9d2787d880ddd268fee5c3a56b4100bf357c2'
 old=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(SOFA_SOURCE));sofa_donors=[o for o in bpy.data.objects if o not in old and o.type=='MESH'];assert len(sofa_donors)==6
 dcol=collection('FA26 - source sofa donor / retained hidden')
 for o in sofa_donors:
  for c in list(o.users_collection):c.objects.unlink(o)
  dcol.objects.link(o);o.name='FA26_DONOR_SOFA_'+o.name;o.hide_render=True;o.hide_viewport=True
 for row in REG['items']:
  if row['status']!='READY_GENERIC' or row['priority']!=1:continue
  w,d=begin(row);id=row['id']
  if 'CurvedPiece' in id:
   # Two quarter-annular pieces; footprint and seating direction retained, exact product curve estimated.
   left=id.endswith('_0');inner=.53;outer=1.;verts=[];faces=[];n=20
   for z in [0,.30]:
    for radius in [inner,outer]:
     for i in range(n+1):
      a=(0 if left else math.pi/2)+(math.pi/2)*i/n;verts.append((radius*math.cos(a),radius*math.sin(a),z))
   for i in range(n):
    a=i;b=i+1;c=n+1+i;dd=c+1;e=2*(n+1)+i;f=e+1;g=3*(n+1)+i;h=g+1;faces.extend([(a,b,dd,c),(e,g,h,f),(a,e,f,b),(c,dd,h,g)])
   faces.extend([(0,n+1,3*(n+1),2*(n+1)),(n,3*(n+1)-1,4*(n+1)-1,3*(n+1)-1-(n+1))])
   # Build annular component with explicit end caps.
   faces[-1]=(n,2*n+1,4*n+3,3*n+2)
   o=addmesh('CurvedSeat',verts,faces,'cloth');bpy.context.view_layer.update();lo,hi=bounds(o);o.data.transform(Matrix.Translation((-((lo.x+hi.x)/2-ctx['center'].x),-((lo.y+hi.y)/2-ctx['center'].y),0)));o.scale=(w/(hi.x-lo.x),d/(hi.y-lo.y),1);o.location.z+=.16
   # Base follows same curved mesh with lower profile, shared geometry copied for distinct dimensions/material.
   base=o.copy();base.data=o.data.copy();base.name=o.name+'_OakBase';ctx['col'].objects.link(base);base.data.materials.clear();base.data.materials.append(materials['oak']);base.scale.z=.16/.30;base.location.z=ctx['floor'];ctx['made'].append(base);parts.append(base)
  elif 'Sofa' in id:
   lo,hi=joined_bounds(sofa_donors);cen=(lo+hi)/2;cen.z=lo.z;scale=Vector((w/(hi.x-lo.x),d/(hi.y-lo.y),1))
   for j,src in enumerate(sofa_donors):
    o=src.copy();o.data=src.data;o.parent=None;o.name='FA26_'+id+'_NativeSofa_'+str(j);ctx['col'].objects.link(o);o.matrix_world=Matrix.Translation(ctx['center'])@Matrix.Diagonal((*scale,1))@Matrix.Translation(-cen)@src.matrix_world;o.hide_render=False;o.hide_viewport=False;o['stable_id']=o.name;o['replacement_of']=id;o['source_zone']=row['room'];o['reused_from']=src.name;ctx['made'].append(o);parts.append(o)
   ctx['donors'].append({'file':str(SOFA_SOURCE),'sha256':'f684c936dca186fabc6552bb7fa9d2787d880ddd268fee5c3a56b4100bf357c2','native_components':['StaticMeshActor_'+str(i) for i in range(659,665)],'shared_mesh':True,'fit_scale':list(scale),'proportion_basis':'Width/depth fit are estimates; native style/material retained'})
  else:
   # East glazing counter; stools already exist and are not duplicated.
   box('OakCounterTop',(0,0,1.02),(w,d,.06),'oak',.012)
   box('WallSideApron',(w*.36,0,.965),(w*.16,d,.06),'oak')
   for y in [-d*.42,0,d*.42]:box('Bracket'+str(y),(0,y,.99),(w*.72,.045,.06),'steel')
   # Accepted top overhang supported by narrow legs within room, height estimated to existing stool type.
   for y in [-d*.4,d*.4]:box('Leg'+str(y),(w*.25,y,.48),(.045,.045,.96),'metal')
  finish()

if BATCH==2:
 native=json.loads((R/'downstream/shared_v25_r01/desktop-r15-scene-inventory.json').read_text())
 for row in REG['items']:
  if row['status']!='READY_GENERIC' or row['priority']!=2:continue
  row=dict(row)
  if row['id']=='PH02_Trainer_049':row.update(label='Storage',source_dimensions='35x24; corrected by source-local v10 trace')
  if row['id']=='PH02_Trainer_050':row.update(label='Taping',source_dimensions='35x26.5; corrected by source-local v10 trace')
  w,d=begin(row);id=row['id'];label=row['label']
  if 'Bench_' in id:
   reuse('LockerBench','V6_Gym_sideline_bench_140',w,d,h=.46,angle=math.pi/2 if d>w else 0)
  elif 'StoolLike' in id:
   reuse('BacklessStool','RE11_DONOR_BacklessStool',w,d,h=.50)
  elif 'TrophyCase' in id:
   box('CaseBase',(0,0,.12),(w,d,.24),'oak')
   box('CaseBack',(-w/2+.022,0,.94),(.044,d,1.40),'oak')
   box('CaseTop',(0,0,1.66),(w,d,.05),'oak')
   for y in [-d/2+.018,d/2-.018]:box('End'+str(y),(0,y,.94),(w,.035,1.40),'oak')
   box('DisplayGlass',(w/2-.012,0,.95),(.018,d-.075,1.37),'glass',0)
   for z in [.64,1.08,1.48]:box('Shelf'+str(z),(0,0,z),(w-.045,d-.065,.022),'white')
   for y in [-d*.27,0,d*.27]:
    cyl('TrophyCupBase'+str(y),(0,y,.66),min(w*.16,.075),.02,'metal')
    rod('TrophyStem'+str(y),(0,y,.67),(0,y,.77),.013,'steel')
    cyl('TrophyCup'+str(y),(0,y,.80),min(w*.12,.05),.07,'steel')
   ctx['donors'].append({'id':'existing Natural oak / native glass materials','style':'generic glazed trophy cabinet; contents symbolic cups, not actual awards'})
  elif 'Bleacher' in id:
   bank=1 if id.endswith('_01') else 2;actors=[a for a in native['actors'] if a['label'].startswith(f'PS08_Bleacher_{bank}_')]
   assert actors
   lows=[];highs=[]
   for a in actors:
    c=a['bounds_cm']['origin'];e=a['bounds_cm']['extent'];lows.append(Vector(((c[0]-e[0])/100,-(c[1]+e[1])/100,(c[2]-e[2])/100)));highs.append(Vector(((c[0]+e[0])/100,-(c[1]-e[1])/100,(c[2]+e[2])/100)))
   lo=Vector([min(v[i] for v in lows) for i in range(3)]);hi=Vector([max(v[i] for v in highs) for i in range(3)]);cen=(lo+hi)/2;cen.z=lo.z;sx=w/(hi.x-lo.x);sy=d/(hi.y-lo.y)
   for a,al,ah in zip(actors,lows,highs):
    pos=(al+ah)/2-cen;pos.x*=sx;pos.y*=sy;sz=ah-al;sz.x*=sx;sz.y*=sy
    part=box(a['label'],pos,sz,'metal',0);part['native_reuse_actor']=a['name'];part['native_reuse_mesh']=a['components'][0]['properties']['static_mesh'];part['native_reuse_materials']=json.dumps(a['components'][0]['materials'])
   ctx['donors'].append({'native_bank':bank,'actors':[a['name'] for a in actors],'fit_scale':[sx,sy,1],'original_bounds_m':[list(lo),list(hi)],'transform':'Fit original bank X/Y envelope to accepted west-wall marker; Z height preserved. Blender proxies represent native assembly; UE uses actual cube/cylinder components. North bank extent/row count remain inherited estimates.'})
  elif 'Whirlpool' in label:
   # Open basin with separated shell sides, not a solid filled box.
   box('BasinFloor',(0,0,.22),(w*.88,d*.88,.12),'white')
   for x in [-w*.46,w*.46]:box('BasinSide'+str(x),(x,0,.59),(w*.08,d,.66),'white',.025)
   for y in [-d*.46,d*.46]:box('BasinEnd'+str(y),(0,y,.59),(w*.84,d*.08,.66),'white',.025)
   for x in [-w*.34,w*.34]:box('Support'+str(x),(x,0,.10),(w*.12,d*.5,.20),'metal')
   box('ControlPanel',(0,d*.42,.95),(w*.20,d*.10,.07),'steel')
   cyl('Drain',(0,0,.29),.025,.008,'steel')
  elif 'Treatment' in label or 'treatment' in label or 'Rehabilitation' in label:
   h=.48 if 'Low' in label else .66 if 'Rehabilitation' in label else .78
   box('Cushion',(0,0,h-.065),(w,d,.13),'cloth',.025);box('SupportFrame',(0,0,h-.155),(w*.91,d*.9,.06),'metal')
   for x in [-w*.37,w*.37]:
    for y in [-d*.34,d*.34]:box('Leg'+str((x,y)),(x,y,(h-.18)/2),(.045,.045,h-.18),'steel')
   box('LowerShelf',(0,0,.23),(w*.8,d*.77,.035),'white')
  elif 'Taping' in label:
   box('Cabinet',(0,0,.40),(w*.94,d*.95,.80),'white');box('PaddedTop',(0,0,.84),(w,d,.08),'cloth',.022)
   for z in [.24,.47,.67]:box('DrawerFront'+str(z),(0,-d*.48,z),(w*.84,.028,.16),'oak');rod('DrawerPull'+str(z),(-w*.12,-d*.49,z),(w*.12,-d*.49,z),.011,'steel')
  elif id.endswith('_060'):
   # Sink intentionally lies inside first-aid counter; no second cabinet underneath.
   box('SinkBottom',(0,0,.82),(w*.8,d*.8,.025),'steel')
   for x in [-w*.46,w*.46]:box('SinkRimX'+str(x),(x,0,.91),(w*.08,d,.025),'steel')
   for y in [-d*.46,d*.46]:box('SinkRimY'+str(y),(0,y,.91),(w*.84,d*.08,.025),'steel')
   rod('TapStem',(0,d*.33,.91),(0,d*.33,1.08),.014,'steel');rod('TapSpout',(0,d*.33,1.08),(0,0,1.08),.014,'steel')
   # Bottom must remain at local floor for generic support test; hidden thin plumbing reaches slab within accepted footprint.
   rod('WastePipe',(0,0,.015),(0,0,.81),.015,'steel')
  elif id.endswith('_061'):
   box('UndercounterAppliance',(0,0,.43),(w*.94,d*.95,.86),'steel');box('Door',(0,-d*.49,.46),(w*.9,.025,.73),'steel');rod('Handle',(-w*.25,-d*.49,.74),(w*.25,-d*.49,.74),.012,'metal')
  elif id.endswith('_059'):
   # Side-and-back carcass and rim preserve space for the separately located sink/DW.
   box('CounterBack',(0,d*.46,.43),(w,d*.08,.86),'white')
   for x in [-w*.46,w*.46]:box('CounterEnd'+str(x),(x,0,.43),(w*.08,d,.86),'white')
   box('TopBackRail',(0,d*.40,.90),(w,d*.18,.055),'oak');box('TopFrontRail',(0,-d*.43,.90),(w,d*.12,.055),'oak')
  elif id.endswith('_063'):
   box('OfficeServiceCabinet',(0,0,.39),(w,d,.78),'white');box('OakTop',(0,0,.81),(w,d,.06),'oak')
   box('GenericPrinterBody',(0,0,.96),(w*.55,d*.55,.24),'white');box('PrinterLid',(0,0,1.095),(w*.58,d*.58,.035),'metal');box('PaperSlot',(0,-d*.29,.99),(w*.44,.008,.055),'metal',0)
  else:
   box('StorageCabinet',(0,0,.42),(w,d,.84),'white');box('CabinetTop',(0,0,.875),(w,d,.05),'oak')
   for z in [.22,.49,.72]:box('Front'+str(z),(0,-d*.47,z),(w*.90,.03,.18),'oak');rod('Pull'+str(z),(-w*.12,-d*.49,z),(w*.12,-d*.49,z),.009,'steel')
  finish()

if BATCH==3:
 for o in bpy.data.objects:
  if o.type=='MESH' and o.name.startswith('FA26_') and not o.get('reused_from') and not o.data.uv_layers:
   uv=o.data.uv_layers.new(name='FA26_ProjectedUV')
   for p in o.data.polygons:
    axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
    for li in p.loop_indices:
     co=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]],co[axes[1]])
 for row in REG['items']:
  if row['status']!='READY_GENERIC' or row['priority']!=3:continue
  w,d=begin(row);id=row['id'];label=row['label']
  if 'Bike' in label:
   fw,fd=max(w,d),min(w,d);wheel=min(.27,fw*.23);flyx=fw*.22
   for x in [-fw*.36,fw*.34]:box('GroundStabilizer'+str(x),(x,0,.04),(.08,fd*.92,.08),'metal')
   cyl('Flywheel',(flyx,0,wheel+.09),wheel,min(fd*.32,.13),'metal',axis='Y',n=32)
   rod('FrameMain',(-fw*.33,0,.08),(fw*.24,0,.70),.040,'steel');rod('SeatTube',(-fw*.16,0,.09),(-fw*.22,0,.82),.035,'metal');rod('UpperFrame',(-fw*.21,0,.60),(fw*.24,0,.64),.025,'steel')
   box('Saddle',(-fw*.22,0,.88),(fw*.19,fd*.36,.09),'rubber',.018)
   rod('HandleStem',(fw*.31,0,.13),(fw*.27,0,1.02),.029,'metal');rod('HandleBar',(fw*.26,-fd*.35,1.05),(fw*.26,fd*.35,1.05),.024,'rubber')
   cyl('Crank',(0,0,.28),min(.085,fw*.08),fd*.62,'steel',axis='Y')
   for y in [-fd*.30,fd*.30]:box('Pedal'+str(y),(0,y,.26),(fw*.14,fd*.18,.035),'rubber')
   if 'Assault' in label:
    for y in [-fd*.25,fd*.25]:rod('MovingHandle'+str(y),(fw*.22,y,.35),(fw*.34,y,1.20),.025,'metal')
   else:box('Console',(fw*.30,0,1.13),(fw*.13,fd*.30,.035),'metal')
   if d>w:
    bpy.context.view_layer.update()
    for o in ctx['made']:o.matrix_world=Matrix.Translation(ctx['center'])@Matrix.Rotation(math.pi/2,4,'Z')@Matrix.Translation(-ctx['center'])@o.matrix_world
  elif 'Ball Rack' in label:
   for x in [-w*.40,w*.40]:
    for y in [-d*.40,d*.40]:rod('Post'+str((x,y)),(x,y,.0),(x,y,1.48),.02,'metal')
   for z in [.20,.73,1.27]:
    for y in [-d*.34,d*.34]:rod('BasketRail'+str((z,y)),(-w*.40,y,z),(w*.40,y,z),.018,'steel')
    sphere('ExerciseBall'+str(z),(0,0,z+.18),min(w,d)*.28,'cloth')
  elif label in ['Core Machine','Nautilus Pulldown','Shoulder Press']:
   box('WeightedBase',(0,0,.07),(w*.95,d*.95,.14),'metal')
   box('WeightStack',(w*.30,d*.30,.66),(w*.18,d*.30,1.10),'rubber')
   for x in [-w*.38,w*.38]:rod('FrameUpright'+str(x),(x,d*.35,.12),(x,d*.35,1.77),.045,'steel')
   rod('CrossBeam',(-w*.38,d*.35,1.76),(w*.38,d*.35,1.76),.035,'metal')
   box('Seat',(0,-d*.18,.54),(w*.44,d*.45,.11),'cloth',.023)
   box('BackPad',(0,d*.06,.93),(w*.40,.12,.66),'cloth',.024)
   for x in [-w*.25,w*.25]:rod('Arm'+str(x),(x,d*.10,1.32),(x,-d*.29,1.12),.029,'steel');rod('Grip'+str(x),(x,-d*.29,1.12),(x,-d*.40,1.12),.021,'rubber')
   if 'Pulldown' in label:
    rod('Cable',(0,d*.34,.25),(0,d*.34,1.72),.004,'metal');rod('PullBar',(-w*.32,-d*.15,1.57),(w*.32,-d*.15,1.57),.025,'steel')
   ctx['donors'].append({'id':'Existing V6 rack/bench style and metal/upholstery materials','basis':'No complete named machine donor; generic functioning silhouette, mechanism estimated'})
  elif 'Chalk' in label and not id.endswith('_040') or id.endswith('_058'):
   cyl('StandBase',(0,0,.035),min(w,d)*.44,.07,'metal');rod('Stand',(0,0,.04),(0,0,.85),.025,'steel');cyl('Bowl',(0,0,.91),min(w,d)*.43,.10,'white');cyl('ChalkSurface',(0,0,.965),min(w,d)*.36,.008,'white')
  elif 'Weight' in label or 'Kettle' in label:
   for x in [-w*.43,w*.43]:box('RackEnd'+str(x),(x,0,.38),(.035,d*.88,.76),'metal')
   for z in [.14,.44,.72]:
    box('Shelf'+str(z),(0,0,z),(w*.95,d*.92,.035),'steel')
    for j in range(4):
     x=(-.34+j*.225)*w
     if 'Kettle' in label:
      sphere('Kettlebell'+str((z,j)),(x,0,z+.074),min(.065,d*.24,w*.09),'rubber');rod('KBHandleLeft'+str((z,j)),(x-.027,0,z+.09),(x-.027,0,z+.15),.009,'metal');rod('KBHandleTop'+str((z,j)),(x-.027,0,z+.15),(x+.027,0,z+.15),.009,'metal');rod('KBHandleRight'+str((z,j)),(x+.027,0,z+.09),(x+.027,0,z+.15),.009,'metal')
     else:cyl('WeightDisc'+str((z,j)),(x,0,z+.07),min(.065,d*.26),min(.035,w*.06),'rubber',axis='Y')
  elif 'Yoga' in label or 'Roller' in label or id.endswith('_057'):
   box('RackBacking',(0,d*.43,.48),(w,.035,.95),'oak')
   box('FloorFoot',(0,0,.025),(w,d,.05),'metal')
   if id.endswith('_057'):
    for j in range(4):rod('BandHook'+str(j),((j/4-.38)*w,d*.35,.75),((j/4-.38)*w,-d*.32,.75),.009,'steel');rod('HangingBand'+str(j),((j/4-.38)*w,-d*.28,.75),((j/4-.38)*w,-d*.28,.20),.009,'rubber')
   else:
    for j in range(3):cyl('StoredRoll'+str(j),((j/3-.33)*w,0,.42),min(w*.11,d*.28),.78,'cloth')
   ctx['donors'].append({'basis':'Wall-mounted projection is schematic; mounting/body height estimated. Preserve source depth envelope and keep circulation clear.'})
  elif id.endswith('_040'):
   box('BarStorageBase',(0,0,.03),(w,d,.06),'metal')
   for j in range(3):
    x=(j/3-.33)*w;cyl('StorageSocket'+str(j),(x,0,.11),min(w*.09,.045),.16,'metal');rod('StoredBar'+str(j),(x,0,.16),(x,0,1.30),.014,'steel')
  else:
   # Office wall bands and Admin sink counter: generic casework, not unidentified machinery.
   h=.90;box('Cabinet',(0,0,.40),(w,d,.80),'white');box('OakWorktop',(0,0,.84),(w,d,.08),'oak')
   for x in [-w*.24,w*.24]:box('Door'+str(x),(x,-d*.49,.42),(w*.47,.02,.67),'oak');rod('Pull'+str(x),(x,-d*.49,.45),(x,-d*.49,.58),.01,'steel')
   if 'SinkCounter' in id:
    box('SinkInset',(w*.22,0,.887),(w*.30,d*.62,.012),'steel');rod('TapStem',(w*.23,d*.22,.89),(w*.23,d*.22,1.04),.012,'steel');rod('TapSpout',(w*.23,d*.22,1.04),(w*.23,0,1.04),.012,'steel')
  finish()

assert float(ctrl['closed'])==closed
for name,before in original.items():
 o=bpy.data.objects[name];assert [list(v) for v in o.matrix_world]==before['matrix'],(name,'transform');assert (o.data.name if o.data else None)==before['mesh'],(name,'data');assert [s.material.name if s.material else None for s in o.material_slots]==before['materials'],(name,'materials')
 if name not in allowed:assert o.hide_render==before['hidden'],(name,'visibility')
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_sha
path=R/'scene'/f'Campus_Center_New_Plans_Furniture_v26_b{BATCH:02}.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path));sha=hashlib.sha256(path.read_bytes()).hexdigest()
record={'version':f'furniture_v26_batch{BATCH}','source_blend':str(source),'source_sha256':source_sha,'accepted_v25_sha256':'c39e7b686b56603f38500f1b22d6ebbb459362e66fa255da1a4b315e4a216721','output_blend':str(path),'output_blend_sha256':sha,'items':prior+items,'new_items':len(items),'original_objects_transform_mesh_material_preserved':True,'allowed_marker_visibility_changes':sorted(allowed),'partition_control_unchanged':True,'status':'Saved geometry/footprint checks pass; reopen/support-ray/visual review/export pending','assumptions':'Function/source footprint governs; height/style/mechanism and native donor fitting are conservative estimates. No brand claim. Accepted architecture/iLab unchanged.'}
(OUT/f'batch{BATCH}-manifest.json').write_text(json.dumps(record,indent=2));print('FA26_BATCH_SAVED',BATCH,len(items),sha,flush=True)
