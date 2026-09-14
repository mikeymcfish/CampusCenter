import bpy,math,pathlib,json,random,sys
R=pathlib.Path(__file__).parent;random.seed(27);preview='--preview' in sys.argv
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.use_denoising=False;s.cycles.filter_width=.01;s.render.dither_intensity=0
s.render.resolution_x=1024;s.render.resolution_y=786;s.render.resolution_percentage=100;s.render.pixel_aspect_x=s.render.pixel_aspect_y=1;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.view_settings.view_transform='Standard';s.view_settings.look='None';s.render.fps=24;s.frame_start=1;s.frame_end=144
w=bpy.data.worlds.new('Projector zero ambient');w.use_nodes=True;w.node_tree.nodes.get('Background').inputs[1].default_value=0;s.world=w
d=bpy.data.cameras.new('Fixed direct vertical projector');cam=bpy.data.objects.new(d.name,d);s.collection.objects.link(cam);cam.location=(512,393,2000);d.type='ORTHO';d.ortho_scale=1024;d.sensor_fit='HORIZONTAL';d.clip_end=5000;s.camera=cam
def plane(name,x,y,z,sx,sy):
 mesh=bpy.data.meshes.new(name);mesh.from_pydata([(-sx/2,-sy/2,0),(sx/2,-sy/2,0),(sx/2,sy/2,0),(-sx/2,sy/2,0)],[],[(0,1,2,3)]);mesh.update();uv=mesh.uv_layers.new();coords=[(0,0),(1,0),(1,1),(0,1)]
 for i in range(4):uv.data[i].uv=coords[i]
 o=bpy.data.objects.new(name,mesh);s.collection.objects.link(o);o.location=(x,786-y,z);return o
def tree(o,name):
 m=bpy.data.materials.new(name);m.use_nodes=True;o.data.materials.append(m);m.node_tree.nodes.clear();return m.node_tree.nodes,m.node_tree.links
baseim=bpy.data.images.load(str(R/'Projection_Base_Detailed_3x.png'));maskim=bpy.data.images.load(str(R/'floor_only_mask.png'));maskim.colorspace_settings.name='Non-Color'
o=plane('IMMUTABLE detailed floor and furnishings',512,393,0,1024,786);n,l=tree(o,'Detailed projection base');uv=n.new('ShaderNodeTexCoord');im=n.new('ShaderNodeTexImage');im.image=baseim;im.interpolation='Linear';l.new(uv.outputs['UV'],im.inputs[0]);e=n.new('ShaderNodeEmission');l.new(im.outputs[0],e.inputs[0]);out=n.new('ShaderNodeOutputMaterial');l.new(e.outputs[0],out.inputs[0])
assets={k:bpy.data.images.load(str(R/'assets'/f'{k}.png')) for k in ['talking','seated','basketball']}
walk=bpy.data.images.load(str(R/'imagegen_raw/people_0001.png'));walk.source='SEQUENCE';assets['walking']=walk
collections={}
for name in ['Seated study and social groups','Standing conversations','Gym players and spectators','Walking students']:
 c=bpy.data.collections.new('STUDENTS - '+name);s.collection.children.link(c);collections[name]=c
