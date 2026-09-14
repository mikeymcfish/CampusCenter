import bpy,pathlib,json,math,sys
R=pathlib.Path(__file__).parent
preview='--preview' in sys.argv
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.use_denoising=False;s.cycles.filter_width=.01;s.render.dither_intensity=0
s.render.resolution_x=1024;s.render.resolution_y=786;s.render.resolution_percentage=100;s.render.pixel_aspect_x=s.render.pixel_aspect_y=1
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='8';s.render.film_transparent=False;s.render.fps=4;s.frame_start=1;s.frame_end=24
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0
w=bpy.data.worlds.new('Zero ambient');w.use_nodes=True;w.node_tree.nodes.get('Background').inputs[1].default_value=0;s.world=w
cd=bpy.data.cameras.new('Direct top-down projector');cam=bpy.data.objects.new(cd.name,cd);s.collection.objects.link(cam);cam.location=(512,393,2000);cd.type='ORTHO';cd.ortho_scale=1024;cd.sensor_fit='HORIZONTAL';cd.clip_end=5000;cd.dof.use_dof=False;s.camera=cam
baseim=bpy.data.images.load(str(R/'Projection_Base_Top_Down.png'));maskim=bpy.data.images.load(str(R/'floor_only_mask.png'));maskim.colorspace_settings.name='Non-Color'
def plane(name,x,y,z,sx,sy):
 bpy.ops.mesh.primitive_plane_add(size=1,location=(x,786-y,z));o=bpy.context.object;o.name=name;o.scale=(sx,sy,1);return o
def tree(o,name):
 m=bpy.data.materials.new(name);m.use_nodes=True;o.data.materials.append(m);m.node_tree.nodes.clear();return m.node_tree.nodes,m.node_tree.links
