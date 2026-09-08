"""Reference-informed detail pass; preserves all v02 objects and route."""
import bpy,bmesh,math,random,json,pathlib,hashlib
from mathutils import Vector,Matrix
R=pathlib.Path(__file__).parent;s=bpy.context.scene;s.frame_set(1)
random.seed(1309);made=[];hidden=[];cols={}
for n in ['Graphics and art','Planting','Refined commons furniture','Refined iLab equipment']:
 c=bpy.data.collections.new('V03 '+n);s.collection.children.link(c);cols[n]=c
category='Graphics and art';T=Matrix.Identity(4)
def color(h):
 v=[int(h[i:i+2],16)/255 for i in (0,2,4)];return tuple(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in v)+(1,)
def mat(n,h,rough=.5,metal=0):
 m=bpy.data.materials.new('V03 '+n);m.diffuse_color=color(h);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=color(h);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal;return m
navy=mat('King navy','082E50',.85);gold=mat('Champagne bronze','B69A62',.35,.5);ivory=mat('Warm paper','F0ECE0',.82)
black=mat('Graphite powdercoat','252B2D',.43,.25);silver=mat('Machine silver','A9AEAF',.34,.75);orange=mat('BigRep orange','EC511F',.36)
white=mat('Equipment pearl','DFE2DE',.36);rubber=mat('Rubber feet','171B1C',.9);soil=mat('Potting soil','282018',1)
terracotta=mat('Stoneware planters','8B7560',.86);bark=mat('Ficus bark','69503A',.9)
leaves=[mat('Leaf '+str(i),h,.42) for i,h in enumerate(['244C24','376A2E','527B35','426D29','668D40'])]
for m in leaves:
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Subsurface Weight'].default_value=.08;bs.inputs['Roughness'].default_value=.45
glass=bpy.data.materials['Clear architectural glazing'];oak=bpy.data.materials['Natural oak'];steel=bpy.data.materials['Brushed stainless hardware'];top=bpy.data.materials['V8 plain light table surface']
fabrics=[]
for name,hex in [('Sage','677966'),('Ochre','A38151'),('Slate','4F6A7D')]:
 m=bpy.data.materials['V8 plain sage upholstery'].copy();m.name='V03 '+name+' woven upholstery'
 for n in m.node_tree.nodes:
  if n.type=='VALTORGB':
   c=color(hex);n.color_ramp.elements[0].color=tuple(v*.82 for v in c[:3])+(1,);n.color_ramp.elements[1].color=c
 fabrics.append(m)
def mesh(n,vs,fs,m,smooth=False):
 me=bpy.data.meshes.new('V03 '+n);me.from_pydata(vs,[],fs);me.update();me.transform(T)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 o=bpy.data.objects.new('V03 '+n,me);cols[category].objects.link(o);me.materials.append(m);made.append(o.name)
 for f in me.polygons:f.use_smooth=smooth
 return o
def box(n,c,d,m,bevel=.008):
 vs=[(c[0]+a*d[0]/2,c[1]+b*d[1]/2,c[2]+k*d[2]/2) for k in [-1,1] for b in [-1,1] for a in [-1,1]]
 o=mesh(n,vs,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],m)
 if bevel:
  mod=o.modifiers.new('Rounded manufactured edges','BEVEL');mod.width=min(bevel,min(d)*.40);mod.segments=4
  mod=o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL');mod.keep_sharp=True
 return o
def rod(n,a,b,r,m,sides=20,r2=None):
 a=Vector(a);b=Vector(b);u=(b-a).normalized();v=u.cross(Vector((0,0,1)) if abs(u.z)<.95 else Vector((1,0,0))).normalized();w=u.cross(v)
 vs=[cen+radius*(v*math.cos(i*math.tau/sides)+w*math.sin(i*math.tau/sides)) for cen,radius in [(a,r),(b,r if r2 is None else r2)] for i in range(sides)]
 return mesh(n,vs,[tuple(reversed(range(sides))),tuple(range(sides,2*sides))]+[(i,(i+1)%sides,(i+1)%sides+sides,i+sides) for i in range(sides)],m,True)
