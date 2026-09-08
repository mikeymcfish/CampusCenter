import bpy,bmesh,math,random,json,pathlib,hashlib
from mathutils import Vector
R=pathlib.Path(__file__).parent;s=bpy.context.scene;s.frame_set(1);random.seed(55)
made=[];hidden=[];art=[]
c=bpy.data.collections.new('V05 Student artwork and notices');s.collection.children.link(c)
def mat(n,h,rough=.8,metal=0):
 m=bpy.data.materials.new('V05 '+n);m.use_nodes=True;v=[int(h[i:i+2],16)/255 for i in (0,2,4)];rgba=tuple(x/12.92 if x<.04045 else ((x+.055)/1.055)**2.4 for x in v)+(1,);b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=rgba;b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal;return m
def mesh(n,vs,fs,m):
 me=bpy.data.meshes.new('V05 '+n);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(me.name,me);c.objects.link(o);me.materials.append(m);made.append(o.name);return o
def box(n,p,d,m,b=.008):
 vs=[(p[0]+a*d[0]/2,p[1]+q*d[1]/2,p[2]+k*d[2]/2) for k in [-1,1] for q in [-1,1] for a in [-1,1]]
 o=mesh(n,vs,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],m)
 if b:mod=o.modifiers.new('Soft edges','BEVEL');mod.width=b;mod.segments=3
 return o
def panel(n,p,u,w,h,m,tilt=0):
 p=Vector(p);u=Vector(u);v=Vector((0,0,1));u,v=u*math.cos(tilt)+v*math.sin(tilt),v*math.cos(tilt)-u*math.sin(tilt)
 o=mesh(n,[p-u*w/2-v*h/2,p+u*w/2-v*h/2,p+u*w/2+v*h/2,p-u*w/2+v*h/2],[(0,1,2,3)],m);uv=o.data.uv_layers.new()
 for a,b in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)]):a.uv=b
 return o
def hide(o):o.hide_render=True;o.hide_viewport=True;hidden.append(o.name)
paper=mat('Warm paper','E9E4D7');black=mat('Charcoal metal','252526',.38,.35);stone=mat('Warm honed limestone','C4BCAF',.75);oak=bpy.data.materials['Natural oak'];cork=mat('Pinboard felt','59696B');tape=mat('Masking tape','DBD0B0');charcoal=mat('Fireplace mineral finish','464C50',.85)
nt=charcoal.node_tree;noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=30;bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.001;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],nt.nodes.get('Principled BSDF').inputs['Normal'])
mats={}
for p in sorted((R/'assets').glob('*.png')):
 m=mat(p.stem,'FFFFFF',.94);nt=m.node_tree;im=nt.nodes.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(p));im.image.pack();nt.links.new(im.outputs['Color'],nt.nodes.get('Principled BSDF').inputs['Base Color']);mats[p.stem]=m
def artwork(key,p,u,w=.45,framed=False):
 h=w*4/3;normal=Vector(u).cross(Vector((0,0,1)));p=Vector(p)
 if framed:panel('Frame '+str(len(art)),p-normal*.006,u,w+.055,h+.055,oak)
 else:
  for dx in [-w*.34,w*.34]:panel('Tape '+str(len(made)),p+Vector(u)*dx+Vector((0,0,h*.48))+normal*.003,u,.09,.038,tape,random.uniform(-.14,.14))
 o=panel(key+' '+str(len(art)),p,u,w,h,mats[key],0 if framed else random.uniform(-.018,.018));art.append({'object':o.name,'asset':key,'position':list(p),'size':[w,h]})
# Enlarge the complete three-banner assemblies by another 25 percent, within the double-height volume.
for o in list(s.objects):
 if o.type=='MESH' and o.name.startswith(('V03 King banner ','V03 Banner top rail ','V03 Banner bottom weight ')):
  ys=[v.co.y for v in o.data.vertices];cy=(min(ys)+max(ys))/2;o.data=o.data.copy()
  for v in o.data.vertices:v.co.y=cy+(v.co.y-cy)*1.25;v.co.z=5.5+(v.co.z-5.5)*1.25
# Replace geometric placeholder artwork with a varied student gallery on the existing gym wall.
for o in list(s.objects):
 if o.name.startswith(('V03 Gallery ','V03 Art shape ')):hide(o)
