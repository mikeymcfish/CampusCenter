import bpy,bmesh,json,math,pathlib,hashlib,time
from mathutils import Vector,Matrix
O=pathlib.Path(__file__).parent
ROOT=pathlib.Path('C:/Users/mikef/Documents/Codex/2026-09-30/task/CampusCenter-new-plans')
items={i['id']:i for i in json.loads((ROOT/'revision-evidence/v02-footprints.json').read_text())}
inventory=json.loads((O/'b05_inventory.json').read_text())
source_hash=hashlib.sha256((ROOT/'scene/Campus_Center_New_Plans_Furniture_v26_b05.blend').read_bytes()).hexdigest()
assert source_hash=='3013db5f7f8171b403bd5fac8561c84e24591875aa049683f950c3ee4e19e56e'
oldnames=[o.name for o in bpy.data.objects if o.name.startswith(('RE07_PH02_Fitness218_','FA26_PH02_Fitness218_','FA26_PH10_Fitness218_'))]
oldcopies={}
for n in oldnames:
 o=bpy.data.objects[n];c=o.copy();c.data=o.data.copy();c.matrix_world=o.matrix_world.copy();oldcopies[n]=c
materials={n:bpy.data.materials.get(n) for n in ['Dark metal','V8 plain rubber','V8 plain sage upholstery','Brushed stainless hardware','V8 plain dark screen']}
print('MATERIALS',[(k,bool(v)) for k,v in materials.items()])
def mat(n,col,metal=0,rough=.5):
 m=materials.get(n) or bpy.data.materials.new(n);m.diffuse_color=(*col,1);m.use_nodes=True
 m.node_tree.nodes.clear();bs=m.node_tree.nodes.new('ShaderNodeBsdfPrincipled');output=m.node_tree.nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(bs.outputs['BSDF'],output.inputs['Surface']);bs.inputs['Base Color'].default_value=(*col,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough;materials[n]=m;return m
steel=mat('Dark metal',(.075,.09,.105),.7,.3)
rubber=mat('V8 plain rubber',(.022,.028,.033),0,.75)
pad=mat('V8 plain sage upholstery',(.26,.37,.32),0,.65)
chrome=mat('Brushed stainless hardware',(.46,.51,.55),.85,.28)
screen=mat('V8 plain dark screen',(.01,.018,.024),.15,.22)
# Only the staging scene is stripped. No save to the input copy or frozen source.
for o in list(bpy.data.objects):
 if o not in oldcopies.values():bpy.data.objects.remove(o,do_unlink=True)
for n,c in oldcopies.items():c.name=n
sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
groups={};records=[];active=None
def choose(num,old):
 global active
 ident='EQ27_PH02_Fitness218_'+num;active=bpy.data.collections.new(ident);sc.collection.children.link(active);groups[num]=active
 it=items['PH02_Fitness218_'+num]
 records.append({'id':ident,'source_marker':it['id'],'label':it['label'],'raw_annotation':it['raw_dimension_annotation'],'accepted_position_m':it['position_m'],'accepted_footprint_m':it['footprint_m'],'replaces_objects':old,'dimension_status':'Footprint traced from approved plan; all mechanics, sections and heights are estimates, no manufacturer certification','parts':[]})
 return it
def finish(o,n,m):
 o.name=active.name+'_'+n
 for c in list(o.users_collection):c.objects.unlink(o)
 active.objects.link(o);o.data.materials.clear();o.data.materials.append(m)
 o['replacement_id']=active.name;o['dimension_status']='Estimated representative mechanics; approved footprint';o['source_zone']='U218';o['collision_policy']='CTF_USE_COMPLEX_AS_SIMPLE; QUERY_AND_PHYSICS; preserve openings'
 records[-1]['parts'].append(o.name)
 return o
def box(n,p,s,m=steel,bevel=.008):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(o,n,m)
 if bevel:
  mod=o.modifiers.new('Editable edge radii','BEVEL');mod.width=min(bevel,min(s)*.22);mod.segments=2
 return o
def rod(n,a,b,r=.025,m=steel,segments=24):
 a,b=Vector(a),Vector(b);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=segments,radius=r,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();finish(o,n,m)
 for f in o.data.polygons:f.use_smooth=len(f.vertices)==4
 return o
def beam(n,a,b,w=.06,m=steel):
 a,b=Vector(a),Vector(b);o=box(n,(a+b)/2,(w,w,(b-a).length),m);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def reuse(n):
 c=oldcopies[n];active.objects.link(c);c.hide_render=False;c.hide_viewport=False;c.hide_set(False);c['replacement_id']=active.name;c['donor_preservation']='B05 corrected mesh and world transform unchanged';records[-1]['parts'].append(c.name);return c
def B(o):
 bpy.context.view_layer.update();v=[o.matrix_world@Vector(p) for p in o.bound_box];return [[min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)]]
