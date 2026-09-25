"""Isolated world-space mesh decals and their architectural mounting surfaces."""
import bpy,json,math
from pathlib import Path
R=Path(__file__).parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);return m
oak=mat('Display_PaleOak',(.48,.33,.19));cork=mat('Display_Cork',(.30,.22,.145));white=mat('Display_Ivory',(.73,.72,.66));dark=mat('Display_Shadow',(.055,.05,.04))
def mesh(name,verts,faces,material,uvs=None):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(material)
 if uvs:
  uv=me.uv_layers.new(name='UVMap')
  for loop in me.loops:uv.data[loop.index].uv=uvs[loop.vertex_index]
 return o
def box(name,c,s,m):
 vs=[(c[0]+x*s[0]/2,c[1]+y*s[1]/2,c[2]+z*s[2]/2) for x,y,z in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
 return mesh(name,vs,[tuple(reversed(f)) for f in [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]],m)
data=json.loads((R/'asset_inventory.json').read_text());placements=[]
art=[it for it in data if it['category']=='artwork']
for i,it in enumerate(art):
 bbox=it['alpha_bbox'];ratio=(bbox[2]-bbox[0])/(bbox[3]-bbox[1]);h=min(1.08,.94/ratio);w=h*ratio
 x=-10.55+i*1.18;y=16.172;z=1.80
 mesh('DD_Artwork_%02d'%it['id'],[(x-w/2,y,z-h/2),(x+w/2,y,z-h/2),(x+w/2,y,z+h/2),(x-w/2,y,z+h/2)],[(0,1,2,3)],mat('Decal_%02d'%it['id'],(.5,.5,.5)),[(0,0),(1,0),(1,1),(0,1)])
 placements.append({'id':it['id'],'label':'DD_Artwork_%02d'%it['id'],'category':'artwork','center_blender_m':[x,y,z],'size_m':[w,h],'facing':'south; opposite lab north glass'})
# Matches the reference's cork exhibition field over pale timber dado.
box('DD_Gallery_Cork',(-5.83,16.207,1.80),(10.72,.038,1.62),cork)
box('DD_Gallery_Dado',(-5.83,16.212,.56),(10.72,.028,1.10),oak)
for z in [.995,2.615]:box('DD_Gallery_Rail_'+str(z),(-5.83,16.175,z),(10.78,.06,.035),oak)
for i,it in enumerate([it for it in data if it['category']=='trophy']):
 bbox=it['alpha_bbox'];ratio=(bbox[2]-bbox[0])/(bbox[3]-bbox[1]);h=[.60,.58,.72,.68,.69,.63,.51,.66,.54,.54][i];w=h*ratio
 x=-25.878;y=18.35+i*1.045;z=1.24+h/2
 mesh('DD_Trophy_%02d'%it['id'],[(x,y+w/2,z-h/2),(x,y-w/2,z-h/2),(x,y-w/2,z+h/2),(x,y+w/2,z+h/2)],[(0,1,2,3)],mat('Decal_%02d'%it['id'],(.5,.5,.5)),[(0,0),(1,0),(1,1),(0,1)])
 placements.append({'id':it['id'],'label':'DD_Trophy_%02d'%it['id'],'category':'trophy','center_blender_m':[x,y,z],'size_m':[w,h],'base_height_m':1.24,'facing':'west; opposite lockers'})
box('DD_Trophy_Shelf',(-26.00,23.0525,1.205),(.32,10.40,.07),oak)
box('DD_Trophy_Backboard',(-25.865,23.0525,1.84),(.025,10.40,1.20),white)
box('DD_Trophy_ShadowReveal',(-25.875,23.0525,1.135),(.02,10.40,.022),dark)
for y in [18.5,20.5,22.5,24.5,26.5,27.6]:box('DD_Shelf_Bracket_'+str(y),(-25.99,y,1.115),(.25,.035,.10),dark)
(R/'placements.json').write_text(json.dumps(placements,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Decal_Display_Layer.blend'))
bpy.ops.export_scene.gltf(filepath=str(R/'Decal_Display_Layer.glb'),export_format='GLB',export_animations=False,export_cameras=False,export_lights=False)
print('BUILT',len(placements),'decal cards')
