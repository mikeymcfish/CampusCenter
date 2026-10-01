import bpy,json,pathlib,math,time,sys,hashlib
from mathutils import Vector
O=pathlib.Path(__file__).parent
contract=json.loads((O/'preview_contract.json').read_text());out=O/'previews';out.mkdir(exist_ok=True)
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=24;sc.cycles.use_denoising=True
sc.render.resolution_x=1200;sc.render.resolution_y=900;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGBA';sc.render.image_settings.color_depth='8';sc.render.use_border=False;sc.use_nodes=False;sc.view_settings.view_transform='AgX';sc.world=bpy.data.worlds.new('CPU Studio');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.55,.55,.55,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.65
def objects(num):return list(bpy.data.collections['EQ27_PH02_Fitness218_'+num].objects)
manifest=json.loads((O/'replacement_manifest.json').read_text());sources={r['source_marker'][-3:]:r for r in manifest['replacements']}
def bb(obs):
 bpy.context.view_layer.update();vs=[o.matrix_world@Vector(v) for o in obs for v in o.bound_box];lo=Vector([min(v[i] for v in vs) for i in range(3)]);hi=Vector([max(v[i] for v in vs) for i in range(3)]);return lo,hi
def render(file,sets):
 for o in bpy.data.objects:o.hide_render=True
 copies=[]
 for obs,offset in sets:
  lo,hi=bb(obs);centre=(lo+hi)/2
  for o in obs:
   c=o.copy();c.data=o.data.copy();sc.collection.objects.link(c);c.matrix_world=o.matrix_world.copy();c.location += Vector(offset)-Vector((centre.x,centre.y,lo.z));c.hide_render=False;copies.append(c)
 lo,hi=bb(copies);center=(lo+hi)/2;extent=hi-lo
 bpy.ops.mesh.primitive_plane_add(size=200,location=(center.x,center.y,-.005));floor=bpy.context.object;floor.hide_render=False
 m=bpy.data.materials.get('Studio floor') or bpy.data.materials.new('Studio floor');m.diffuse_color=(.64,.66,.68,1);floor.data.materials.append(m)
 bpy.ops.object.camera_add(location=center+Vector((3.6,-5.0,3.4))*max(extent.x,extent.y,extent.z)*.75);cam=bpy.context.object;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=max(extent.x,extent.y*1.25,extent.z*1.65)*1.35;sc.camera=cam
 lamps=[]
 for p,energy,size in (((-3,-4,7),1100,5),((4,2,5),900,4)):
  bpy.ops.object.light_add(type='AREA',location=center+Vector(p));l=bpy.context.object;l.data.energy=energy;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(center-l.location).to_track_quat('-Z','Y').to_euler();l.hide_render=False;lamps.append(l)
 sc.render.filepath=str(out/file);start=time.time();bpy.ops.render.render(write_still=True)
 results.append({'filename':file,'elapsed_seconds':time.time()-start,'target_parts':len(copies),'resolution':[1200,900],'engine':'CYCLES','device':'CPU','samples':24})
 for o in copies+[floor,cam]+lamps:bpy.data.objects.remove(o,do_unlink=True)
updated='--updated' in sys.argv
treadmill_update='--treadmill-update' in sys.argv
results=[]
if treadmill_update and (out/'render_results.json').exists():results=[r for r in json.loads((out/'render_results.json').read_text())['results'] if r['filename'] not in ('improved_representatives.png','treadmill_detail.png')]
if updated and (out/'render_results.json').exists():results=[r for r in json.loads((out/'render_results.json').read_text())['results'] if r['filename'] in ('rack_detail.png','treadmill_detail.png','baseline_representatives.png')]
render('improved_representatives.png',[(objects('009'),(-2.1,0,0)),(objects('003'),(0,0,0)),(objects('029'),(1.65,0,0))])
if not updated and not treadmill_update:
 render('rack_detail.png',[(objects('009'),(0,0,0))])
if not updated:
 render('treadmill_detail.png',[(objects('003'),(0,0,0))])
if not treadmill_update:
 render('pulldown_detail.png',[(objects('029'),(0,0,0))])
 render('press_core_detail.png',[(objects('027'),(-1.2,0,0)),(objects('030'),(1.1,0,0))])
# Load original donor representatives from isolated audit copy, without loading its scene.
if not updated and not treadmill_update:
 names=sum([sources[n]['replaces_objects'] for n in ('009','003','029')],[])
 with bpy.data.libraries.load(str(O/'audit_b05.blend'),link=False) as (src,dst):dst.objects=names
 baseline={n:[] for n in ('009','003','029')}
 for o in dst.objects:
  sc.collection.objects.link(o);o.hide_render=False;o.hide_viewport=False;o.hide_set(False)
  for num in baseline:
   if o.name.split('.')[0] in sources[num]['replaces_objects']:baseline[num].append(o)
 render('baseline_representatives.png',[(baseline['009'],(-2.1,0,0)),(baseline['003'],(0,0,0)),(baseline['029'],(1.65,0,0))])
(out/'render_results.json').write_text(json.dumps({'contract':contract,'results':results,'source_blend_sha256':hashlib.sha256((O/'CampusCenter_Equipment_Editable_EQ27_R01.blend').read_bytes()).hexdigest()},indent=2))