def union(objects):
 bb=[B(o) for o in objects];return [[min(b[0][i] for b in bb) for i in range(3)],[max(b[1][i] for b in bb) for i in range(3)]]
# Six treadmills: keep the accepted silhouette and original height envelope.
for k in range(3,9):
 num=f'{k:03d}';it=choose(num,[f'RE07_PH02_Fitness218_{num}_{j}' for j in (0,1)]);x,y,z=it['position_m'];w,d=it['footprint_m'];front=y+d/2;back=y-d/2
 box('BeltDeck',(x,y,z+.14),(w*.77,d*.89,.1),rubber,.012)
 box('RunningBelt',(x,y-.025,z+.197),(w*.68,d*.82,.015),rubber,.003)
 for s in (-1,1):
  xx=x+s*w*.445;box('SideStep'+str(s),(xx,y,z+.16),(w*.10,d*.95,.075),steel)
  box('FootRear'+str(s),(xx,back+.09,z+.025),(.065,.14,.05),rubber)
  box('FootFront'+str(s),(xx,front-.11,z+.025),(.065,.14,.05),rubber)
  box('LevelingRiserRear'+str(s),(xx,back+.09,z+.09),(.045,.09,.08),steel)
  box('LevelingRiserFront'+str(s),(xx,front-.11,z+.09),(.045,.09,.08),steel)
  beam('Upright'+str(s),(xx,front-.28,z+.12),(xx,front-.10,z+1.04),.06)
  beam('Handrail'+str(s),(xx,front-.10,z+.96),(xx,y+.12,z+.86),.04)
  rod('Grip'+str(s),(xx,y+.12,z+.86),(xx,y-.08,z+.86),.025,rubber)
 rod('RearRoller',(x-w*.385,back+.14,z+.14),(x+w*.385,back+.14,z+.14),.06,chrome)
 for j,yy in enumerate((back+.15,front-.22)):box('DeckCrossmember'+str(j),(x,yy,z+.12),(w*.89,.065,.065),steel)
 rod('FrontRoller',(x-w*.385,front-.16,z+.14),(x+w*.385,front-.16,z+.14),.06,chrome)
 box('MotorCover',(x,front-.16,z+.28),(w*.72,.21,.20),steel,.035)
 box('ConsoleBridge',(x,front-.10,z+1.03),(w*.91,.11,.07),steel)
 console=box('ConsoleHousing',(x,front-.11,z+1.15),(w*.82,.12,.18),steel,.02);console.rotation_euler.x=math.radians(16)
 disp=box('BlankDisplay',(x,front-.177,z+1.17),(w*.5,.014,.10),screen,.005);disp.rotation_euler.x=math.radians(16)
 for s in (-1,1):box('ControlButton'+str(s),(x+s*w*.32,front-.18,z+1.115),(.028,.015,.026),pad,.003)
 box('EmergencyKey',(x,front-.183,z+1.087),(.025,.018,.018),rubber,.003)
