import bpy,bmesh,json,pathlib,random,math,hashlib
from mathutils import Vector,Matrix
R=pathlib.Path(__file__).parent;s=bpy.context.scene;s.frame_set(1);random.seed(4204)
report={'source_sha256':hashlib.sha256((R/'Source_Copy.blend').read_bytes()).hexdigest(),'hidden':[],'changed_geometry':[],'added':[],'materials':[],'plant_instances':[]}
cols={}
for name in ['Site grass and concrete','Textured planting','Fireplace fire']:
 c=bpy.data.collections.new('V04 '+name);s.collection.children.link(c);cols[name]=c
category='Site grass and concrete'
def color(h):
 vals=[int(h[i:i+2],16)/255 for i in (0,2,4)];return tuple(v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4 for v in vals)+(1,)
def material(name,c,rough=.75):
 m=bpy.data.materials.new('V04 '+name);m.use_nodes=True;m.diffuse_color=color(c);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color(c);bs.inputs['Roughness'].default_value=rough;return m
def mesh(name,vs,fs,mat):
 me=bpy.data.meshes.new('V04 '+name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('V04 '+name,me);cols[category].objects.link(o);me.materials.append(mat);report['added'].append(o.name);return o
def slab(name,x0,x1,y0,y1,z,mat):return mesh(name,[(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z)],[(0,1,2,3)],mat)
def hide(o):
 if o and not o.hide_render:o.hide_render=True;o.hide_viewport=True;report['hidden'].append(o.name)
def node(nt,t):return nt.nodes.new(t)
def texture_noise(m,base1,base2,scale,rough=.85,bumpdist=.0008):
 nt=m.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');g=node(nt,'ShaderNodeNewGeometry');n=node(nt,'ShaderNodeTexNoise');n.inputs['Scale'].default_value=scale;n.inputs['Detail'].default_value=4;nt.links.new(g.outputs['Position'],n.inputs['Vector']);r=node(nt,'ShaderNodeValToRGB');r.color_ramp.elements[0].color=color(base1);r.color_ramp.elements[1].color=color(base2);nt.links.new(n.outputs['Fac'],r.inputs[0]);nt.links.new(r.outputs[0],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=rough
 bump=node(nt,'ShaderNodeBump');bump.inputs['Distance'].default_value=bumpdist;bump.inputs['Strength'].default_value=.22;nt.links.new(n.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],bs.inputs['Normal']);return g,n,bs
