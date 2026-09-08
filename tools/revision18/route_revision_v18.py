from pathlib import Path
import bpy,json,math
from mathutils import Vector,Matrix
R=Path(__file__).parent;O=R/'output_v18';bpy.ops.wm.open_mainfile(filepath=str(O/'Campus_Center_Textured.blend'));s=bpy.context.scene
old=json.loads((R/'output_v14/walkthrough_route.json').read_text())['keys'];F=4.2672;E=1.65
# Route extensions through the actual door openings.
def K(x,y,z=E,label='walk',look=None,speed=.85,hold=0):return dict(p=[x,y,z],label=label,look=look,speed=speed,hold=hold)
ground=[K(-28.3,25),K(-28.3,28.7,label='Locker room approach'),K(-29.8,28.7),K(-30.6,28.7,speed=.55),K(-30.6,28.05),K(-31.3,28.05),K(-35,28.05,label='Student lockers',look=[-35,25,1.1],speed=.65),K(-39.0,28.05,label='Locker room overview',look=[-42,26,1.2],speed=.6),K(-38.9,27.8),K(-38.9,25.6,label='Locker aisle',look=[-38.9,23.1,1.3],hold=3),K(-38.9,28.05),K(-35,28.05),K(-31.3,28.05),K(-30.6,28.05),K(-30.6,28.7),K(-29.8,28.7),K(-28.3,28.7),K(-28.3,16),K(-28.3,15.4),K(-28.8,15.4),K(-29.2,14.75),K(-30.8,14.75),K(-32,14.95),K(-39.2,14.95,label='Student bathroom approach'),K(-39.2,13.1,speed=.5),K(-39.2,11.8,label='Student bathroom',look=[-37.4,9.3,1.2],speed=.5,hold=4),K(-39.2,13.1),K(-39.2,14.95),K(-32,14.95),K(-28.3,14.95)]
upper=[K(-27.7,17.8,F+E),K(-27.7,19.6,F+E,label='Fitness entry',speed=.6),K(-27.7,20.3,F+E),K(-30.9,20.3,F+E),K(-30.9,24.5,F+E),K(-34,25,F+E,label='Fitness room',look=[-39,28,5.3],speed=.65),K(-38.8,25,F+E,label='Cardio equipment',look=[-41,28,5.3],speed=.6),K(-39.75,20,F+E),K(-39.75,18,F+E),K(-39.75,14.95,F+E),K(-30,14.95,F+E)]
route=old[:23]+ground+old[23:35]+upper+old[35:]
for d in json.loads((R/'output_3d_v4/door_schedule.json').read_text()):
 if d['id'] not in ['Locker122_east_door0','Restrooms_north_door0','Fitness_south_door1','Fitness_south_door3','Corridor_stair_boundary_door0']:continue
 for leaf in d['leaf_geometry']:
  ob=bpy.data.objects.get(leaf['name']) or bpy.data.objects.get(leaf['name']+'_bottom');center=sum((ob.matrix_world@v.co for v in ob.data.vertices),Vector())/len(ob.data.vertices);cur=math.atan2(center.y-leaf['hinge'][1]/1000,center.x-leaf['hinge'][0]/1000);target=0 if ('Locker' in d['id'] or 'Corridor_stair' in d['id']) else math.pi/2
  hinge=Vector((*leaf['hinge'],leaf['base_mm']))/1000;T=Matrix.Translation(hinge)@Matrix.Rotation(target-cur,4,'Z')@Matrix.Translation(-hinge)
  for ob in s.objects:
   if ob.name.startswith(leaf['name']):ob.matrix_world=T@ob.matrix_world
# Use existing proven Hermite/arc-length sampler, then smooth view direction.
sc=s
samples=[];elapsed=0
for i in range(len(route)-1):
 for _ in range(round(route[i].get('hold',0)*24)):samples.append(dict(p=route[i]['p'],segment=i,label=route[i]['label'],hold=True))
 p0=Vector(route[max(0,i-1)]['p']);p1=Vector(route[i]['p']);p2=Vector(route[i+1]['p']);p3=Vector(route[min(len(route)-1,i+2)]['p'])
 # Tamed Hermite tangents avoid excessive corner overshoot.
 delta=(p2-p1).length;m1=(p2-p0).normalized()*min(delta,(p2-p0).length*.30);m2=(p3-p1).normalized()*min(delta,(p3-p1).length*.30)
 dense=[]
 for j in range(101):
  t=j/100;dense.append((2*t**3-3*t*t+1)*p1+(t**3-2*t*t+t)*m1+(-2*t**3+3*t*t)*p2+(t**3-t*t)*m2)
 length=sum((b-a).length for a,b in zip(dense,dense[1:]));duration=length/min(route[i]['speed'],route[i+1]['speed']);n=max(2,round(duration*24));cum=[0.]
 for a,b in zip(dense,dense[1:]):cum.append(cum[-1]+(b-a).length)
 k=0
 for j in range(n):
  target=length*j/n
  while k<99 and cum[k+1]<target:k+=1
  t=(target-cum[k])/max(1e-8,cum[k+1]-cum[k]);pos=dense[k].lerp(dense[k+1],t)
  samples.append(dict(p=list(pos),segment=i,label=route[i]['label']))
 elapsed+=duration
samples.append(dict(p=route[-1]['p'],segment=len(route)-1,label=route[-1]['label']))
cam=sc.camera;cam.animation_data_clear();cam.rotation_mode='QUATERNION';cam.data.lens=22;cam.data.clip_start=.05;cam.data.dof.use_dof=False
previous=None
for i,s in enumerate(samples):
 p=Vector(s['p']);ahead=Vector(samples[min(len(samples)-1,i+36)]['p']);direction=ahead-p
 if direction.length<.01:direction=Vector((0,1,0))
 direction.normalize();ri=s['segment'];look=route[ri].get('look')
 if look:
  v=(Vector(look)-p).normalized();direction=direction.lerp(v,1.0 if s.get('hold') else .45).normalized()
 # Smooth look-ahead orientation so interest points do not snap at segment boundaries.
 q=direction.to_track_quat('-Z','Y')
 if previous:q=previous.slerp(q,.065)
 if previous and previous.dot(q)<0:q.negate()
 previous=q;cam.location=p;cam.rotation_quaternion=q;cam.keyframe_insert('location',frame=i+1);cam.keyframe_insert('rotation_quaternion',frame=i+1)
sc.frame_start=1;sc.frame_end=len(samples);sc.render.fps=24;sc.frame_set(1)

sc['route']='Entrance, commons, iLab, locker 122, student bathroom 117, Stair B, fitness 218, upper corridor, bridge, balcony'
(O/'walkthrough_route.json').write_text(json.dumps(dict(fps=24,frames=len(samples),duration_seconds=len(samples)/24,keys=route,samples=samples),indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Campus_Center_Textured.blend'))
print('ROUTE_SAVED',len(samples),flush=True)