records=[]
def worldpixel(x,y):return (512+(x+13.356249809265137)*1024/69.1622314453125,393-(y-22.987499237060547)*1024/69.1622314453125)
def sprite(name,x,y,asset,quad,heading=0,size=20,group='Standing conversations',motion=None,subtle=True):
 o=plane(name,x,y,1,size,size)
 for c in list(o.users_collection):c.objects.unlink(o)
 collections[group].objects.link(o);n,l=tree(o,name+' Imagegen material');uv=n.new('ShaderNodeTexCoord');scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs['Scale'].default_value=.5;l.new(uv.outputs['UV'],scale.inputs[0]);add=n.new('ShaderNodeVectorMath');add.operation='ADD';l.new(scale.outputs[0],add.inputs[0]);add.inputs[1].default_value=(.5*(quad%2),.5*(1-quad//2),0);tex=n.new('ShaderNodeTexImage');tex.image=assets[asset];tex.interpolation='Linear';l.new(add.outputs[0],tex.inputs[0])
 if asset=='walking':tex.image_user.frame_duration=24;tex.image_user.frame_start=1-random.randrange(24);tex.image_user.frame_offset=0;tex.image_user.use_cyclic=True;tex.image_user.use_auto_refresh=True
 sep=n.new('ShaderNodeSeparateColor');sep.mode='RGB';l.new(tex.outputs[0],sep.inputs[0]);mn=n.new('ShaderNodeMath');mn.operation='MINIMUM';l.new(sep.outputs[0],mn.inputs[0]);l.new(sep.outputs[2],mn.inputs[1]);sub=n.new('ShaderNodeMath');sub.operation='SUBTRACT';l.new(mn.outputs[0],sub.inputs[0]);l.new(sep.outputs[1],sub.inputs[1]);key=n.new('ShaderNodeMapRange');l.new(sub.outputs[0],key.inputs['Value']);key.inputs['From Min'].default_value=.08;key.inputs['From Max'].default_value=.3;key.inputs['To Min'].default_value=1;key.inputs['To Max'].default_value=0;key.clamp=True
 geo=n.new('ShaderNodeNewGeometry');map=n.new('ShaderNodeVectorMath');map.operation='MULTIPLY';l.new(geo.outputs['Position'],map.inputs[0]);map.inputs[1].default_value=(1/1024,1/786,0);mtex=n.new('ShaderNodeTexImage');mtex.image=maskim;mtex.interpolation='Closest';l.new(map.outputs[0],mtex.inputs[0]);mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';l.new(key.outputs['Result'],mul.inputs[0]);l.new(mtex.outputs[0],mul.inputs[1]);em=n.new('ShaderNodeEmission');l.new(tex.outputs[0],em.inputs[0]);tr=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader');l.new(mul.outputs[0],mix.inputs[0]);l.new(tr.outputs[0],mix.inputs[1]);l.new(em.outputs[0],mix.inputs[2]);out=n.new('ShaderNodeOutputMaterial');l.new(mix.outputs[0],out.inputs[0])
 phase=random.random()*2*math.pi;a=f'(2*pi*(frame-1)/144+{phase})';o.rotation_euler.z=heading
 if motion:
  rx,ry=motion;o.driver_add('location',0).driver.expression=f'{x}+{rx}*cos{a}';o.driver_add('location',1).driver.expression=f'{786-y}-{ry}*sin{a}'
  if asset=='walking':o.driver_add('rotation_euler',2).driver.expression=f'atan2({rx}*sin{a},-{ry}*cos{a})'
 if subtle and asset!='walking':o.driver_add('rotation_euler',2).driver.expression=f'{heading}+.022*sin{a}'
 records.append({'name':name,'asset':asset,'quadrant':quad,'group':group,'pixel_center':[x,y],'heading':heading,'size_pixels':size,'motion_radii':motion,'phase':phase});return o
def student_world(name,x,y,asset,quad,target=None,size=20,group='Standing conversations',motion=None):
 px,py=worldpixel(x,y);heading=0 if not target else math.atan2(-(target[0]-x),target[1]-y);return sprite(name,px,py,asset,quad,heading,size,group,motion)
inventory=json.loads((R/'source_inventory.json').read_text())['objects']
tables={0:(9.84,26.75),1:(9.22,23.01),2:(2.98,22.37),3:(.85,21.33),4:(10.4,19.3),5:(5.73,22.7)}
# Seated groups follow existing chair locations and face their own table.
for row in inventory:
 if row['name'].startswith('V03 Lounge ') and row['name'].endswith(' seat'):
  parts=row['name'].split();k=int(parts[2]);j=int(parts[3]);x,y=[(row['lo'][i]+row['hi'][i])/2 for i in [0,1]]
  student_world('Commons lounge '+str(k)+' student '+str(j),x,y,'seated',(k+j)%4,tables[k],17.2,'Seated study and social groups')
for cy in [25.51,17.14]:
 for j,(dx,dy) in enumerate([(-.63,0),(.63,0),(0,.62),(0,-.62)]):student_world('Commons cafe table student',1.69+dx,cy+dy,'seated',j,(1.69,cy),16.7,'Seated study and social groups')
for j,y in enumerate([16.7,17.8,18.8]):
 for x in [6.05,7.82]:student_world('Commons collaboration student',x,y,'seated',j%4,(6.94,y),16.7,'Seated study and social groups')
for j,x in enumerate([2.6,3.3,12.1,12.8]):student_world('North bench conversation',x,29.4,'seated',j,(x,28.5),17,'Seated study and social groups')
for room in ['113','112']:
 picked=[r for r in inventory if 'V8_DETAIL_V6_'+room+'_group_table_' in r['name']]
 for j,row in enumerate(picked[:4]):
  x,y=[(row['lo'][i]+row['hi'][i])/2 for i in [0,1]];student_world('Collaboration '+room+' student '+str(j),x,y,'seated',j%4,(-23.88 if room=='113' else -18.3,y),16.5,'Seated study and social groups')
for side,x,targetx in [('west',-3.16,-2.32),('east',-1.19,-2.32)]:
 for j,y in enumerate([2.2,4.4,6.6]):student_world('iLab table '+side+' '+str(j),x,y,'seated',(j+1)%4,(targetx,y),16.5,'Seated study and social groups')
for j,y in enumerate([3.4,5.8,7.0]):student_world('iLab maker bench student '+str(j),-8.75,y,'seated',j,(-7.8,y),16.2,'Seated study and social groups')
# Basketball: one practice game with ten players, plus sideline observers.
players=[(-14.5,26.5,0),(-10.2,28.7,3),(-12,28.8,1),(-17.4,24,0),(-9.3,24.7,1),(-14,36,0),(-10.8,37,1),(-17,39,3),(-13.2,40.8,0),(-8.8,33.7,1)]
for j,(x,y,q) in enumerate(players):student_world('Court player '+str(j+1),x,y,'basketball',q,(-12.93,31.81),21,'Gym players and spectators',(random.uniform(2,5),random.uniform(2,5)))
for side,x in [('west',-22.77),('east',-2.63)]:
 for j,y in enumerate([28.3,30.1,32.6,34.7]):student_world('Sideline '+side+' spectator '+str(j),x,y,'seated',j,(-12.93,y),17,'Gym players and spectators')
# Face-to-face conversations in clear areas, not over existing tables.
for group,(x,y) in enumerate([(5.0,25.5),(11.0,12.0),(-29.0,34.0),(-13.2,14.75),(-4.0,10.8)]):
 for j,dx in enumerate([-.42,.42]):student_world('Conversation group '+str(group)+' student '+str(j),x+dx,y,'talking',(group+j)%4,(x-dx,y),19,'Standing conversations')
for j,(x,y) in enumerate([(-38.9,25.8),(-34.9,19.2)]):student_world('Locker bench student '+str(j),x,y,'seated',j,(x+1,y),16.5,'Seated study and social groups')
# Twelve moving students, with floor-safe routes and independently phased gait artwork.
paths=[(823,542,25,9),(789,322,18,9),(611.5,663,.4,27),(291,441,7,27),(932,551,10,7),(466,513,29,3),(291,352,6,23),(731,551,9,6),(194,286,25,3),(640,552,23,4),(515,473,38,2),(939,365,2.5,18)]
for i,(x,y,rx,ry) in enumerate(paths):sprite('Walking student '+str(i+1),x,y,'walking',i%4,size=20,group='Walking students',motion=(rx,ry))
# An orange ball passing between two players; its small height cue is local object motion, not moving light.
bc=bpy.data.collections.new('COURT - looping ball');s.collection.children.link(bc)
ball=plane('Basketball pass',512,350,2,3.6,3.6)
for c in list(ball.users_collection):c.objects.unlink(ball)
bc.objects.link(ball);n,l=tree(ball,'Basketball projection');uv=n.new('ShaderNodeTexCoord');sub=n.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=(.5,.5,0);l.new(uv.outputs['UV'],sub.inputs[0]);length=n.new('ShaderNodeVectorMath');length.operation='LENGTH';l.new(sub.outputs[0],length.inputs[0]);mask=n.new('ShaderNodeMath');mask.operation='LESS_THAN';mask.inputs[1].default_value=.46;l.new(length.outputs['Value'],mask.inputs[0]);shade=n.new('ShaderNodeMapRange');l.new(length.outputs['Value'],shade.inputs['Value']);shade.inputs['From Min'].default_value=0;shade.inputs['From Max'].default_value=.5;shade.inputs['To Min'].default_value=1;shade.inputs['To Max'].default_value=.34;col=n.new('ShaderNodeMixRGB');col.blend_type='MULTIPLY';col.inputs[0].default_value=1;col.inputs[1].default_value=(.7,.19,.025,1);l.new(shade.outputs['Result'],col.inputs[2]);em=n.new('ShaderNodeEmission');l.new(col.outputs[0],em.inputs[0]);tr=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader');l.new(mask.outputs[0],mix.inputs[0]);l.new(tr.outputs[0],mix.inputs[1]);l.new(em.outputs[0],mix.inputs[2]);out=n.new('ShaderNodeOutputMaterial');l.new(mix.outputs[0],out.inputs[0])
p0=worldpixel(-14.5,27.2);p1=worldpixel(-10.2,28.0);a='(2*pi*(frame-1)/144)'
ball.driver_add('location',0).driver.expression=f'{(p0[0]+p1[0])/2}-{(p1[0]-p0[0])/2}*cos{a}';ball.driver_add('location',1).driver.expression=f'{786-(p0[1]+p1[1])/2}+{(p1[1]-p0[1])/2}*cos{a}'
for axis in [0,1]:ball.driver_add('scale',axis).driver.expression=f'1+.15*sin{a}**2'
s.frame_set(1);bpy.context.view_layer.update();s['student_count']=len(records);s['projection_note']='Direct overhead, 24 fps, static detailed floor base; generated students in activity groups. Same blackout mask as v02.'
for im in bpy.data.images:
 if im.source=='FILE' and not im.packed_file:im.pack()
walk.filepath='//imagegen_raw/people_0001.png'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Campus_Center_Lively_Projection.blend'))
(R/'population_manifest.json').write_text(json.dumps({'student_count':len(records),'groups':{k:len(c.objects) for k,c in collections.items()},'people':records,'frames':144,'fps':24,'loop_seconds':6,'keyframes':list(range(1,145,6)),'geometry_and_light_static':True},indent=2))
if preview:
 frames=[1,37,73,109]
else:
 (R/'video_frames').mkdir(exist_ok=True);frames=range(1,145)
for frame in frames:
 s.frame_set(frame);bpy.context.view_layer.update();s.render.resolution_x=1024;s.render.resolution_y=786;s.render.filepath=str(R/(f'preview_{frame:04}.png' if preview else f'video_frames/{frame:04}.png'));bpy.ops.render.render(write_still=True)
 if not preview and (frame-1)%6==0:
  # Save the exact same rendered pixels as the 24 requested key images.
  import shutil
  shutil.copy2(s.render.filepath,R/'frames'/f'{(frame-1)//6+1:04}.png')
 if frame==1:
  s.render.resolution_x=3072;s.render.resolution_y=2358;s.render.filepath=str(R/'Projection_Hero_3x.png');bpy.ops.render.render(write_still=True)
 print('FRAME',frame,flush=True)
print('POPULATION_COMPLETE',len(records))
