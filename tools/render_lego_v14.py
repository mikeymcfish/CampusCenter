from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'lego';d=json.loads((O/'lego_model.json').read_text());bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene
colors={'Black':(.04,.04,.045),'White':(.9,.9,.88),'Tan':(.60,.43,.24),'Light bluish gray':(.5,.53,.55),'Dark bluish gray':(.2,.22,.24)}
meshes={}
for color in colors:
 m=bpy.data.materials.new(color);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*colors[color],1);m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.32;meshes[color]=[bmesh.new(),m]
for p in d['placements']:
 bm,ma=meshes[p['color']];base=p['layer']==0;h=1.6 if base else 9.6;z=-1.6 if base else(p['layer']-1)*9.6
 vs=bmesh.ops.create_cube(bm,size=1)['verts']
 for v in vs:v.co=Vector(((p['x']+(p['w']-1)/2)*8+v.co.x*(p['w']*8-.18),(p['y']+(p['d']-1)/2)*8+v.co.y*(p['d']*8-.18),z+h/2+v.co.z*h))
 # Actual studs make the building instructions preview readable.
 for x in range(p['x'],p['x']+p['w']):
  for y in range(p['y'],p['y']+p['d']):
   vs=bmesh.ops.create_cone(bm,cap_ends=True,cap_tris=False,segments=8,radius1=2.4,radius2=2.4,depth=1.8)['verts']
   for v in vs:v.co+=Vector((x*8,y*8,z+h+.9))
for col,(bm,ma) in meshes.items():
 me=bpy.data.meshes.new(col);bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(col,me);sc.collection.objects.link(ob);me.materials.append(ma)
sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=.001;sc.render.engine='CYCLES';sc.cycles.samples=20;sc.cycles.use_denoising=True;sc.render.resolution_x=1500;sc.render.resolution_y=1000;sc.render.resolution_percentage=100
sc.world=bpy.data.worlds.new('Studio');sc.world.use_nodes=True;sc.world.node_tree.nodes.get('Background').inputs[0].default_value=(.5,.5,.5,1)
ld=bpy.data.lights.new('Softbox','AREA');ld.energy=6000000;ld.size=700;lo=bpy.data.objects.new('Softbox',ld);sc.collection.objects.link(lo);lo.location=(400,-100,900)
cd=bpy.data.cameras.new('Preview');cam=bpy.data.objects.new('Preview',cd);sc.collection.objects.link(cam);sc.camera=cam;cam.location=(1000,-700,1150);cam.rotation_euler=(Vector((380,250,0))-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=950;cd.clip_end=5000
sc.render.filepath=str(O/'LEGO_preview.png');bpy.ops.render.render(write_still=True);bpy.ops.wm.save_as_mainfile(filepath=str(O/'LEGO_Assembly_Preview.blend'));print('LEGO_PREVIEW_READY',flush=True)