# Concrete walk and plaza connect the existing entrance approach to surrounding lawn.
concrete=material('Cast concrete','C5C1B5');texture_noise(concrete,'ACA99F','D3CFC3',55,.88,.0011)
grassmat=material('Mown lawn','52703A');g,n,bs=texture_noise(grassmat,'3D5327','6B7D42',3,.95,.003)
# Dense short-grass PBR beneath the individual blades, blended at two orientations.
nt=grassmat.node_tree;scale=node(nt,'ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=1/1.4;nt.links.new(g.outputs['Position'],scale.inputs[0]);rotate=node(nt,'ShaderNodeVectorRotate');rotate.rotation_type='AXIS_ANGLE';rotate.inputs['Axis'].default_value=(0,0,1);rotate.inputs['Angle'].default_value=1.5708;nt.links.new(scale.outputs[0],rotate.inputs['Vector']);offset=node(nt,'ShaderNodeVectorMath');offset.operation='ADD';offset.inputs[1].default_value=(.37,.63,0);nt.links.new(rotate.outputs[0],offset.inputs[0])
im=bpy.data.images.load(str(R/'assets/Grass001/Grass001_2K-JPG_Color.jpg'));im.pack();a=node(nt,'ShaderNodeTexImage');b=node(nt,'ShaderNodeTexImage');a.image=im;b.image=im;nt.links.new(scale.outputs[0],a.inputs['Vector']);nt.links.new(offset.outputs[0],b.inputs['Vector']);blend=node(nt,'ShaderNodeMixRGB');nt.links.new(n.outputs['Fac'],blend.inputs[0]);nt.links.new(a.outputs['Color'],blend.inputs[1]);nt.links.new(b.outputs['Color'],blend.inputs[2]);nt.links.new(blend.outputs[0],bs.inputs['Base Color'])
bump=node(nt,'ShaderNodeBump');bump.inputs['Strength'].default_value=.3;bump.inputs['Distance'].default_value=.009;nt.links.new(blend.outputs[0],bump.inputs['Height']);nt.links.new(bump.outputs[0],bs.inputs['Normal'])
ground=slab('Continuous lawn',-110,145,-110,150,-.041,grassmat)
slab('Entry plaza',16.4,35,9.45,14.70,-.020,concrete)
slab('Facade sidewalk',16.4,19.85,-5.0,38.0,-.019,concrete)
slab('Campus connecting walk',-52,35,-5.0,-2.1,-.019,concrete)
slab('North connecting walk',-1,19.85,32,35,-.019,concrete)
old=bpy.data.objects.get('V5_Entry_approach')
if old:
 old.data=old.data.copy()
 for i in range(len(old.data.materials)):old.data.materials[i]=concrete
joint=material('Concrete control joints','77766D',.94)
for x in [20,23,26,29,32]:slab('Plaza control joint',x-.003,x+.003,9.45,14.70,-.018,joint)
for y in range(-3,38,3):slab('Walk control joint',16.4,19.85,y-.003,y+.003,-.017,joint)
# Larger banners: two times both width and height, preserving their centers.
for o in list(s.objects):
 if o.type=='MESH' and o.name.startswith(('V03 King banner ','V03 Banner top rail ','V03 Banner bottom weight ')):
  ys=[v.co.y for v in o.data.vertices];cy=(min(ys)+max(ys))/2;o.data=o.data.copy()
  for v in o.data.vertices:v.co.y=cy+(v.co.y-cy)*2;v.co.z=5.5+(v.co.z-5.5)*2
  report['changed_geometry'].append(o.name)
# Retain the obstructing curved group as a disabled alternative, clearing the fire sightline.
hide(bpy.data.objects.get('V15_Commons_curved_lounge'))
category='Fireplace fire'
fire=material('Imagegen fire insert','000000');nt=fire.node_tree;nt.nodes.clear();im=node(nt,'ShaderNodeTexImage');im.image=bpy.data.images.load(str(R/'assets/fire_insert.png'));im.image.pack();em=node(nt,'ShaderNodeEmission');em.inputs['Strength'].default_value=3.2;out=node(nt,'ShaderNodeOutputMaterial');nt.links.new(im.outputs['Color'],em.inputs['Color']);nt.links.new(em.outputs[0],out.inputs['Surface'])
x=6.117278;z=.68;w=1.17;h=.78;y=30.445
o=mesh('Fire billboard',[(x-w/2,y,z-h/2),(x+w/2,y,z-h/2),(x+w/2,y,z+h/2),(x-w/2,y,z+h/2)],[(0,1,2,3)],fire);uv=o.data.uv_layers.new(name='UVMap')
for i,p in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[i].uv=p
data=bpy.data.lights.new('V04 Warm hearth glow','AREA');data.energy=75;data.color=(1,.22,.045);data.shape='RECTANGLE';data.size=.85;data.size_y=.38
light=bpy.data.objects.new(data.name,data);cols[category].objects.link(light);light.location=(x,30.12,.66);light.rotation_euler=Vector((0,-1,0)).to_track_quat('-Z','Y').to_euler();report['added'].append(light.name)
# Replace visibly repeating bitmap walls with world-space procedural variation.
def projected(nt):
 g=node(nt,'ShaderNodeNewGeometry');p=node(nt,'ShaderNodeSeparateXYZ');nt.links.new(g.outputs['Position'],p.inputs[0]);c=node(nt,'ShaderNodeCombineXYZ');add=node(nt,'ShaderNodeMath');add.operation='ADD';nt.links.new(p.outputs['X'],add.inputs[0]);nt.links.new(p.outputs['Y'],add.inputs[1]);nt.links.new(add.outputs[0],c.inputs['X']);nt.links.new(p.outputs['Z'],c.inputs['Y']);return g,c
for name,c1,c2,mortar in [('Gray thin brick','96978F','A6A59A','86877F'),('Warm ivory facade brick','C0BBAC','CFC8B6','ABA89C')]:
 m=bpy.data.materials[name];nt=m.node_tree;nt.nodes.clear();bs=node(nt,'ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=.9;out=node(nt,'ShaderNodeOutputMaterial');nt.links.new(bs.outputs[0],out.inputs['Surface']);g,co=projected(nt)
 brick=node(nt,'ShaderNodeTexBrick');brick.offset=.5;brick.offset_frequency=2;brick.inputs['Scale'].default_value=1;brick.inputs['Brick Width'].default_value=.23;brick.inputs['Row Height'].default_value=.075;brick.inputs['Mortar Size'].default_value=.003;brick.inputs['Mortar Smooth'].default_value=.001;brick.inputs['Color1'].default_value=color(c1);brick.inputs['Color2'].default_value=color(c2);brick.inputs['Mortar'].default_value=color(mortar);nt.links.new(co.outputs[0],brick.inputs['Vector'])
 noise=node(nt,'ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1.9;noise.inputs['Detail'].default_value=4;nt.links.new(g.outputs['Position'],noise.inputs['Vector']);mix=node(nt,'ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.17;nt.links.new(brick.outputs['Color'],mix.inputs[1]);nt.links.new(noise.outputs['Fac'],mix.inputs[2]);nt.links.new(mix.outputs[0],bs.inputs['Base Color'])
 bump=node(nt,'ShaderNodeBump');bump.invert=True;bump.inputs['Distance'].default_value=.003;bump.inputs['Strength'].default_value=.33;nt.links.new(brick.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],bs.inputs['Normal']);report['materials'].append(name)
for name,lo,hi in [('Warm white plaster','DCDAD3','E1DFD8'),('V02 Light blue matte interior paint','ADC8DA','B4CEDE')]:
 m=bpy.data.materials[name];nt=m.node_tree;nt.nodes.clear();bs=node(nt,'ShaderNodeBsdfPrincipled');out=node(nt,'ShaderNodeOutputMaterial');nt.links.new(bs.outputs[0],out.inputs['Surface']);texture_noise(m,lo,hi,125,.92,.00032);report['materials'].append(name)
# Stochastic UV warping and multiscale blending remove the conspicuous short oak repeat.
wood=bpy.data.materials['Natural oak'];nt=wood.node_tree;nt.nodes.clear();bs=node(nt,'ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=.5;out=node(nt,'ShaderNodeOutputMaterial');nt.links.new(bs.outputs[0],out.inputs['Surface']);g,co=projected(nt)
stretch=node(nt,'ShaderNodeVectorMath');stretch.operation='MULTIPLY';stretch.inputs[1].default_value=(.8,95,1);nt.links.new(co.outputs[0],stretch.inputs[0]);noise=node(nt,'ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1;noise.inputs['Detail'].default_value=5;noise.inputs['Roughness'].default_value=.65;nt.links.new(stretch.outputs[0],noise.inputs['Vector']);r=node(nt,'ShaderNodeValToRGB');r.color_ramp.elements[0].color=color('947756');r.color_ramp.elements[1].color=color('C8AA80');nt.links.new(noise.outputs['Fac'],r.inputs[0]);nt.links.new(r.outputs[0],bs.inputs['Base Color']);bump=node(nt,'ShaderNodeBump');bump.inputs['Distance'].default_value=.0006;bump.inputs['Strength'].default_value=.14;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],bs.inputs['Normal']);report['materials'].append('Natural oak')
# Clean indoor blue wall portion of the older region-mixed material also gets subtle paint microtexture.
mixed=bpy.data.materials.get('V02 Commons blue feature wall')
if mixed:
 for b in [n for n in mixed.node_tree.nodes if n.type=='BSDF_PRINCIPLED' and not n.inputs['Base Color'].is_linked]:
  nt=mixed.node_tree;g=node(nt,'ShaderNodeNewGeometry');n=node(nt,'ShaderNodeTexNoise');n.inputs['Scale'].default_value=125;nt.links.new(g.outputs['Position'],n.inputs['Vector']);bump=node(nt,'ShaderNodeBump');bump.inputs['Distance'].default_value=.0003;bump.inputs['Strength'].default_value=.15;nt.links.new(n.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],b.inputs['Normal'])
# Photographic HDRI lighting, visible sky and reflections. The panorama is illustrative context.
world=bpy.data.worlds.new('V04 Greenwich Park photographic environment');world.use_nodes=True;nt=world.node_tree;nt.nodes.clear();coord=node(nt,'ShaderNodeTexCoord');mapping=node(nt,'ShaderNodeMapping');mapping.inputs['Rotation'].default_value[2]=math.radians(115);nt.links.new(coord.outputs['Generated'],mapping.inputs['Vector'])
env=node(nt,'ShaderNodeTexEnvironment');env.image=bpy.data.images.load(str(R/'assets/greenwich_park_4k.hdr'));env.image.pack();nt.links.new(mapping.outputs[0],env.inputs['Vector']);bg=node(nt,'ShaderNodeBackground');bg.inputs['Strength'].default_value=.65;nt.links.new(env.outputs['Color'],bg.inputs['Color']);out=node(nt,'ShaderNodeOutputWorld');nt.links.new(bg.outputs[0],out.inputs['Surface']);s.world=world
for o in s.objects:
 if o.type=='LIGHT' and o.data.type=='SUN':
  o.hide_render=False;o.data.energy=1.5;o.data.angle=math.radians(3);o.data.color=(1,.95,.85);o.rotation_euler=Vector((-.65,.35,-.75)).to_track_quat('-Z','Y').to_euler()
# Replace all old procedural foliage with photo-textured downloaded meshes.
for o in list(bpy.data.collections['V03 Planting'].objects):hide(o)
category='Textured planting';templates={};all_new_images=set(bpy.data.images)
def load_models(key):
 with bpy.data.libraries.load(str(R/'assets'/key/(key+'.blend')),link=False) as (a,b):b.objects=[n for n in a.objects if key=='potted_plant_01' or n.endswith('LOD0') and ('geonodes' not in n and 'geometry_nodes' not in n)]
 return [o for o in b.objects if o and o.type=='MESH']
def normalize(o):
 o.data=o.data.copy();o.data.transform(o.matrix_basis);o.matrix_basis=Matrix.Identity(4);vs=[v.co for v in o.data.vertices];lo=Vector([min(v[i] for v in vs) for i in range(3)]);hi=Vector([max(v[i] for v in vs) for i in range(3)]);o.data.transform(Matrix.Translation((-(lo.x+hi.x)/2,-(lo.y+hi.y)/2,-lo.z)));return hi-lo
pots=load_models('potted_plant_01');plantcol=bpy.data.collections.new('V04 ASSET potted plant')
for o in pots:plantcol.objects.link(o);o.hide_render=False;o.hide_viewport=False
def instance(coll,name,p,scale,angle):
 o=bpy.data.objects.new('V04 '+name,None);o.instance_type='COLLECTION';o.instance_collection=coll;cols[category].objects.link(o);o.location=p;o.scale=(scale,)*3;o.rotation_euler.z=angle;report['added'].append(o.name);report['plant_instances'].append(o.name);return o
for i,(x,y) in enumerate([(15.35,29.7),(1.5,29.0)]):instance(plantcol,'Indoor textured plant '+str(i),(x,y,0),1.40 if i else 1.55,i*2.0)
shrubs=load_models('shrub_03');grasses=load_models('grass_medium_01')
for key,objects in [('shrub',shrubs),('grass',grasses)]:
 templates[key]=[]
 for o in objects:
  dims=normalize(o);c=bpy.data.collections.new('V04 ASSET '+o.name);c.objects.link(o);o.hide_render=False;o.hide_viewport=False;templates[key].append((c,dims,o))
soil=material('Dark planting mulch','30291D');texture_noise(soil,'292018','514735',75,1,.005)
for y in [7,18]:
 slab('Entry planter mulch',20.41,21.59,y-1.43,y+1.43,.701,soil)
 for i in range(120):
  c,d,o=random.choice(templates['shrub']);height=random.uniform(.5,.92);instance(c,'Entry shrub '+str(y)+' '+str(i),(21+random.uniform(-.38,.38),y+random.uniform(-1.14,1.14),.705),height/d.z,random.random()*math.tau)
for y in [8,18,25]:
 slab('Terrace planter mulch',15.41,15.99,y-.55,y+.55,4.836,soil)
 for i in range(30):
  c,d,o=random.choice(templates['grass']);instance(c,'Terrace grass '+str(y)+' '+str(i),(15.70+random.uniform(-.17,.17),y+random.uniform(-.42,.42),4.84),random.uniform(.28,.46)/d.z,random.random()*math.tau)
# Near-field turf blades in a single batched mesh, with shared photo-textured material.
tuft=min(grasses,key=lambda o:len(o.data.vertices));vs=[];fs=[];uvs=[]
baseuv=tuft.data.uv_layers.active;srcverts=[v.co.copy() for v in tuft.data.vertices];srcfaces=[list(p.vertices) for p in tuft.data.polygons]
for i in range(20000):
 x=random.uniform(19.9,40);y=random.uniform(-1,34)
 if 9.2<y<14.9 and x<35.2:continue
 if 20.2<x<21.8 and (5.3<y<8.7 or 16.3<y<19.7):continue
 a=random.random()*math.tau;scale=random.uniform(.65,1.15);M=Matrix.Translation((x,y,-.037))@Matrix.Rotation(a,4,'Z')@Matrix.Scale(scale,4);off=len(vs);vs.extend([M@v for v in srcverts]);fs.extend([[off+j for j in f] for f in srcfaces]);uvs.extend([tuple(u.uv) for u in baseuv.data])
o=mesh('Mown lawn textured blades',vs,fs,tuft.data.materials[0]);uv=o.data.uv_layers.new(name='UVMap')
for u,v in zip(uv.data,uvs):u.uv=v
# Repair imported texture paths from the exact downloaded dependency tree; pack for portability.
lookup={p.name:p for p in (R/'assets').rglob('*') if p.is_file()}
for im in set(bpy.data.images)-all_new_images:
 if im.source=='FILE':
  p=lookup.get(pathlib.Path(im.filepath.replace('\\','/')).name)
  if p:im.filepath=str(p);im.reload();im.pack()
# Preserve the original route and add an unobstructed close fireplace camera.
data=bpy.data.cameras.new('07_Fireplace');cam=bpy.data.objects.new(data.name,data);cols['Fireplace fire'].objects.link(cam);cam.location=(8.4,24.8,1.5);cam.rotation_euler=(Vector((6.117,30.25,1.65))-cam.location).to_track_quat('-Z','Y').to_euler();data.lens=36;data.dof.use_dof=True;data.dof.aperture_fstop=5.6;data.dof.focus_distance=5.9;report['added'].append(cam.name)
s.camera=bpy.data.objects['02_Commons'];s['cycles_studio_version']='v04';s['fire_insert']='Static imagegen billboard and warm area-light glow; not simulated flame animation';s['environment']='CC0 Greenwich Park HDRI, illustrative backdrop rather than actual campus';s['site']='Grass and concrete at the modeled entrance; simplified landscape context'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Campus_Center_Cycles_Studio.blend'))
report['fire_generated_asset']='assets/fire_insert.png';report['banner_dimensions_m']=[1.4,4.2];report['mesh_count']=sum(o.type=='MESH' for o in s.objects);report['added_count']=len(report['added']);(R/'build_report.json').write_text(json.dumps(report,indent=2));print('V04_BUILD_COMPLETE',report['added_count'],flush=True)
