import bpy,math,json,pathlib,random,hashlib
from mathutils import Vector
R=pathlib.Path(__file__).parent;s=bpy.context.scene;random.seed(31)
source=next(p for p in [R.parent/'projection_print_v02/Campus_Center_Top_Down_Projection.blend',R.parent/'ground_4x_projection_v02/Campus_Center_Top_Down_Projection.blend'] if p.is_file());sourcehash=hashlib.sha256(source.read_bytes()).hexdigest()
coll=bpy.data.collections.new('V03 PROJECTED DETAIL - floor content only');s.collection.children.link(coll)
added=[]
def own(o,name,mat=None):
 o.name=name
 for c in list(o.users_collection):c.objects.unlink(o)
 coll.objects.link(o)
 if mat:o.data.materials.append(mat)
 added.append(name);return o
def mat(name,color,rough=.55,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
navy=mat('V03 painted navy',(.025,.085,.17),.35);white=mat('V03 warm white line paint',(.87,.89,.85),.36);gold=mat('V03 warm ochre paint',(.75,.48,.07),.38);dark=mat('V03 graphite hardware',(.018,.025,.032),.33,.4);paper=mat('V03 paper',(.8,.81,.77),.8);silver=mat('V03 laptop alloy',(.28,.34,.38),.24,.75);screen=mat('V03 blue displays',(.07,.3,.45),.25);terracotta=mat('V03 ceramic pot',(.25,.13,.07),.72);soil=mat('V03 pot soil',(.022,.015,.009),1)
navy.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.15
navy.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.6
def box(name,loc,dim,m,bevel=.02):
 dx,dy,dz=[v/2 for v in dim];verts=[(x,y,z) for x in [-dx,dx] for y in [-dy,dy] for z in [-dz,dz]];faces=[tuple(reversed(f)) for f in [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]];mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);o.location=loc;own(o,name,m)
 if bevel:
  b=o.modifiers.new('Soft real edges','BEVEL');b.width=min(bevel,min(dim)*.35);b.segments=2;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o
def cyl(name,loc,r,depth,m,vertices=32):
 vs=[(r*math.cos(2*math.pi*i/vertices),r*math.sin(2*math.pi*i/vertices),z) for z in [-depth/2,depth/2] for i in range(vertices)];fs=[tuple(reversed(range(vertices))),tuple(range(vertices,2*vertices))]+[(i,(i+1)%vertices,(i+1)%vertices+vertices,i+vertices) for i in range(vertices)];mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],fs);mesh.update();o=bpy.data.objects.new(name,mesh);o.location=loc;return own(o,name,m)
def line(name,pts,width,m):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=width/2;c.bevel_resolution=2;sp=c.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,co in zip(sp.points,pts):p.co=(*co,1)
 o=bpy.data.objects.new(name,c);coll.objects.link(o);c.materials.append(m);added.append(name);return o
def rectline(name,x0,y0,x1,y1,w,m,z=.019):return line(name,[(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z),(x0,y0,z)],w,m)
def arc(name,x,y,r,a,b,w,m,z=.022):return line(name,[(x+r*math.cos(a+(b-a)*i/100),y+r*math.sin(a+(b-a)*i/100),z) for i in range(101)],w,m)
def floor_shader(name,c1,c2,width,height,wood=False):
 m=mat(name,c1,.3 if wood else .65);n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');geo=n.new('ShaderNodeNewGeometry');sep=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Position'],sep.inputs[0]);vec=n.new('ShaderNodeCombineXYZ');l.new(sep.outputs['Y' if wood else 'X'],vec.inputs[0]);l.new(sep.outputs['X' if wood else 'Y'],vec.inputs[1]);brick=n.new('ShaderNodeTexBrick');brick.offset=.5;brick.offset_frequency=2;brick.inputs['Scale'].default_value=1;brick.inputs['Brick Width'].default_value=width;brick.inputs['Row Height'].default_value=height;brick.inputs['Mortar Size'].default_value=.00065 if wood else .006;brick.inputs['Mortar Smooth'].default_value=.001;brick.inputs['Color1'].default_value=(*c1,1);brick.inputs['Color2'].default_value=(*c2,1);brick.inputs['Mortar'].default_value=(.23,.20,.14,1) if wood else (.26,.28,.29,1);l.new(vec.outputs[0],brick.inputs[0]);l.new(brick.outputs['Color'],p.inputs['Base Color'])
 scale=n.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(7,280,1) if wood else (220,220,220);l.new(vec.outputs[0],scale.inputs[0]);noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1;noise.inputs['Detail'].default_value=3;l.new(scale.outputs[0],noise.inputs[0]);bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.0006;l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal']);return m
