import bpy,json,pathlib,sys,time,hashlib
from mathutils import Vector
R=pathlib.Path(__file__).parent;rooms=json.loads((R/'rooms/room_contract.json').read_text());s=bpy.context.scene;s.frame_set(1)
pilot='--pilot' in sys.argv
if pilot:rooms=[r for r in rooms if r['number'] in ['108','102']]
for o in s.objects:
 if o.type!='MESH':continue
 bb=[o.matrix_world@Vector(v) for v in o.bound_box];zmin=min(v.z for v in bb)
 names=[c.name for c in o.users_collection]
 if zmin>=3.45 or any(n in ['ROOF','ROOF_DETAILS','UPPER','ROOM_LABELS','STUDENTS - toggle entire collection','V5_CEILING'] for n in names):o.hide_render=True
 if o.type=='MESH' and any(k in o.name.lower() for k in ['ceiling','roof_top','roof_slab']):o.hide_render=True
s.render.engine='CYCLES';prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='CUDA';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='CUDA'
s.cycles.device='GPU';s.cycles.samples=64;s.cycles.use_denoising=True;s.cycles.adaptive_threshold=.02
s.render.resolution_x=1024;s.render.resolution_y=1024;s.render.resolution_percentage=100;s.render.pixel_aspect_x=s.render.pixel_aspect_y=1
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';s.render.film_transparent=True;s.render.use_border=False
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=.3
s.use_nodes=False
camdata=bpy.data.cameras.new('Room orthographic - exact vertical');cam=bpy.data.objects.new(camdata.name,camdata);s.collection.objects.link(cam);s.camera=cam;camdata.type='ORTHO';camdata.dof.use_dof=False;camdata.clip_start=.01;camdata.clip_end=100
lightdata=bpy.data.lights.new('Room soft overhead','AREA');light=bpy.data.objects.new(lightdata.name,lightdata);s.collection.objects.link(light);lightdata.shape='DISK'
report=[]
for r in rooms:
 cx,cy=r['center_world_m'];span=r['ortho_span_m'];cam.location=(cx,cy,3.5);cam.rotation_euler=(0,0,0);camdata.ortho_scale=span
 light.location=(cx,cy,3.3);light.rotation_euler=(0,0,0);lightdata.size=max(2,span*.7);lightdata.energy=max(200,span*span*7)
 out=R/'rooms'/r['number'];f=out/('topdown_pilot_raw.png' if pilot else 'topdown_raw.png');s.render.filepath=str(f);start=time.monotonic();bpy.ops.render.render(write_still=True)
 report.append({'room':r['number'],'file':str(f),'seconds':time.monotonic()-start,'orthographic':True,'dof':False,'samples':64,'resolution':[1024,1024],'source':str(R/'Source_Studio.blend')})
 (R/'rooms'/('pilot_render_report.json' if pilot else 'render_report.json')).write_text(json.dumps(report,indent=2));print('ROOM_DONE',r['number'],flush=True)
if not pilot:bpy.ops.wm.save_as_mainfile(filepath=str(R/'Ground_Room_Render_Setup.blend'))
