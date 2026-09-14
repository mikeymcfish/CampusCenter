import bpy,bmesh,json,math,pathlib,hashlib
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
R=pathlib.Path(__file__).parent;cfg=json.loads((R/'projector_config.json').read_text());manifest=json.loads((R/'print_manifest.json').read_text());s=bpy.context.scene;s.frame_set(1)
sourcehash=hashlib.sha256((R/'Source_Copy.blend').read_bytes()).hexdigest();kept=[];hidden=[]
# Render only ground-floor contents. Print geometry supplies the exact physical shell.
architecture={'GROUND','UPPER','GYM','ROOF','STAIR','ROOM_LABELS','PRESENTATION','DOOR_HARDWARE','ROOF_DETAILS'}
for o in list(s.objects):
 if o.type=='LIGHT':o.hide_render=True;continue
 if o.type not in {'MESH','FONT','CURVE','EMPTY'}:continue
 if o.hide_render:continue
 cols={c.name for c in o.users_collection};n=o.name.lower()
 # Hidden original occupants stay hidden; no change to source character placements.
 if o.type=='EMPTY':o.hide_render=True;continue
 pts=[o.matrix_world@Vector(p) for p in o.bound_box];lo=Vector([min(p[i] for p in pts) for i in range(3)]);hi=Vector([max(p[i] for p in pts) for i in range(3)])
 remove=bool(cols&architecture) or lo.z>=3.7 or hi.z>4.2673 or hi.z<-.03 or lo.x<-46 or hi.x>19 or hi.y>48 or lo.y<-1
 remove|=any(k in n for k in ['ceiling','roof','pendant','skylight','banner','glazing','glass','window','wall','lintel','jamb','base_trim','skirting','handrail','guardrail','stair','floor','slab','lawn','sidewalk','plaza','walkway'])
 remove|=bool(cols&{'V04 Site grass and concrete','V5_SITE','V5_CEILING','LIGHT_FIXTURES','V14 corridor lighting'})
 if remove:o.hide_render=True;hidden.append(o.name)
 else:kept.append(o.name)
c=bpy.data.collections.new('PROJECTION - physical receiving shell');s.collection.children.link(c)
def material(name,col):
 m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*col,1);b.inputs['Roughness'].default_value=.85;return m
shellmat=material('Projection neutral white model',(.62,.65,.66));shells=[]
gymmat=bpy.data.materials.get('Natural oak',shellmat);carpet=next((m for m in bpy.data.materials if 'carpet' in m.name.lower()),shellmat)
for tile in manifest['tiles']:
 bpy.ops.wm.stl_import(filepath=str(R/'print_tiles'/tile['file']));o=bpy.context.object;o.name='Receiver '+tile['name']
 for old in list(o.users_collection):old.objects.unlink(o)
 c.objects.link(o);o.data.transform(Matrix.Translation(Vector(tile['assembly_offset_mm'])));o.data.transform(Matrix.Scale(.0875,4));o.data.transform(Matrix.Translation((-47,-2.3,-.42)));o.data.materials.clear();o.data.materials.append(shellmat);o.data.materials.append(gymmat);o.data.materials.append(carpet);o.data.update();shells.append(o)
 for face in o.data.polygons:
  p=face.center
  if abs(p.z)<.001 and face.normal.z>.9:
   if -25.7<p.x<-.16 and 16.38<p.y<47.24:face.material_index=1
   elif .15<p.x<16.4 and 14.7<p.y<30.9:face.material_index=2
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.cycles.adaptive_threshold=.08
s.render.resolution_x=cfg['width'];s.render.resolution_y=cfg['height'];s.render.resolution_percentage=100;s.render.pixel_aspect_x=s.render.pixel_aspect_y=1;s.render.film_transparent=True
s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';s.render.fps=cfg['fps'];s.frame_start=1;s.frame_end=cfg['fps']*cfg['loop_seconds']
s.use_nodes=False
world=bpy.data.worlds.new('Projection ambient');world.use_nodes=True;world.node_tree.nodes.get('Background').inputs[0].default_value=(.75,.82,1,1);world.node_tree.nodes.get('Background').inputs[1].default_value=.55;s.world=world
camdata=bpy.data.cameras.new('PROJECTOR - adjustable physical lens');cam=bpy.data.objects.new(camdata.name,camdata);s.collection.objects.link(cam);s.camera=cam;camdata.type='PERSP';camdata.sensor_fit='HORIZONTAL';camdata.sensor_width=36;camdata.lens=36*cfg['throw_ratio'];camdata.clip_end=1000;camdata.dof.use_dof=False
lo=Vector(manifest['assembly_bounds_mm'][0])*.0875+Vector((-47,-2.3,-.42));hi=Vector(manifest['assembly_bounds_mm'][1])*.0875+Vector((-47,-2.3,-.42));target=(lo+hi)/2;target.z=0
e=math.radians(cfg['elevation_degrees']);a=math.radians(cfg['azimuth_degrees']);direction=Vector((math.sin(a)*math.cos(e),-math.cos(a)*math.cos(e),math.sin(e)))
corners=[Vector((x,y,z)) for x in [lo.x,hi.x] for y in [lo.y,hi.y] for z in [lo.z,hi.z]];distance=50
for _ in range(200):
 cam.location=target+direction*distance;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();points=[world_to_camera_view(s,cam,p) for p in corners];margin=cfg['fit_margin']
 if all(margin<p.x<1-margin and margin<p.y<1-margin and p.z>0 for p in points):break
 distance*=1.025