wood=floor_shader('V03 gym maple individual boards',(.48,.31,.13),(.67,.47,.24),2.0,.11,True)
stone=floor_shader('V03 corridor warm terrazzo tiles',(.47,.49,.47),(.51,.52,.50),1.2,1.2)
locker=floor_shader('V03 locker non slip floor',(.23,.33,.35),(.28,.37,.38),.45,.45)
bath=floor_shader('V03 washroom ceramic tiles',(.67,.72,.70),(.61,.68,.68),.3,.3)
lab=floor_shader('V03 iLab durable pale floor',(.5,.48,.42),(.55,.53,.47),.6,.6)
carpet=mat('V03 dense woven indigo carpet',(.085,.145,.21),.98);n=carpet.node_tree.nodes;l=carpet.node_tree.links;p=n.get('Principled BSDF');tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=240;tex.inputs['Detail'].default_value=2;geo=n.new('ShaderNodeNewGeometry');l.new(geo.outputs['Position'],tex.inputs[0]);mix=n.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(.06,.10,.15,1);mix.inputs[2].default_value=(.13,.21,.28,1);l.new(tex.outputs['Fac'],mix.inputs[0]);l.new(mix.outputs[0],p.inputs['Base Color']);b=n.new('ShaderNodeBump');b.inputs['Distance'].default_value=.001;b.inputs['Strength'].default_value=.16;l.new(tex.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],p.inputs['Normal'])
for o in s.objects:
 if not o.name.startswith('Receiver '):continue
 for m in [stone,locker,bath,lab,carpet,wood]:o.data.materials.append(m)
 idx={m.name:i for i,m in enumerate(o.data.materials)}
 for f in o.data.polygons:
  if abs(f.center.z)>.001 or f.normal.z<.999:continue
  x,y=f.center.x,f.center.y;use=stone
  if -25.7<x<-.16 and 16.38<y<47.24:use=wood
  elif .15<x<16.4 and 14.7<y<30.9:use=carpet
  elif -42<x<-30 and 16<y<29.4:use=locker
  elif x<-41.8 or (x<-32 and 7<y<13):use=bath
  elif -12<x<0 and 0<y<9.4:use=lab
  f.material_index=idx[use.name]
# Material variation on existing fixtures, preserving mesh layout.
for m in bpy.data.materials:
 if not m.use_nodes:continue
 p=m.node_tree.nodes.get('Principled BSDF')
 if not p:continue
 if m.name=='V8 plain light table surface':p.inputs['Base Color'].default_value=(.56,.49,.35,1);p.inputs['Roughness'].default_value=.42
 if m.name=='V8 plain chair shell':p.inputs['Base Color'].default_value=(.2,.32,.37,1);p.inputs['Roughness'].default_value=.47
 if m.name=='Blockout furniture - untextured':p.inputs['Base Color'].default_value=(.22,.3,.32,1);p.inputs['Roughness'].default_value=.7
# A representative basketball layout fitted inside the existing gym footprint.
cx=-12.93;cy=31.81;x0=cx-7.62;x1=cx+7.62;y0=cy-12.8;y1=cy+12.8
rectline('Basketball boundary',x0,y0,x1,y1,.055,navy)
line('Half court',[(x0,cy,.022),(x1,cy,.022)],.05,navy);arc('Center circle',cx,cy,1.83,0,2*math.pi,.055,navy)
cyl('Center court roundel',(cx,cy,.012),1.23,.008,navy)
arc('Center crest gold ring',cx,cy,1.13,0,2*math.pi,.045,gold)
def label(name,text,loc,size,m,rotation=0):
 c=bpy.data.curves.new(name,'FONT');c.body=text;c.align_x='CENTER';c.align_y='CENTER';c.size=size;c.extrude=.0005;o=bpy.data.objects.new(name,c);coll.objects.link(o);o.location=loc;o.rotation_euler.z=rotation;c.materials.append(m);added.append(name)