def hide(n):
 o=bpy.data.objects.get(n)
 if o:o.hide_render=True;o.hide_viewport=True;hidden.append(n)
def bounds(o):
 pts=[o.matrix_world@Vector(v) for v in o.bound_box];return Vector([min(v[i] for v in pts) for i in range(3)]),Vector([max(v[i] for v in pts) for i in range(3)])
def image_mat(n,path):
 m=mat(n,'FFFFFF',.82);nt=m.node_tree;b=nt.nodes.get('Principled BSDF');im=nt.nodes.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(path));im.image.pack();nt.links.new(im.outputs['Color'],b.inputs['Base Color']);return m
def panel(n,c,u,v,w,h,m):
 c=Vector(c);u=Vector(u);v=Vector(v);o=mesh(n,[c-u*w/2-v*h/2,c+u*w/2-v*h/2,c+u*w/2+v*h/2,c-u*w/2+v*h/2],[(0,1,2,3)],m)
 uv=o.data.uv_layers.new(name='UVMap')
 for i,p in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[i].uv=p
 return o
def text(n,body,p,size,m,normal=(0,-1,0)):
 data=bpy.data.curves.new('V03 '+n,'FONT');data.body=body;data.align_x='CENTER';data.size=size;data.extrude=.0005
 o=bpy.data.objects.new('V03 '+n,data);cols[category].objects.link(o);o.location=T@Vector(p);o.rotation_euler=(T.to_3x3()@Vector(normal)).to_track_quat('Z','Y').to_euler();data.materials.append(m);made.append(o.name);return o
# Match the hanging banner locations already in the scene.
banner=image_mat('King banner textile',R/'assets/King_banner.png')
for y in [20,25,29]:
 hide('V5_Banner_'+str(y));panel('King banner '+str(y),(.241,y,5.5),(0,1,0),(0,0,1),.70,2.10,banner)
 rod('Banner top rail '+str(y),(.24,y-.39,6.56),(.24,y+.39,6.56),.012,steel)
 rod('Banner bottom weight '+str(y),(.24,y-.35,4.445),(.24,y+.35,4.445),.009,steel)
# Six original geometric studies occupy existing art placeholders. No claim of actual student authorship.
artcols=[mat('Art '+str(i),h,.93) for i,h in enumerate(['B97746','567484','C7AE79','445C4C','D6CDBB','293D51'])]
for idx,x in enumerate([-21,-18,-15,-12,-9,-6]):
 hide('V5_Art_placeholder_'+str(x));box('Gallery frame '+str(idx),(x,16.085,5.9),(1.11,.06,.72),black,.009)
 panel('Gallery mat '+str(idx),(x,16.051,5.9),(1,0,0),(0,0,1),1.065,.675,ivory)
 # Cut-paper geometric composition with canvas margins.
 for j in range(5):
  xx=x-.42+j*.17;h=.23+.19*math.sin(idx+j*1.3)**2
  panel('Art shape '+str(idx)+' '+str(j),(xx,16.049-j*.0001,5.80+h/2),(1,0,0),(0,0,1),.155,h,artcols[(idx+j)%len(artcols)])
 text('Gallery caption '+str(idx),'STUDIES / '+str(idx+1).zfill(2),(x,16.043,5.65),.018,navy)
