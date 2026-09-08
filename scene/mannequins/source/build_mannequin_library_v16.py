from pathlib import Path
import bpy,json,sys
from mathutils import Vector
R=Path(__file__).parent;sys.path.insert(0,str(R));from mannequin_library_v16 import create_pose,POSES
O=R/'output_v16';O.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;c=bpy.data.collections.new('BAKED MANNEQUIN POSE LIBRARY');s.collection.children.link(c)
m=bpy.data.materials.new('Untextured mannequin clay');m.use_nodes=True;m.diffuse_color=(.63,.66,.64,1);m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=m.diffuse_color
records=[]
for style in ['male','female']:
 for pose in POSES:
  ob,j=create_pose(pose,style,c,m);ob.location=(len(records)%7*1.2,len(records)//7*2.3,0);records.append({'name':ob.name,'style':style,'pose':pose,'vertices':len(ob.data.vertices),'faces':len(ob.data.polygons),'joints':j});print('POSE_BAKED',style,pose,len(ob.data.vertices),flush=True)
s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Mannequin_Pose_Library.blend'))
(O/'pose_library.json').write_text(json.dumps({'source':'Original procedural blank mannequins authored for this project; no external asset dependencies','poses':records},indent=2))
# Studio proof sheet: plain lighting, labelled in accompanying JSON; no source-scene edits.
bpy.ops.mesh.primitive_plane_add(size=200);floor=bpy.context.object;floor.location.z=-.025
fm=bpy.data.materials.new('Studio floor');fm.diffuse_color=(.20,.23,.25,1);floor.data.materials.append(fm)
bpy.ops.object.camera_add(location=(9,-13,11));cam=bpy.context.object;cam.rotation_euler=(Vector((3.6,3.5,.7))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=12;s.camera=cam
for loc,power,size in [((2,-4,10),2500,8),((7,7,8),1800,6)]:
 bpy.ops.object.light_add(type='AREA',location=loc);bpy.context.object.data.energy=power;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=size
s.world=bpy.data.worlds.new('Studio world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.25,.25,.25,1)
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.filepath=str(O/'pose_library_preview.png');bpy.ops.render.render(write_still=True)
print('LIBRARY_READY',flush=True)
