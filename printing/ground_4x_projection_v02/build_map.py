import bpy, math, json, pathlib, hashlib, time
from mathutils import Vector
R=pathlib.Path(__file__).parent
R.mkdir(exist_ok=True)
S=R.parent/'projection_print_v01/Campus_Center_Projection.blend'
source_hash=hashlib.sha256(S.read_bytes()).hexdigest()
s=bpy.context.scene;s.frame_set(1)
contract={'source':str(S),'source_sha256':source_hash,'working_copy':str(R/'Campus_Center_Top_Down_Projection.blend'),'resolution':[1024,786],'base_count':1,'generated_frames':24,'frame_names':'frames/0001.png .. 0024.png','camera':'Orthographic, vertical downward; north is image top','engine':'Cycles CUDA','samples':64,'denoising':True,'sun_lights':0,'animated_lighting':False,'mask':'Exact printed floor top faces at full-scale Z=0; everything else black; one-pixel conservative inset','composite':'Immutable Blender furniture base with independently generated people artwork on top; hard floor mask last','format':'8-bit RGB PNG; black RGB 0,0,0','source_policy':'Never overwrite source; preserve existing print tiles','validation':'Visual review, source hashes, floor-mask black pixels, output count and dimensions, loop seam'}
(R/'render_contract.json').write_text(json.dumps(contract,indent=2))
hidden_people=[]
for o in s.objects:
 if o.type=='LIGHT':o.hide_render=True
 if o.name.startswith(('Loop occupant ','Student_')) or any('mannequin' in c.name.lower() or 'occupant' in c.name.lower() for c in o.users_collection):
  o.hide_render=True;hidden_people.append(o.name)
 if o.animation_data:
  mat=o.matrix_world.copy();o.animation_data_clear();o.matrix_world=mat
for collection in [bpy.data.materials,bpy.data.worlds,bpy.data.lights]:
 for data in collection:
  if data.animation_data:data.animation_data_clear()
  if getattr(data,'node_tree',None) and data.node_tree.animation_data:data.node_tree.animation_data_clear()
s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.use_denoising=True;s.cycles.adaptive_threshold=.035
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='CUDA';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='CUDA'
s.cycles.device='GPU'
s.render.resolution_x=1024;s.render.resolution_y=786;s.render.resolution_percentage=100
s.render.pixel_aspect_x=s.render.pixel_aspect_y=1;s.render.use_border=False;s.render.film_transparent=False
s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='8';s.render.fps=8;s.frame_start=1;s.frame_end=24;s.use_nodes=False
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0
world=bpy.data.worlds.new('V02 static soft studio ambient');world.use_nodes=True;world.node_tree.nodes.get('Background').inputs[0].default_value=(.85,.9,1,1);world.node_tree.nodes.get('Background').inputs[1].default_value=.7;s.world=world
cam=s.camera;cam.name='PROJECTOR - direct vertical top down';cam.data.type='ORTHO';cam.data.sensor_fit='HORIZONTAL';cam.data.ortho_scale=743*.0875/ .94;cam.data.dof.use_dof=False;cam.data.clip_end=1000
cam.location=(384.5*.0875-47,289*.0875-2.3,100);cam.rotation_euler=(0,0,0)
ld=bpy.data.lights.new('V02 fixed broad overhead fill','AREA');lo=bpy.data.objects.new(ld.name,ld);s.collection.objects.link(lo);lo.location=(*cam.location[:2],35);ld.energy=18000;ld.shape='DISK';ld.size=48
def emission(name,color):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();e=n.new('ShaderNodeEmission');e.inputs[0].default_value=(*color,1);out=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],out.inputs[0]);return m
black=emission('PROJECTOR BLACK - no light on walls',(0,0,0));white=emission('Receiver floor validity',(1,1,1))
floor=bpy.data.materials.new('V02 floor warm neutral');floor.use_nodes=True;p=floor.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.46,.49,.5,1);p.inputs['Roughness'].default_value=.9
shells=[o for o in s.objects if o.name.startswith('Receiver ')];floor_counts={}
for o in shells:
 old=list(o.data.materials);oldidx=[p.material_index for p in o.data.polygons];o.data.materials.clear()
 for m in [black,floor,old[1],old[2],white]:o.data.materials.append(m)
 count=0
 for p,idx in zip(o.data.polygons,oldidx):
  isfloor=abs(p.center.z)<.001 and p.normal.z>.999
  p.material_index=(idx+1 if idx else 1) if isfloor else 0
  count+=isfloor
 floor_counts[o.name]=count
def render(name):
 s.render.filepath=str(R/name);bpy.ops.render.render(write_still=True);print('SAVED',name,flush=True)
render('base_beauty_unmasked.png')
visibility={o.name:o.hide_render for o in s.objects};indices={o.name:[p.material_index for p in o.data.polygons] for o in shells}
for o in s.objects:
 if o.type in {'MESH','FONT','CURVE'}:o.hide_render=o not in shells
for o in shells:
 for p in o.data.polygons:p.material_index=4 if p.material_index else 0
s.view_settings.view_transform='Standard';s.view_settings.look='None';world.node_tree.nodes.get('Background').inputs[1].default_value=0;s.cycles.samples=4;s.cycles.use_denoising=False
render('floor_mask_raw.png')
for o in shells:
 for p,idx in zip(o.data.polygons,indices[o.name]):p.material_index=idx
for o in s.objects:o.hide_render=visibility[o.name]
world.node_tree.nodes.get('Background').inputs[1].default_value=.7
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.cycles.samples=64;s.cycles.use_denoising=True
s['projection_purpose']='Direct vertical floor-only projection. All walls and all non-floor receiving surfaces black.';s['loop_note']='Fixed illumination. 24 Imagegen people frames composited onto the same base; no sun animation.'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Campus_Center_Top_Down_Projection.blend'))
width=cam.data.ortho_scale;height=width*786/1024
report={'source_sha256':source_hash,'source_unchanged':hashlib.sha256(S.read_bytes()).hexdigest()==source_hash,'resolution':[1024,786],'camera_type':'ORTHO','camera_rotation_degrees':[0,0,0],'elevation_degrees':90,'horizontal_width_world_m':width,'vertical_height_world_m':height,'center_world_m':list(cam.location[:2]),'physical_projection_center_mm':[384.5,289],'physical_projection_width_mm':width/.0875,'physical_projection_height_mm':height/.0875,'source_floor_z_m':0,'black_wall_mask_inset_pixels':1,'floor_face_counts':floor_counts,'hidden_people':hidden_people,'devices':[{'name':d.name,'type':d.type,'use':d.use} for d in prefs.devices],'blender_version':bpy.app.version_string}
(R/'projection_manifest.json').write_text(json.dumps(report,indent=2))