# Refine the six plan-based lounge clusters at exactly their previous seat centers.
category='Refined commons furniture'
def cp(x,y):return ((x-45)*.0281,(1156-y)*.0281)
def chair(n,x,y,a,m):
 global T
 T=Matrix.Translation((x,y,0))@Matrix.Rotation(a,4,'Z')
 box(n+' seat',(0,0,.43),(.65,.64,.17),m,.065)
 box(n+' underframe',(0,0,.315),(.56,.56,.065),black,.018)
 box(n+' back',(0,.295,.70),(.69,.17,.58),m,.065)
 for side in [-1,1]:
  box(n+' arm '+str(side),(side*.335,0,.595),(.105,.66,.265),m,.045)
  for yy in [-.22,.22]:rod(n+' tapered leg',(side*.25,yy,0),(side*.24,yy,.33),.017,black,r2=.023)
 # Thin welt around cushion perimeter, matching the fabric rather than contrasting trim.
 for yy in [-.294,.294]:rod(n+' welt',( -.29,yy,.47),(.29,yy,.47),.0023,m,10)
 for xx in [-.29,.29]:rod(n+' welt',(xx,-.294,.47),(xx,.294,.47),.0023,m,10)
 T=Matrix.Identity(4)
for i,(xx,yy,angles) in enumerate([(395,204,[90,195,280]),(373,337,[80,200,340]),(151,360,[45,145,265]),(52,397,[35,290]),(415,469,[85,190,280]),(249,348,[30,285])]):
 old_group=bpy.data.objects['V15_Commons_lounge_cluster_'+str(i)];offset=old_group.matrix_world.translation.copy()
 hide(old_group.name);x,y=cp(xx,yy);x+=offset.x;y+=offset.y
 rod('Cluster '+str(i)+' table',(x,y,.445),(x,y,.48),.43,top,48);rod('Cluster table stem',(x,y,.04),(x,y,.445),.04,black);rod('Cluster table foot',(x,y,0),(x,y,.04),.25,black,40)
 for k,deg in enumerate(angles):
  a=math.radians(deg);chair('Lounge '+str(i)+' '+str(k),x+.92*math.cos(a),y+.92*math.sin(a),a-math.pi/2,fabrics[1 if i in [1,4] else 2 if i==3 else 0])
# Plant geometry: tapered woody stems and curved, pointed leaf blades with central folds.
category='Planting'
def leaf_mesh(n,base,angle,length,width,rise,m):
 u=Vector((math.cos(angle),math.sin(angle),rise));v=Vector((-math.sin(angle),math.cos(angle),0));base=Vector(base);vs=[]
 for k in range(9):
  t=k/8;center=base+u*(length*t)+Vector((0,0,.10*length*math.sin(math.pi*t)));w=width*math.sin(math.pi*t)**.75
  vs.extend([center-v*w+Vector((0,0,-w*.16)),center+Vector((0,0,w*.10)),center+v*w+Vector((0,0,-w*.16))])
 fs=[]
 for k in range(8):
  for j in range(2):fs.append((3*k+j,3*(k+1)+j,3*(k+1)+j+1,3*k+j+1))
 return mesh(n,vs,fs,m,True)
def plant(n,x,y,z,height=2.0,pot=True):
 if pot:
  # Open pot wall with soil covering the center.
  N=48;vs=[]
  for r,zz in [(.22,z),(.30,z+.52),(.277,z+.52),(.20,z+.04)]:
   vs.extend([(x+r*math.cos(i*math.tau/N),y+r*math.sin(i*math.tau/N),zz) for i in range(N)])
  fs=[(k*N+i,k*N+(i+1)%N,((k+1)%4)*N+(i+1)%N,((k+1)%4)*N+i) for k in range(4) for i in range(N)];mesh(n+' pot',vs,fs,terracotta,True)
  rod(n+' soil',(x,y,z+.465),(x,y,z+.475),.275,soil,40);z+=.48
 rod(n+' trunk',(x,y,z),(x+.05,y+.02,z+height*.74),.026,bark,r2=.009)
 for branch in range(13):
  a=branch*2.4;root=Vector((x+.02,y,z+height*(.28+branch*.045)));tip=root+Vector((math.cos(a)*.45,math.sin(a)*.45,height*.20))
  rod(n+' branch',root,tip,.009,bark,10,r2=.003)
  for k in range(9):
   t=.15+k*.085;pos=root.lerp(tip,t);aa=a+(-1 if k%2 else 1)*random.uniform(.6,1.7)
   leaf_mesh(n+' leaf',pos,aa,random.uniform(.17,.30),random.uniform(.045,.085),random.uniform(.1,.7),random.choice(leaves))