# Five racks: retain corrected donor bench and loaded shaft; replace solid panels with tubes.
support=[]
for k in (9,11,13,15,17):
 num=f'{k:03d}';bench=f'RE07_PH02_Fitness218_{k+1:03d}_0';it=choose(num,[f'RE07_PH02_Fitness218_{num}_{j}' for j in range(3)]+[bench]);x,y,z=it['position_m'];w,d=it['footprint_m'];c=reuse(bench)
 verts=[c.matrix_world@v.co for v in c.data.vertices];bar=[v for v in verts if v.z>5]
 by=sum(v.y for v in bar)/len(bar);bz=(min(v.z for v in bar)+max(v.z for v in bar))/2
 # The shaft centre is the centre of the bar's thickness, not the plates' top.
 bz=(min(v.z for v in bar)+max(v.z for v in bar))/2
 cols=[]
 for s in (-1,1):
  old=oldcopies[f'RE07_PH02_Fitness218_{num}_{0 if s<0 else 1}'];bb=B(old);xx=(bb[0][0]+bb[1][0])/2;rear=y+d/2-.085
  box('BaseRail'+str(s),(xx,y,z+.045),(.08,d-.02,.09),steel)
  for j,yy in enumerate((by,rear)):
   box(f'Foot{s}_{j}',(xx,yy,z+.022),(.083,.16,.044),rubber)
   box(f'Upright{s}_{j}',(xx,yy,z+.970),(.074,.074,1.84),steel)
   for zz in (.35,.5,.65,.8,.95,1.1,1.25,1.4,1.55):
    rod(f'AdjustmentPort{s}_{j}_{zz}',(xx-.039,yy,z+zz),(xx+.039,yy,z+zz),.009,rubber,12)
  beam('UpperSide'+str(s),(xx,by,z+1.87),(xx,rear,z+1.87),.07)
  beam('SafetyRail'+str(s),(xx,by,z+.67),(xx,rear,z+.67),.045)
  # Horizontal ledge top meets shaft underside; raised stop sits behind shaft.
  box('JcupLedge'+str(s),(xx,by,bz-.016-.014),(.10,.12,.028),chrome,.002)
  box('JcupBacking'+str(s),(xx,by+.042,bz+.023),(.085,.022,.12),steel,.003)
  box('JcupLip'+str(s),(xx,by-.051,bz-.012),(.10,.012,.035),rubber,.002)
  cols.append(xx)
 rod('RearPullupCrossbar',(cols[0],rear,z+1.85),(cols[1],rear,z+1.85),.024)
 beam('RearLowBrace',(cols[0],rear,z+.13),(cols[1],rear,z+.13),.065)
 support.append({'rack_id':active.name,'donor_bench':bench,'shaft_yz':[by,bz],'upright_x':cols,'ledge_top_z':bz-.016,'shaft_radius_m':.016,'check':'Two ledges contact underside of retained shaft; upright at shaft Y; retained B05 bar mesh unchanged'})