o=plane('IMMUTABLE BASE - floor furniture only',512,393,0,1024,786);n,l=tree(o,'Fixed furnished floor projection')
uv=n.new('ShaderNodeTexCoord');t=n.new('ShaderNodeTexImage');t.image=baseim;t.interpolation='Closest';l.new(uv.outputs['UV'],t.inputs[0]);e=n.new('ShaderNodeEmission');l.new(t.outputs[0],e.inputs[0]);out=n.new('ShaderNodeOutputMaterial');l.new(e.outputs[0],out.inputs[0])
people=bpy.data.collections.new('IMAGEGEN PEOPLE - disable to show base only');s.collection.children.link(people)
# Pixel paths are deliberately small loops in clear circulation areas, away from furniture and walls.
specs=[('Navy student - commons',823,542,25,9,0,0),('Coral student - commons aisle',789,322,18,9,1,1),('Green student - iLab central aisle',615,661,1.5,28,2,2),('Mustard student - west corridor',291,441,7,27,3,3)]
actors=[];texnodes=[]
for name,cx,cy,rx,ry,index,phase in specs:
 actor=plane(name,cx,cy,1,20,20)
 for c in list(actor.users_collection):c.objects.unlink(actor)
 people.objects.link(actor);n,l=tree(actor,name+' generated surface')
 uv=n.new('ShaderNodeTexCoord');scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs['Scale'].default_value=.5;l.new(uv.outputs['UV'],scale.inputs[0]);add=n.new('ShaderNodeVectorMath');add.operation='ADD';l.new(scale.outputs[0],add.inputs[0]);add.inputs[1].default_value=(.5*(index%2),.5*(1-index//2),0)
 tex=n.new('ShaderNodeTexImage');tex.interpolation='Linear';tex.extension='CLIP';l.new(add.outputs[0],tex.inputs[0]);texnodes.append(tex)
 sep=n.new('ShaderNodeSeparateColor');sep.mode='RGB';l.new(tex.outputs[0],sep.inputs[0])
 # Key out only highly saturated magenta; hair, green hoodie, white shoes and coral remain opaque.
 mn=n.new('ShaderNodeMath');mn.operation='MINIMUM';l.new(sep.outputs[0],mn.inputs[0]);l.new(sep.outputs[2],mn.inputs[1]);sub=n.new('ShaderNodeMath');sub.operation='SUBTRACT';l.new(mn.outputs[0],sub.inputs[0]);l.new(sep.outputs[1],sub.inputs[1]);key=n.new('ShaderNodeMapRange');l.new(sub.outputs[0],key.inputs['Value']);key.inputs['From Min'].default_value=.08;key.inputs['From Max'].default_value=.3;key.inputs['To Min'].default_value=1;key.inputs['To Max'].default_value=0;key.clamp=True
 geo=n.new('ShaderNodeNewGeometry');mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';l.new(geo.outputs['Position'],mapping.inputs[0]);mapping.inputs[1].default_value=(1/1024,1/786,0);mt=n.new('ShaderNodeTexImage');mt.image=maskim;mt.interpolation='Closest';mt.extension='CLIP';l.new(mapping.outputs[0],mt.inputs[0]);mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';l.new(key.outputs['Result'],mul.inputs[0]);l.new(mt.outputs[0],mul.inputs[1])
 em=n.new('ShaderNodeEmission');l.new(tex.outputs[0],em.inputs[0]);tr=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader');l.new(mul.outputs[0],mix.inputs[0]);l.new(tr.outputs[0],mix.inputs[1]);l.new(em.outputs[0],mix.inputs[2]);out=n.new('ShaderNodeOutputMaterial');l.new(mix.outputs[0],out.inputs[0])
 # Smooth closed paths and tangent heading, exact repeat at frame 25.
 a=f'(2*pi*(frame-1)/24+{phase*math.pi/2})'
 actor.driver_add('location',0).driver.expression=f'{cx}+{rx}*cos{a}'
 actor.driver_add('location',1).driver.expression=f'{786-cy}-{ry}*sin{a}'
 actor.driver_add('rotation_euler',2).driver.expression=f'atan2({rx}*sin{a},-{ry}*cos{a})'
 actors.append(actor)
rendered=[]
frames=[1,7,13,19] if preview else range(1,25)
for frame in frames:
 image=bpy.data.images.load(str(R/'imagegen_raw'/f'people_{frame:04}.png'),check_existing=True)
 for tex in texnodes:tex.image=image
 s.frame_set(frame);bpy.context.view_layer.update()
 path=(R/f'people_preview_{frame:04}.png') if preview else R/'frames'/f'{frame:04}.png'
 s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
 rendered.append({'frame':frame,'image':str(path.relative_to(R)),'people_source':f'imagegen_raw/people_{frame:04}.png','actors':[{'name':o.name,'pixel_center':[o.location.x,786-o.location.y],'heading':o.rotation_euler.z} for o in actors]})
 print('COMPOSITED',frame,flush=True)
if not preview:
 # Use a native image sequence in the editable file. The source PNGs remain unchanged.
 seq=bpy.data.images.load(str(R/'imagegen_raw/people_0001.png'),check_existing=False);seq.source='SEQUENCE';seq.filepath='//imagegen_raw/people_0001.png'
 for tex in texnodes:tex.image=seq;tex.image_user.frame_duration=24;tex.image_user.frame_start=1;tex.image_user.use_cyclic=True;tex.image_user.use_auto_refresh=True
 baseim.filepath='//Projection_Base_Top_Down.png';maskim.filepath='//floor_only_mask.png'
 s.frame_set(1);s['loop_seconds']=6;s['projection_mode']='Direct overhead, black walls, immutable base. 24 Imagegen character-frame assets, Blender keyed and floor-masked.'
 s['loop_note']='24 unique keyframes, 4 fps / 6 seconds. Imagegen supplies approximate walking poses; spatial paths are mathematically closed.'
 bpy.ops.wm.save_as_mainfile(filepath=str(R/'Projection_24_Frame_Loop.blend'))
 (R/'frames_manifest.json').write_text(json.dumps({'width':1024,'height':786,'fps':4,'duration_seconds':6,'frames':rendered,'motion':'Only Imagegen people; fixed floors, furniture, lighting and camera','mask_last':True},indent=2))