else:raise RuntimeError('Projector fit failed')
period=s.frame_end
lightdata=bpy.data.lights.new('Looping daylight and moving shadows','SUN');light=bpy.data.objects.new(lightdata.name,lightdata);s.collection.objects.link(light);lightdata.energy=2;lightdata.angle=.06
for axis,base,amp in [(0,.45,.16),(1,-.55,.16),(2,-.2,.12)]:
 driver=light.driver_add('rotation_euler',axis).driver;driver.expression=f'{base}+{amp}*sin(2*pi*(frame-1)/{period})'
# Two deliberately simple moving occupants, reusing the existing baked mannequin mesh.
template=next(o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('Student_'))
for i in range(2):
 o=bpy.data.objects.new('Loop occupant '+str(i+1),template.data.copy());s.collection.objects.link(o);o.hide_render=False;o.hide_viewport=False
 # Normalize baked local bounds so motion remains on the corridor floor.
 vs=[v.co for v in o.data.vertices];center=Vector(((min(v.x for v in vs)+max(v.x for v in vs))/2,(min(v.y for v in vs)+max(v.y for v in vs))/2,min(v.z for v in vs)));o.data.transform(Matrix.Translation(-center));o.data.materials.clear();o.data.materials.append(material('Occupant '+str(i),(.13,.26,.40) if i==0 else (.6,.29,.1)))
 phase=f'(2*pi*(frame-1)/{period}+{i*math.pi})'
 for axis,expr in [(0,f'-19+3*cos{phase}'),(1,f'14.9+.30*sin{phase}')]:o.driver_add('location',axis).driver.expression=expr
 o.driver_add('rotation_euler',2).driver.expression=f'{phase}+pi/2'
# Original fireplace image emits a periodic warm flicker; geometry still matches the print shell.
for m in bpy.data.materials:
 if m.name=='V04 Imagegen fire insert':
  for node in m.node_tree.nodes:
   if node.type=='EMISSION':node.inputs['Strength'].driver_add('default_value').driver.expression=f'3.2+.6*sin(2*pi*7*(frame-1)/{period})+.25*sin(2*pi*13*(frame-1)/{period})'
s['projection_purpose']='Ground-floor physical model projection. Fixed camera is projector, not audience viewpoint.';s['loop_note']='12-second periodic daylight shadows, fire flicker and two stylized baked-pose moving occupants. No walking gait simulation.'
s.frame_set(1);bpy.context.view_layer.update();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Campus_Center_Projection.blend'))
offset=Vector((-47,-2.3,-.42));physical=lambda p:list((Vector(p)-offset)/.0875)
report={'source_sha256':sourcehash,'kept_contents':kept,'hidden_for_cutaway':hidden,'projector_location_assembly_mm':physical(cam.location),'aim_point_assembly_mm':physical(target),'projector_to_aim_distance_mm':distance/.0875,'elevation_degrees':cfg['elevation_degrees'],'throw_ratio':cfg['throw_ratio'],'resolution':[cfg['width'],cfg['height']],'frames':[1,period],'fps':cfg['fps'],'shells':[o.name for o in shells],'coordinate_mapping':'fullsize_m = print_assembly_mm * 0.0875 + (-47, -2.3, -0.42)','source_unchanged':hashlib.sha256((R.parent/'cycles_studio_v05/Campus_Center_Cycles_Studio.blend').read_bytes()).hexdigest()==sourcehash}
(R/'projection_manifest.json').write_text(json.dumps(report,indent=2));print('PROJECTION_BUILT',len(kept),report['projector_location_assembly_mm'])