keys=['portrait','landscape','portrait2','still_life']
for floor,z in [('upper',5.95),('lower',1.85)]:
 for i,x in enumerate([-24,-22,-20,-18,-16,-14,-12,-10,-8,-6]):
  artwork(keys[(i+(floor=='lower'))%4],(x,16.045,z+random.uniform(-.13,.13)),(1,0,0),[.52,.70,.43,.60][i%4],i%3!=1)
# Commons community noticeboard below the enlarged banners, safely above the built-in seating.
panel('Commons community board',(.214,22.25,2.16),(0,1,0),2.65,1.0,cork)
for i,key in enumerate(['clubs','food_drive','ilab','repair']):artwork(key,(.23,21.33+i*.61,2.16),(0,1,0),.43)
# Ground-floor corridor notices, backed by the solid gym wall.
for i,x in enumerate([-23,-18,-13]):
 artwork(['food_drive','clubs','repair'][i],(x,16.04,2.0),(1,0,0),.40)
# iLab east wall: high enough to clear existing equipment, facing into the room.
for i,(y,key) in enumerate([(2.2,'ilab'),(3.45,'repair'),(4.7,'still_life'),(6.0,'ilab'),(7.4,'clubs'),(8.5,'repair')]):
 artwork(key,(-.145,y,2.65),(0,-1,0),.48 if i%2 else .60)
# iLab west wall section has no door below y=8.4.
for i,key in enumerate(['repair','landscape','ilab']):artwork(key,(-11.435,4.5+i*1.15,2.65),(0,1,0),.52, i==1)
# Modern projecting fireplace assembly, covering the former small opening without removing the architectural pier.
c=bpy.data.collections.new('V05 Modern fireplace');s.collection.children.link(c);x=6.117278
for o in list(s.objects):
 if o.name in ['V6_V5_Fireplace_hearth_corrected','V04 Fire billboard']:hide(o)
box('Wide limestone hearth',(x,29.82,.19),(3.4,1.02,.28),stone,.025)
box('Surround left',(x-1.19,30.025,1.32),(.42,.43,2.00),charcoal,.014)
box('Surround right',(x+1.19,30.025,1.32),(.42,.43,2.00),charcoal,.014)
box('Surround upper',(x,30.025,1.965),(1.96,.43,.71),charcoal,.008)
box('Surround lower',(x,30.025,.48),(1.96,.43,.32),charcoal,.008)
box('Oak mantel',(x,29.97,2.38),(3.10,.61,.14),oak,.018)
box('Dark firebox back',(x,30.20,1.12),(1.98,.045,.96),black)
for dx in [-.99,.99]:box('Firebox return',(x+dx,30.00,1.12),(.025,.38,.96),black,.003)
for z in [.64,1.60]:box('Firebox lintel sill',(x,30.00,z),(2.0,.38,.025),black,.003)
fire=bpy.data.materials['V04 Imagegen fire insert'];panel('Wide natural flame insert',(x,30.166,1.10),(1,0,0),1.88,.91,fire)
light=bpy.data.objects['V04 Warm hearth glow'];light.location=(x,29.68,1.05);light.data.energy=110;light.data.size=1.75
# Dedicated camera for the new wall of student work.
data=bpy.data.cameras.new('08_iLab_Posters');cam=bpy.data.objects.new(data.name,data);c.objects.link(cam);cam.location=(-8.5,4.5,1.9);cam.rotation_euler=(Vector((-.15,5.0,2.4))-cam.location).to_track_quat('-Z','Y').to_euler();data.lens=32
s['cycles_studio_version']='v05';s['student_art']='Eight original Imagegen illustrations, fictional notices; decorative interpretations, not actual student submissions';s.camera=bpy.data.objects['02_Commons']
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Campus_Center_Cycles_Studio.blend'))
(R/'build_report.json').write_text(json.dumps({'added':made,'hidden':hidden,'artwork':art,'banner_dimensions':[1.75,5.25],'source_sha256':hashlib.sha256((R/'Source_Copy.blend').read_bytes()).hexdigest()},indent=2));print('BUILD_COMPLETE',len(art),len(made))