for i,(x,y) in enumerate([(15.40,29.70),(1.25,28.85)]):plant('Commons ficus '+str(i),x,y,0,1.75,True)
for y in [7,18]:
 plant('Entry tree '+str(y),21,y,.70,2.25,False)
 for i in range(24):
  x=21+random.uniform(-.48,.48);yy=y+random.uniform(-1.28,1.28)
  for j in range(7):leaf_mesh('Entry underplant', (x,yy,.70),random.random()*math.tau,random.uniform(.23,.48),.015,random.uniform(.6,1.9),random.choice(leaves))
for y in [8,18,25]:
 for i in range(20):
  x=15.7+random.uniform(-.22,.22);yy=y+random.uniform(-.48,.48)
  for j in range(6):leaf_mesh('Terrace grasses',(x,yy,4.835),random.random()*math.tau,random.uniform(.22,.46),.012,random.uniform(.7,1.9),random.choice(leaves))
# Rebuild only the most conspicuous reconstructed machines. Existing source meshes stay hidden.
category='Refined iLab equipment'
def machine_transform(old):
 global T
 lo,hi=bounds(bpy.data.objects[old]);c=(lo+hi)/2
 T=Matrix.Translation((c.x,c.y,max(lo.z,0)))
 return lo,hi
for old,ams in [('V9_Lab_bambu_h2d_1','V9_Lab_ams2pro_2'),('V9_Lab_bambu_h2d_3','V9_Lab_ams2pro_4')]:
 lo,hi=machine_transform(old);hide(old);hide(ams);n=old.replace('V9_Lab_','')
 # Existing 0.51 x 0.50 m planning envelope; front faces the north aisle.
 w=.505;d=.49;h=.632
 for xx in [-w/2+.021,w/2-.021]:box(n+' side',(xx,0,h/2),(.042,d,h),silver,.016)
 box(n+' back',(0,-d/2+.015,h/2),(w-.06,.03,h),black,.008)
 for z in [.018,h-.025]:box(n+' frame',(0,0,z),(w,d,.036),black,.012)
 box(n+' top fascia',(0,d/2-.018,h-.058),(w-.065,.035,.095),black,.01)
 box(n+' glass door',(0,d/2-.009,.276),(w-.07,.007,.48),glass,.002)
 rod(n+' handle',(-.19,d/2+.004,.20),(-.19,d/2+.004,.32),.008,black)
 box(n+' bed',(0,0,.13),(.35,.35,.013),black,.005)
 for xx in [-.17,.17]:rod(n+' Z screw',(xx,-.10,.08),(xx,-.10,.55),.006,steel)
 for zz in [.44,.47]:rod(n+' gantry',(-.20,0,zz),(.20,0,zz),.005,steel)
 box(n+' dual head',(0,0,.425),(.077,.06,.073),black,.007)
 for xx in [-.018,.018]:rod(n+' nozzle',(xx,.012,.386),(xx,.012,.365),.005,gold)
 box(n+' touchscreen',(.145,.257,.583),(.13,.014,.083),black,.006)
 panel(n+' UI',(.145,.265,.583),(-1,0,0),(0,0,1),.108,.061,navy)
 for yy in [.57,.585,.60]:panel(n+' UI readout',(.13,.2655,yy),(-1,0,0),(0,0,1),.040,.0025,ivory)
 text(n+' model','H2D',(-.13,.265,.59),.022,ivory,(0,1,0))
 box(n+' AMS base',(0,0,h+.048),(.44,.34,.075),black,.017)
 # Four separate filament spools beneath a transparent arched cover.
 spoolmats=[ivory,navy,leaves[2],orange]
 for j in range(4):
  xx=-.156+j*.104
  rod(n+' filament',(xx-.037,0,h+.145),(xx+.037,0,h+.145),.09,spoolmats[j],32)
  for sx in [-.040,.040]:rod(n+' spool flange',(xx+sx-.003,0,h+.145),(xx+sx+.003,0,h+.145),.097,black,32)
 # Clear lid follows a semicylindrical roof along the spool axes.
 vs=[]
 for xx in [-.22,.22]:
  for i in range(25):
   a=i*math.pi/24;vs.append((xx,.16*math.cos(a),h+.09+.16*math.sin(a)))
 mesh(n+' AMS clear lid',vs,[(i,i+1,i+26,i+25) for i in range(24)],glass,True)
 text(n+' AMS label','AMS 2 PRO',(0,.174,h+.052),.018,ivory,(0,1,0))
 T=Matrix.Identity(4)