# Core, lat pulldown and shoulder press: individual mechanisms, not shared box shape.
for num in ('027','029','030'):
 old=[n for n in oldnames if n.startswith('FA26_PH02_Fitness218_'+num+'_')];it=choose(num,old);x,y,z=it['position_m'];w,d=it['footprint_m'];rear=y+d*.35
 for s in (-1,1):
  xx=x+s*w*.36;box('BaseRail'+str(s),(xx,y,z+.055),(.07,d*.91,.09))
  for yy in (y-d*.4,y+d*.4):box('RubberFoot'+str((s,yy)),(xx,yy,z+.022),(.10,.13,.044),rubber)
 beam('BaseCrossbar',(x-w*.36,rear,z+.08),(x+w*.36,rear,z+.08),.07)
 beam('SeatBaseCrossmember',(x-w*.36,y-d*.17,z+.08),(x+w*.36,y-d*.17,z+.08),.07)
 beam('BackBaseCrossmember',(x-w*.36,y+d*.10,z+.08),(x+w*.36,y+d*.10,z+.08),.07)
 if num=='027':
  # Representative seated abdominal machine, centre spine and pivoted chest pad.
  box('Seat',(x,y-d*.15,z+.49),(min(.46,w*.35),d*.35,.105),pad,.025)
  beam('SeatSupport',(x,y-d*.15,z+.08),(x,y-d*.15,z+.44),.085)
  box('BackPad',(x,y+d*.05,z+.86),(.43,.12,.65),pad,.025)
  beam('Spine',(x,rear,z+.08),(x,rear,z+1.45),.085)
  beam('BackPadBridge',(x,y+d*.05,z+.90),(x,rear,z+.90),.065)
  beam('PivotCrossbar',(x-w*.20,rear,z+1.12),(x+w*.20,rear,z+1.12),.045)
  beam('ChestPadCrossmember',(x-w*.20,y-d*.16,z+1.02),(x+w*.20,y-d*.16,z+1.02),.04)
  for s in (-1,1):
   xx=x+s*w*.20;rod('Pivot'+str(s),(xx-.025,rear,z+1.12),(xx+.025,rear,z+1.12),.065,chrome)
   beam('PivotArm'+str(s),(xx,rear,z+1.12),(xx,y-d*.19,z+1.0),.048)
   rod('Grip'+str(s),(xx,y-d*.19,z+1),(xx,y-d*.34,z+.94),.024,rubber)
  box('ChestRollerPad',(x,y-d*.16,z+1.02),(.46,.16,.17),pad,.04)
 else:
  box('Seat',(x,y-d*.17,z+.49),(.40,min(.38,d*.34),.105),pad,.025)
  beam('SeatPost',(x,y-d*.17,z+.08),(x,y-d*.17,z+.44),.08)
  box('BackPad',(x,y+d*.035,z+.91),(.35,.13,.65),pad,.025)
  beam('BackSupport',(x,y+d*.10,z+.10),(x,y+d*.10,z+1.22),.07)
 towerx=x+w*.25
 for s in (-1,1):
  xx=towerx+s*.085;rod('GuideRod'+str(s),(xx,rear,z+.16),(xx,rear,z+1.59),.013,chrome)
 for j in range(13):box('WeightPlate'+str(j),(towerx,rear,z+.23+j*.057),(.29,.22,.047),steel,.004)
 rod('SelectorPin',(towerx+.15,rear,z+.58),(towerx+.21,rear,z+.58),.01,chrome)
 beam('TowerLeft',(towerx-.20,rear,z+.08),(towerx-.20,rear,z+1.63),.055)
 beam('TowerRight',(towerx+.20,rear,z+.08),(towerx+.20,rear,z+1.63),.055)
 beam('TowerCap',(towerx-.20,rear,z+1.63),(towerx+.20,rear,z+1.63),.055)
 if num=='029':
  # Cable runs up from stack, across overhead arm and down to the pull bar.
  beam('OverheadBoom',(towerx,rear,z+1.64),(x,y-d*.14,z+1.69),.07)
  for j,(xx,yy,zz) in enumerate(((towerx,rear,z+1.57),(x,y-d*.14,z+1.62))):
   rod('Pulley'+str(j),(xx-.035,yy,zz),(xx+.035,yy,zz),.067,rubber,32)
   rod('PulleyAxle'+str(j),(xx-.045,yy,zz),(xx+.045,yy,zz),.012,chrome)
  rod('CableRise',(towerx,rear-.064,z+.95),(towerx,rear-.064,z+1.57),.004,rubber,12)
  rod('CableOverhead',(towerx,rear-.064,z+1.57),(x,y-d*.14-.064,z+1.62),.004,rubber,12)
  rod('CableDrop',(x,y-d*.14-.064,z+1.62),(x,y-d*.14-.064,z+1.37),.004,rubber,12)
  mid=(x,y-d*.14-.064,z+1.37)
  for s in (-1,1):
   tip=(x+s*w*.35,mid[1],z+1.29);rod('PullBar'+str(s),mid,tip,.014,chrome)
   rod('PullGrip'+str(s),(x+s*w*.24,mid[1],z+1.315),tip,.021,rubber)
   rod('ThighPad'+str(s),(x+s*.05,y-d*.06,z+.68),(x+s*.22,y-d*.06,z+.68),.058,pad)
  beam('ThighPadPost',(x,y+d*.03,z+.08),(x,y+d*.03,z+.68),.048)
  beam('ThighBaseCrossmember',(x-w*.36,y+d*.03,z+.08),(x+w*.36,y+d*.03,z+.08),.048)
 elif num=='030':
  for s in (-1,1):
   xx=x+s*w*.27
   beam('PressPivotSupport'+str(s),(xx,rear,z+.08),(xx,rear,z+1.37),.055)
   rod('PressPivot'+str(s),(xx-.045,rear,z+1.25),(xx+.045,rear,z+1.25),.055,chrome)
   beam('PressArm'+str(s),(xx,rear,z+1.25),(xx,y-d*.18,z+1.13),.05)
   rod('PressGrip'+str(s),(xx,y-d*.18,z+1.13),(xx,y-d*.32,z+1.13),.024,rubber)
  beam('LinkedPivotCrossbar',(x-w*.27,rear,z+1.25),(x+w*.27,rear,z+1.25),.045)
  rod('ResistanceCable',(towerx,rear-.03,z+.96),(towerx,rear-.03,z+1.39),.004,rubber,12)
  rod('ReturnPulley',(towerx-.025,rear,z+1.39),(towerx+.025,rear,z+1.39),.055,rubber)
  rod('CableToPress',(towerx,rear-.054,z+1.39),(x,rear-.03,z+1.25),.004,rubber,12)
 else:
  rod('CoreResistanceCable',(towerx,rear-.03,z+.96),(x,rear-.03,z+1.12),.004,rubber,12)