label('Center KING','KING',(cx,cy,.025),.55,white)
for side,base,sign in [('South',y0,1),('North',y1,-1)]:
 free=base+sign*5.79;basket=base+sign*1.575
 box(side+' painted key',(cx,base+sign*2.895,.007),(3.66,5.79,.008),navy,0)
 rectline(side+' lane',cx-1.83,min(base,free),cx+1.83,max(base,free),.05,white)
 arc(side+' free throw circle',cx,free,1.83,0,2*math.pi,.045,white)
 arc(side+' three point arc',cx,basket,6.02,0 if sign==1 else math.pi,math.pi if sign==1 else 2*math.pi,.055,navy)
 for xx in [cx-6.02,cx+6.02]:line(side+' three point corner',[(xx,base,.022),(xx,basket,.022)],.055,navy)
 for dx in [-1,1]:
  for j in range(1,5):line(side+' lane tick',[(cx+dx*1.85,base+sign*(1.2+j*.78),.025),(cx+dx*2.12,base+sign*(1.2+j*.78),.025)],.07,navy)
 # Projected hoop structure is only virtual imagery, not a floating print part.
 box(side+' basket backboard',(cx,base+sign*1.22,3.05),(1.8,.08,1.05),white)
 arc(side+' orange hoop',cx,basket,.229,0,2*math.pi,.026,gold,z=3.05)
 for j in range(12):
  a=j*math.pi/6;line(side+' net cord',[(cx+.225*math.cos(a),basket+.225*math.sin(a),3.03),(cx+.12*math.cos(a+.3),basket+.12*math.sin(a+.3),2.62)],.008,white)
 box(side+' hoop stanchion',(cx,base-.35*sign,1.6),(.16,.16,3.2),dark)
 label(side+' baseline lettering','K I N G',(cx,base-sign*.68,.023),.58,navy,0 if sign==1 else math.pi)
rectline('Secondary volleyball boundaries',cx-4.5,cy-9,cx+4.5,cy+9,.028,gold)
for yy in [cy-3,cy+3]:line('Volleyball attack line',[(cx-4.5,yy,.025),(cx+4.5,yy,.025)],.028,gold)
# Low sideline bleachers, bags and a scorer table, all inside the receiving floors.
for side,x in [('West',-23.15),('East',-2.25)]:
 for row in range(3):
  xx=x+(.38*row if side=='West' else -.38*row);box(side+' bleacher bench '+str(row),(xx,cy,.25+row*.23),(.34,9,.11),navy)
 for y in [cy-4,cy-2,cy,cy+2,cy+4]:box(side+' seat supports',(x,y,.18),(.9,.13,.35),dark)
box('Scorer table',(-2.2,cy+6,.73),(.8,2.3,.08),wood)
# Practical tabletop detail at the same coordinates as existing surfaces.
propcounts={'laptops':0,'notebooks':0,'cups':0,'plants':0}
def laptop(x,y,z,angle=0):
 o=box('Open laptop base',(x,y,z+.012),(.31,.23,.021),silver,.01);o.rotation_euler.z=angle
 lid=box('Open laptop display',(x,y+.103,z+.116),(.31,.014,.215),dark,.009);lid.rotation_euler.x=math.radians(-12)
 glass=box('Laptop screen',(x,y+.088,z+.12),(.277,.004,.17),screen,.004);glass.rotation_euler.x=math.radians(-12)
 for row in range(4):
  for col in range(9):box('Laptop key',(x-.118+col*.029,y-.05+row*.024,z+.026),(.022,.018,.004),dark,0)
 propcounts['laptops']+=1
def book(x,y,z):
 color=random.choice([navy,gold,terracotta]);a=random.uniform(-.35,.35);o=box('Student notebook',(x,y,z+.009),(.18,.25,.018),color,.002);o.rotation_euler.z=a;propcounts['notebooks']+=1
def cup(x,y,z):
 cyl('Cafe paper cup',(x,y,z+.05),.043,.1,paper);cyl('Cup coffee',(x,y,z+.102),.035,.004,soil);propcounts['cups']+=1
for x,y in [(-38.75,37.85),(-34.7,37.85),(-36.0,34.18),(-33.1,34.18),(-13.3,12),(14.1,2.4)]:laptop(x,y,.75);book(x+.38,y,.75)
for x,y in [(-24.1,9.1),(-23.7,10.7),(-18.55,9.4),(-18.2,10.8),(-2.25,2.1),(-2.25,4.3),(-2.25,6.5),(6.5,16.7),(7.3,18.7)]:laptop(x,y,.75);book(x+.35,y+.25,.75)
for x,y,z in [(9.84,26.75,.48),(9.22,23.01,.48),(2.98,22.37,.48),(.85,21.33,.48),(10.4,19.3,.48),(5.73,22.7,.48),(1.7,25.5,.75),(1.7,17.1,.75),(13.2,18.2,1.06),(15.6,19.8,.92)]:book(x-.1,y,z);cup(x+.15,y+.12,z)
for x,y in [(-7.7,2.1),(-7.7,7.7),(-10.4,5.2)]:
 for j in range(5):box('iLab project component',(x+random.uniform(-.3,.3),y+random.uniform(-.3,.3),.96),(.12,.18,.05),random.choice([navy,gold,silver]),.01)