# BigRep ONE: clean open frame, gantry, build bed and orange corner panels from supplied photo.
lo,hi=machine_transform('V9_Lab_bigrep_7');hide('V9_Lab_bigrep_7')
w=hi.x-lo.x;d=hi.y-lo.y;h=hi.z-max(0,lo.z)
for x in [-w/2+.09,w/2-.09]:
 for y in [-d/2+.09,d/2-.09]:
  box('BigRep upright',(x,y,h/2),(.10,.10,h-.04),silver,.008)
  rod('BigRep leveling foot',(x,y,0),(x,y,.055),.063,rubber)
  for z in [.18,h-.18]:box('BigRep orange corner',(x,y,z),(.23,.19,.29),orange,.01)
for y in [-d/2+.09,d/2-.09]:
 for z in [.12,h-.09]:box('BigRep cross beam',(0,y,z),(w-.1,.1,.10),silver,.006)
for x in [-w/2+.09,w/2-.09]:
 for z in [.12,h-.09]:box('BigRep side beam',(x,0,z),(.10,d-.1,.10),silver,.006)
box('BigRep build bed',(0,0,.35),(w-.4,d-.4,.075),black,.012)
for x in [-w/2+.19,w/2-.19]:rod('BigRep vertical guide',(x,0,.25),(x,0,h-.18),.018,steel)
for y in [-.15,-.08]:rod('BigRep X gantry',(-w/2+.15,y,h-.35),(w/2-.15,y,h-.35),.016,steel)
box('BigRep print carriage',(.25,-.12,h-.42),(.19,.19,.20),black,.016)
rod('BigRep nozzle',(.25,-.12,h-.52),(.25,-.12,h-.57),.016,gold)
box('BigRep control housing',(w/2-.22,d/2-.04,h-.21),(.30,.09,.29),orange,.018)
panel('BigRep touchscreen',(w/2-.22,d/2+.007,h-.20),(-1,0,0),(0,0,1),.21,.16,navy)
text('BigRep label','BigRep ONE',(-.30,d/2-.04,h-.085),.055,black,(0,1,0))
T=Matrix.Identity(4)
# Two foreground print appliances retain the old envelopes and table contacts.
for old,kind in [('V9_Lab_epson_6','Epson'),('V9_Lab_uvflatbed_5','UV flatbed')]:
 lo,hi=machine_transform(old);hide(old);w=hi.x-lo.x;d=hi.y-lo.y;h=hi.z-lo.z
 box(kind+' lower plinth',(0,0,.06),(w-.05,d-.05,.12),black,.018)
 # Recessed loading opening instead of an undifferentiated solid white block.
 for xx in [-w*.40,w*.40]:box(kind+' side cabinet',(xx,-d*.10,h*.48),(w*.20,d*.70,h*.74),silver if kind=='Epson' else white,.028)
 box(kind+' rear',(0,-d*.36,h*.47),(w*.82,d*.20,h*.76),black,.02)
 box(kind+' upper cover',(0,-d*.13,h*.86),(w-.03,d*.65,h*.22),black,.045)
 box(kind+' brand rail',(0,d*.205,h*.68),(w-.08,.025,.027),navy,.004)
 box(kind+' loading slide',(0,d*.17,.16),(w*.47,d*.58,.045),black,.012)
 box(kind+' platen',(0,d*.18,.205),(w*.40,d*.47,.025),silver,.006)
 box(kind+' control housing',(0,d*.20,h*.91),(.20,.065,.085),black,.016)
 panel(kind+' LCD',(0,d*.235,h*.92),(-1,0,0),(0,0,1),.095,.045,navy)
 for xx in [.068,.084]:rod(kind+' control button',(xx,d*.234,h*.92),(xx,d*.24,h*.92),.007,ivory,16)
 text(kind+' label','EPSON' if kind=='Epson' else 'UV FLATBED',(-w*.30,d*.22,h*.78),.035,ivory,(0,1,0))
 if kind=='UV flatbed':
  for j in range(4):
   xx=-w*.34+j*.095;rod('UV ink bottle',(xx,-d*.13,h),(xx,-d*.13,h+.09),.034,black,20)
   rod('UV ink label',(xx,-d*.13,h+.025),(xx,-d*.13,h+.063),.0345,ivory,20)
 T=Matrix.Identity(4)