# Standalone benches, dumbbells, bikes and storage kept as editable B05 donor objects.
retained=bpy.data.collections.new('B05_RETAINED_FITNESS_COMPONENTS');sc.collection.children.link(retained)
used={n for r in records for n in r['replaces_objects']}
for n,c in oldcopies.items():
 if n not in used:
  retained.objects.link(c);c.hide_render=False;c.hide_viewport=False;c.hide_set(False)
# Authoritative checks recorded before export, with modifiers evaluated.
bpy.context.view_layer.update()
for r in records:
 obs=list(bpy.data.collections[r['id']].objects);bb=union(obs);r['bounds_m']=bb;r['parts_count']=len(obs)
 it=items[r['source_marker']];x,y,z=it['position_m'];w,d=it['footprint_m'];allowed=[[x-w/2,y-d/2],[x+w/2,y+d/2]]
 # Racks retain the corrected bar and bench extensions, accepted separately from rack box.
 if it['label'].startswith('Squat'):
  oldbb=union([oldcopies[n] for n in r['replaces_objects']]);allowed=[[oldbb[0][0],oldbb[0][1]],[oldbb[1][0],oldbb[1][1]]]
 r['approved_xy_envelope']=allowed
 r['xy_envelope_pass']=all(bb[0][i]>=allowed[0][i]-.001 and bb[1][i]<=allowed[1][i]+.001 for i in range(2))
 r['floor_support_pass']=abs(bb[0][2]-z)<.025
 r['topology']=[]
 for ob in obs:
  bm=bmesh.new();bm.from_mesh(ob.data);r['topology'].append({'name':ob.name,'vertices':len(bm.verts),'faces':len(bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'materials':[m.name for m in ob.data.materials]});bm.free()
assert all(r['xy_envelope_pass'] and r['floor_support_pass'] for r in records),[(r['id'],r['bounds_m'],r['approved_xy_envelope']) for r in records if not r['xy_envelope_pass']]
manifest={'source_blend':str(ROOT/'scene/Campus_Center_New_Plans_Furniture_v26_b05.blend'),'source_sha256':source_hash,'blender':bpy.app.version_string,'units':'meters; Blender Z up; glTF Y up','replacements':records,'rack_support':support,'standalone_benches_retained_no_loadedbars':['RE07_PH02_Fitness218_035_0','RE07_PH02_Fitness218_036_0'],'unreal_target_actor':'R25_U218_Furniture / StaticMeshActor_1510','unreal_current_mesh':'/Game/Campus/FitnessSupportR26R01/Runtime/FA26_FitnessSupport_U218_R06','collision_contract':'CTF_USE_COMPLEX_AS_SIMPLE; QUERY_AND_PHYSICS; simple collision count 1 retained by integrator; do not generate a solid hull around group','unreal_status':'Mesh staging only; no map mutation/import/runtime collision test','retained_donor_objects':[n for n in oldcopies if n not in used]}
(O/'replacement_manifest.json').write_text(json.dumps(manifest,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(O/'CampusCenter_Equipment_Editable_EQ27_R01.blend'))
(O/'exports').mkdir(exist_ok=True)
def export(path,obs):
 bpy.ops.object.select_all(action='DESELECT')
 for ob in obs:ob.select_set(True)
 bpy.context.view_layer.objects.active=obs[0]
 bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_yup=True,export_materials='EXPORT',export_extras=True,export_apply=True)
export(O/'exports/Equipment_EQ27_R01_World.glb',[o for col in groups.values() for o in col.objects])
for num,col in groups.items():export(O/'exports'/f'{col.name}_World.glb',list(col.objects))
# Full membership of original R25 actor: retain all unaffected donor meshes.
source_manifest=json.loads((ROOT/'downstream/furniture_art_v26_r01/fitness_support_patch_r01/source-manifest.json').read_text())
members=source_manifest['complete_group_membership'];complete=[]
for n in members:
 if n not in used:complete.append(bpy.data.objects[n])
complete += [o for num,col in groups.items() if int(num) in range(3,18) for o in col.objects]
export(O/'exports/R25_U218_Furniture_EQ27_R01_Complete.glb',complete)
print('BUILD_OK',len(records),'complete_objects',len(complete))