leafmats=[mat('V03 foliage '+str(i),c,.55) for i,c in enumerate([(.045,.12,.055),(.08,.21,.085),(.14,.27,.10),(.1,.18,.06)])]
def plant(x,y):
 cyl('Ceramic planter',(x,y,.25),.24,.5,terracotta);cyl('Planter soil',(x,y,.505),.22,.02,soil)
 for j in range(28):
  a=j*2.399963;rr=random.uniform(.2,.5);height=random.uniform(.65,1.1);start=Vector((x,y,.55));end=Vector((x+rr*math.cos(a),y+rr*math.sin(a),height));mid=(start+end)*.5+Vector((0,0,.13));cross=Vector((-math.sin(a),math.cos(a),0))*.11;verts=[start,mid+cross,end,mid-cross,mid+Vector((0,0,.018))];mesh=bpy.data.meshes.new('Curved living leaf');mesh.from_pydata(verts,[],[(0,1,4),(1,2,4),(2,3,4),(3,0,4)]);mesh.update();o=bpy.data.objects.new('Living foliage blade',mesh);coll.objects.link(o);mesh.materials.append(random.choice(leafmats));added.append(o.name)
 propcounts['plants']+=1
for xy in [(1.3,28.4),(14.8,28.4),(15.5,22),(4,29.1),(11.9,14.0),(4.0,12.8),(-10.2,12.2),(-29.25,36),(-29.4,30.2),(-43.9,12.2),(11.9,2.2),(-25.1,7.4)]:plant(*xy)
# Locker-top panel rhythms and nearby benches/bags make the overhead layout readable.
for y in [25.8,19.2]:
 for x in [-39.9,-37.9,-35.9,-33.9]:
  box('Locker top navy inset',(x,y,1.805),(.82,2.2,.02),navy,.005)
  for j in range(6):line('Locker bay divider',[(x-.4,y-1.05+j*.42,1.825),(x+.4,y-1.05+j*.42,1.825)],.013,silver)
 for x in [-38.9,-34.9]:box('Changing bench',(x,y,.46),(.35,1.4,.09),wood)
for x,y in [(-22.7,26.8),(-22.7,36.8),(-3.1,35),(-38.9,20.4),(-34.9,27.1),(3.8,21.7)]:box('Canvas sports bag',(x,y,.15),(.28,.47,.25),random.choice([navy,dark,terracotta]),.09)
s.render.resolution_x=3072;s.render.resolution_y=2358;s.render.resolution_percentage=100;s.cycles.samples=96;s.cycles.adaptive_threshold=.02;s.cycles.use_denoising=True;s.render.dither_intensity=0
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='CUDA';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='CUDA'
s.cycles.device='GPU'
for o in s.objects:
 if o.type=='LIGHT' and not o.hide_render:o.data.energy=11000;o.data.size=38
s.world.node_tree.nodes.get('Background').inputs[1].default_value=.45
s['v03_note']='Projection-only visual enrichment: representative court graphics and equipment, room finishes, desktop props and foliage. Print shell, camera and wall mask unchanged.'
(R/'render_contract.json').write_text(json.dumps({'source':str(source),'source_sha256':sourcehash,'base_resolution':[3072,2358],'output_resolution':[1024,786],'reference_images':24,'video_frames':144,'fps':24,'duration_seconds':6,'student_count':93,'camera':'unchanged vertical ORTHO','samples':96,'engine':'Cycles CUDA','moving_sun':False,'walls':'exact existing binary mask','court':'representative fit, not a verified survey of existing gym markings'},indent=2))
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Campus_Center_Detailed_Projection.blend'))
s.render.filepath=str(R/'base_beauty_3x.png');bpy.ops.render.render(write_still=True)
(R/'detail_report.json').write_text(json.dumps({'source_unchanged':hashlib.sha256(source.read_bytes()).hexdigest()==sourcehash,'added_objects':len(added),'prop_counts':propcounts,'court_bounds_world_m':[x0,y0,x1,y1],'render_resolution':[3072,2358]},indent=2))
print('DETAIL_COMPLETE',len(added),propcounts)