# Give retained manufacturer CAD its distinctive resin hoods without remeshing it.
resin=mat('Amber resin hood','D97220',.23)
bs=resin.node_tree.nodes.get('Principled BSDF');bs.inputs['Transmission Weight'].default_value=.35;bs.inputs['IOR'].default_value=1.48
for o in list(s.objects):
 if o.type!='MESH' or not o.name.startswith('V9_Lab_Formlabs_'):continue
 o.data=o.data.copy();o.data.materials.clear();o.data.materials.append(black);o.data.materials.append(resin)
 lo,hi=bounds(o)
 for f in o.data.polygons:
  p=o.matrix_world@f.center;f.material_index=int(p.z>lo.z+(hi.z-lo.z)*.30 and 'wash' not in o.name)
# Project physically scaled UVs on the new furniture so copied wood and fabric maps are valid.
for name in made:
 o=bpy.data.objects[name]
 if o.type!='MESH':continue
 uv=o.data.uv_layers.get('Cycles_PBR') or o.data.uv_layers.new(name='Cycles_PBR')
 for f in o.data.polygons:
  axis=max(range(3),key=lambda i:abs(f.normal[i]));axes=(0,1) if axis==2 else (0,2) if axis==1 else (1,2)
  for li in f.loop_indices:
   p=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]],p[axes[1]])
# Additional review cameras for details that are not visible from the original three views.
for name,p,target,lens in [('04_Gallery',(-22,14.4,5.9),(-6,16.02,5.9),26),('05_Printer_Detail',(-7.8,9.35,1.85),(-7.8,7.13,1.43),38),('06_Entrance_Planting',(28,6,1.8),(16,12,1.6),26)]:
 data=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,data);cols['Graphics and art'].objects.link(o);o.location=p;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();data.lens=lens;data.dof.use_dof=True;data.dof.aperture_fstop=8;data.dof.focus_distance=(Vector(target)-o.location).length;made.append(name)
s.camera=bpy.data.objects['02_Commons'];s['cycles_studio_version']='v03';s['detail_pass']='Reference-informed graphics, original geometric artwork, planting, upholstered furniture and clean printer representations. Not manufacturer CAD.'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Campus_Center_Cycles_Studio.blend'))
report={'created':made,'hidden_originals':hidden,'collections':list(cols),'original_meshes_retained':3422,'created_count':len(made),'source_sha256':hashlib.sha256((R/'Source_Copy.blend').read_bytes()).hexdigest(),'machine_basis':'Reference-informed clean geometry within existing planning envelopes; not manufacturer CAD','art_basis':'Original geometric studies; decorative interpretation, not actual student artwork'}
(R/'build_report.json').write_text(json.dumps(report,indent=2));print('DETAILS_BUILD_COMPLETE',len(made),len(hidden),flush=True)
