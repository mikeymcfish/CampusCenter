import bpy,bmesh,json,pathlib,sys,time,math
from mathutils import Vector
R=pathlib.Path(__file__).parent;rooms=json.loads((R/'rooms/room_contract.json').read_text());s=bpy.context.scene;s.frame_set(1)
if '--pilot' in sys.argv:rooms=[r for r in rooms if r['number'] in ['108','102']]
source=[]
for o in s.objects:
 if o.type!='MESH':
  if o.type not in ['LIGHT','CAMERA']:o.hide_render=True
  continue
 bb=[o.matrix_world@Vector(v) for v in o.bound_box];lo=Vector([min(v[i] for v in bb) for i in range(3)]);hi=Vector([max(v[i] for v in bb) for i in range(3)])
 if not o.hide_render and lo.z<3.45 and not any(c.name in ['ROOF','ROOF_DETAILS','UPPER','ROOM_LABELS','STUDENTS - toggle entire collection','V5_CEILING'] for c in o.users_collection) and not any(k in o.name.lower() for k in ['ceiling','roof_top','roof_slab']):source.append((o,lo,hi))
 o.hide_render=True
for o in s.objects:
 if o.type=='LIGHT':o.hide_render=True
s.world=bpy.data.worlds.new('Cutaway room studio');s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.15,.19,.24,1);s.world.node_tree.nodes.get('Background').inputs[1].default_value=.45
s.render.engine='CYCLES';prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='CUDA';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='CUDA'
s.cycles.device='GPU';s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.adaptive_threshold=.02
s.render.resolution_x=1280;s.render.resolution_y=960;s.render.resolution_percentage=100;s.render.pixel_aspect_x=s.render.pixel_aspect_y=1;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.film_transparent=False;s.render.use_border=False;s.use_nodes=False
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=.2
cd=bpy.data.cameras.new('Room oblique illustration');cam=bpy.data.objects.new(cd.name,cd);s.collection.objects.link(cam);s.camera=cam;cd.type='ORTHO';cd.dof.use_dof=False;cd.clip_end=300
lights=[]
for i in range(2):
 ld=bpy.data.lights.new('Cutaway softbox '+str(i),'AREA');ob=bpy.data.objects.new(ld.name,ld);s.collection.objects.link(ob);ld.shape='DISK';lights.append(ob)
report=[]
for r in rooms:
 x0,y0,x1,y1=r['mask_bounds_px']
 def wx(x):return ((x-1024)*830/2048+398)*.0875-47
 def wy(y):return ((786-y)*830/2048+289)*.0875-2.3
 xmin,xmax=wx(x0)-.18,wx(x1)+.18;ymin,ymax=wy(y1)-.18,wy(y0)+.18;cx=(xmin+xmax)/2;cy=(ymin+ymax)/2;span=max(xmax-xmin,ymax-ymin);created=[]
 for o,lo,hi in source:
  if hi.x<xmin or lo.x>xmax or hi.y<ymin or lo.y>ymax or hi.z<-.01:continue
  # Remove foreground tall partitions only for this explanatory cutaway.
  thin=min(hi.x-lo.x,hi.y-lo.y)<.6
  if hi.z>1.85 and lo.z<1 and thin and ((hi.y<ymin+.65) or (lo.x>xmax-.65)):continue
  cp=o.copy();cp.data=o.data.copy();s.collection.objects.link(cp);cp.hide_render=False;created.append(cp)
  if lo.x<xmin or hi.x>xmax or lo.y<ymin or hi.y>ymax or hi.z>3.4:
   if len(cp.modifiers):
    old=cp.data;cp.data=bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get()));cp.modifiers.clear()
    if old.users==0:bpy.data.meshes.remove(old)
   cp.data.transform(cp.matrix_world);cp.matrix_world.identity();bm=bmesh.new();bm.from_mesh(cp.data)
   for co,no in [((xmin,0,0),(-1,0,0)),((xmax,0,0),(1,0,0)),((0,ymin,0),(0,-1,0)),((0,ymax,0),(0,1,0)),((0,0,3.4),(0,0,1))]:
    if len(bm.verts):bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.0001,plane_co=co,plane_no=no,clear_outer=True,clear_inner=False)
   bm.to_mesh(cp.data);bm.free()
 target=Vector((cx,cy,1.5));cam.location=target+Vector((span*.63,-span*.80,span*1.02));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
 q=cam.rotation_euler.to_quaternion();corners=[q.inverted()@(Vector((x,y,z))-target) for x in [xmin,xmax] for y in [ymin,ymax] for z in [-.3,3.4]]
 lx,hx=min(p.x for p in corners),max(p.x for p in corners);ly,hy=min(p.y for p in corners),max(p.y for p in corners);cam.location+=q@Vector(((lx+hx)/2,(ly+hy)/2,0));cd.ortho_scale=max(hx-lx,(hy-ly)*4/3)*1.08
 for i,ob in enumerate(lights):
  ob.location=(cx+span*(.3 if i==0 else -.5),cy+span*(-.4 if i==0 else .3),max(5,span*.9));ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler();ob.data.size=max(4,span*.8);ob.data.energy=max(450,span*span*(35 if i==0 else 20))
 f=R/'rooms'/r['number']/'Room_3D.png';s.render.filepath=str(f);st=time.monotonic();bpy.ops.render.render(write_still=True)
 report.append({'room':r['number'],'objects':len(created),'seconds':time.monotonic()-st,'samples':96,'cutaway':True,'source_geometry_unchanged':True});(R/'rooms/oblique_report.json').write_text(json.dumps(report,indent=2));print('OBLIQUE_DONE',r['number'],flush=True)
 for cp in created:
  mesh=cp.data;bpy.data.objects.remove(cp,do_unlink=True)
  if mesh.users==0:bpy.data.meshes.remove(mesh)
