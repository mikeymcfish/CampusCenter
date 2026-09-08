"""Original blank mannequin geometry and baked pose library. No external assets.
Local +Y is forward. Dimensions in metres, nominal standing height 1.70 m.
No facial, clothing or anatomical surface detail. Joint positions remain editable here.
"""
import bpy,bmesh,math
from mathutils import Vector,Matrix

POSES=['stand_relaxed','stand_weight_shift','talk_left','talk_both','listen','walk_left','walk_right','read','workbench','sit_relaxed','sit_talk','sit_work','sit_lounge']
def joints(pose):
 sit=pose.startswith('sit_');hz=.59 if sit else .89
 hip=Vector((.025 if pose=='stand_weight_shift' else 0,0,hz))
 lean=-.085 if pose=='sit_lounge' else .075 if pose in ['sit_work','workbench'] else 0
 shoulder=hip+Vector((0,lean,.42));head=hip+Vector((0,lean+.005,.67))
 j={'hip':hip,'shoulder':shoulder,'head':head}
 for sign,side in [(-1,'L'),(1,'R')]:
  j['hip'+side]=hip+Vector((sign*.10,0,-.015))
  j['knee'+side]=Vector((sign*.115,.36 if sit else 0,.49))
  j['ankle'+side]=Vector((sign*.115,.43 if sit else 0,.095))
  j['shoulder'+side]=shoulder+Vector((sign*.19,0,0))
  j['elbow'+side]=shoulder+Vector((sign*.23,.025,-.265))
  j['wrist'+side]=shoulder+Vector((sign*.235,.045,-.50))
  if sit:
   j['elbow'+side]=shoulder+Vector((sign*.24,.06,-.255))
   j['wrist'+side]=Vector((sign*.14,.30,.67))
  if pose in ['read','sit_work','workbench']:
   j['elbow'+side]=shoulder+Vector((sign*.23,.11,-.25))
   j['wrist'+side]=shoulder+Vector((sign*.105,.36,-.22 if pose!='sit_work' else -.245))
  if pose=='listen':
   j['elbow'+side]=shoulder+Vector((sign*.21,.05,-.26))
   j['wrist'+side]=shoulder+Vector((sign*.07,.19,-.40))
  if pose in ['talk_left','talk_both','sit_talk'] and (side=='L' or pose=='talk_both'):
   j['elbow'+side]=shoulder+Vector((sign*.24,.12,-.23))
   j['wrist'+side]=shoulder+Vector((sign*.17,.34,-.08 if side=='L' else -.20))
 if pose in ['walk_left','walk_right']:
  lead='L' if pose=='walk_left' else 'R'
  for sign,side in [(-1,'L'),(1,'R')]:
   f=1 if side==lead else -1
   j['knee'+side].y=.16*f;j['ankle'+side].y=.29*f
   if f<0:j['ankle'+side].z=.145
   j['elbow'+side].y=-.10*f;j['wrist'+side].y=-.20*f
 return j

def create_pose(pose,style,collection,material):
 j=joints(pose);bm=bmesh.new();nominal=1.71 if style=='male' else 1.63;scale=nominal/1.705
 def ell(c,r,rot=None):
  vs=bmesh.ops.create_uvsphere(bm,u_segments=16,v_segments=10,radius=1)['verts'];c=Vector(c)
  for v in vs:
   p=Vector((v.co.x*r[0],v.co.y*r[1],v.co.z*r[2]));v.co=(rot@p if rot else p)+c
 def limb(a,b,r1,r2):
  a=Vector(a);b=Vector(b);axis=b-a;rot=axis.to_track_quat('Z','Y').to_matrix();N=14;rings=[]
  for t,r in [(0,r1*.85),(.12,r1),(.48,(r1+r2)*.51),(.86,r2),(1,r2*.86)]:
   rings.append([bm.verts.new(a+axis*t+rot@Vector((r*math.cos(i*math.tau/N),r*math.sin(i*math.tau/N),0))) for i in range(N)])
  for ra,rb in zip(rings,rings[1:]):
   for i in range(N):bm.faces.new((ra[i],ra[(i+1)%N],rb[(i+1)%N],rb[i]))
  bm.faces.new(tuple(reversed(rings[0])));bm.faces.new(tuple(rings[-1]))
  ell(a,(r1*.90,)*3);ell(b,(r2*.92,)*3)
 hip=j['hip'];lean=j['shoulder'].y-hip.y
 # Continuous loft provides a quiet, mannequin-like trunk, with a blank pelvis.
 specs=[(-.10,.135,.100),(0,.155 if style=='male' else .162,.107),(.12,.135,.096),(.22,.139,.094),(.34,.177 if style=='male' else .159,.104),(.42,.177 if style=='male' else .157,.095),(.46,.080,.075)]
 rings=[];N=20
 for z,rx,ry in specs:
  rings.append([bm.verts.new(hip+Vector((rx*math.cos(i*math.tau/N),ry*math.sin(i*math.tau/N)+lean*max(z,0)/.42,z))) for i in range(N)])
 for a,b in zip(rings,rings[1:]):
  for i in range(N):bm.faces.new((a[i],a[(i+1)%N],b[(i+1)%N],b[i]))
 bm.faces.new(tuple(reversed(rings[0])));bm.faces.new(tuple(rings[-1]))
 limb(hip+Vector((0,lean,.44)),hip+Vector((0,lean,.55)),.054,.047)
 ell(j['head'],(.103,.100,.145))
 for sign,side in [(-1,'L'),(1,'R')]:
  shoulder=j['shoulder'+side].copy()
  if style=='female':shoulder.x*=.92
  limb(shoulder,j['elbow'+side],.063 if style=='male' else .058,.043)
  limb(j['elbow'+side],j['wrist'+side],.047,.030)
  direction=(j['wrist'+side]-j['elbow'+side]).normalized();hand=j['wrist'+side]+direction*.065
  ell(hand,(.038,.026,.077),direction.to_track_quat('Z','Y').to_matrix())
  limb(j['hip'+side],j['knee'+side],.087,.055)
  limb(j['knee'+side],j['ankle'+side],.057,.035)
  foot=j['ankle'+side]+Vector((0,.055,-.040));ell(foot,(.053,.125,.055))
 for v in bm.verts:v.co*=scale
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 me=bpy.data.meshes.new('Mannequin_'+style+'_'+pose);bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(me.name,me);collection.objects.link(ob);me.materials.append(material)
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 # Bake a lightly fused surface, simplify and smooth once. No live modifiers remain.
 ob.data.remesh_voxel_size=.018*scale;bpy.ops.object.voxel_remesh()
 mod=ob.modifiers.new('Baked smooth','SMOOTH');mod.factor=1.0;mod.iterations=3;bpy.ops.object.modifier_apply(modifier=mod.name)
 mod=ob.modifiers.new('Baked low resolution','DECIMATE');mod.ratio=.30;bpy.ops.object.modifier_apply(modifier=mod.name)
 for p in ob.data.polygons:p.use_smooth=True
 ob.data.name='Baked_'+style+'_'+pose
 ob['base_style']=style;ob['pose']=pose;ob['standing_height_m']=nominal;ob['geometry']='Original blank mannequin, baked pose, no rig or modifiers'
 # Remesh smoothing can lift feet slightly; keep the grounded ankle's sole exactly at local z0.
 if not pose.startswith('sit_'):
  z=min(v.co.z for v in ob.data.vertices)
  for v in ob.data.vertices:v.co.z-=z
 return ob,{k:list(v*scale) for k,v in j.items()}
