"""Actual Blender camera-depth animation with isolated proxy people for motion control."""
from pathlib import Path
R=Path(__file__).parent
code=(R/'render_depth.py').read_text().split('report=[]')[0]
exec(compile(code,str(R/'render_depth.py'),'exec'))
import math
r=next(x for x in json.loads((P/'rooms/room_contract.json').read_text()) if x['number']=='108')
cx,cy=r['center_world_m'];span=r['ortho_span_m'];o.location=(cx,cy,3.5);o.rotation_euler=(0,0,0);d.ortho_scale=span
s.render.resolution_x=s.render.resolution_y=512
people=[]
# Positions measured from the ImageGen pilot; only image-plane x/y guides,
# all depth itself is rendered from actual Blender mesh geometry.
for index,(px,py) in enumerate([(550,550),(220,885),(315,375),(1000,205),(1060,278),(1070,515),(1070,670),(1070,870)]):
    parent=bpy.data.objects.new(f'R12 depth person {index}',None);s.collection.objects.link(parent)
    parent.location=(cx+(px/1280-.5)*span,cy+(.5-py/1280)*span,0)
    parts=[]
    for label,xyz,scale in [('head',(0,0,1.6),(.11,.11,.13)),('torso',(0,0,1.17),(.21,.13,.32)),('legL',(-.1,0,.45),(.08,.085,.43)),('legR',(.1,0,.45),(.08,.085,.43)),('armL',(-.26,0,1.05),(.06,.065,.28)),('armR',(.26,0,1.05),(.06,.065,.28))]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,location=xyz)
        part=bpy.context.object;part.name=f'R12 guide {index} {label}';part.scale=scale;part.parent=parent;parts.append(part)
    people.append((parent,parent.location.copy(),parts))
dest=R/'depth/108/moving';dest.mkdir(parents=True,exist_ok=True)
frames=[]
for frame in range(105):
    phase=2*math.pi*frame/104
    for index,(parent,base,parts) in enumerate(people):
        if index<2:
            # Closed narrow loops confined to the original clear aisles.
            parent.location=base+Vector((.18*math.sin(phase),.45*(1-math.cos(phase)),0))
            parent.rotation_euler.z=math.atan2(.18*math.cos(phase),.45*math.sin(phase))
            for j in [2,3,4,5]:parts[j].rotation_euler.x=.32*math.sin(phase*4+(j%2)*math.pi)
    s.render.filepath=str(dest/'current.exr');bpy.ops.render.render(write_still=True)
    im=bpy.data.images.load(s.render.filepath,check_existing=False);a=np.asarray(im.pixels[:],dtype=np.float32).reshape(512,512,4)[::-1,:,0].copy();bpy.data.images.remove(im);frames.append(a)
    if frame%10==0:print('MOVING_DEPTH_FRAME',frame,flush=True)
np.save(R/'depth/108/moving_depth_metres.npy',np.stack(frames))
(dest/'render_contract.json').write_text(json.dumps({'frames':105,'fps':24,'camera_position':list(o.location),'orthographic_scale':span,'resolution':[512,512],'near_m':0,'far_m':4.5,'people':'8 proxy bodies, two moving on closed paths; geometry-only guidance','source':'Blender mesh camera-depth renders','source_unchanged':hashlib.sha256((P/'Source_Studio.blend').read_bytes()).hexdigest()==inventory['source_sha256']},indent=2))
