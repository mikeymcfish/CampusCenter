import bpy,json,pathlib,math,hashlib
from mathutils import Vector
ROOT=pathlib.Path(__file__).parent/'art_batch_v26_r01'
m=json.loads((ROOT/'manifest.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
s.render.engine='BLENDER_EEVEE';s.render.resolution_x=640;s.render.resolution_y=640;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';s.view_settings.view_transform='Standard'
s.world=bpy.data.worlds.new('ART26_World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.7,.7,.7,1)
def material(name,color):
 a=bpy.data.materials.new(name);a.diffuse_color=(*color,1);a.use_nodes=True;a.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*color,1);a.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.75;return a
frame=material('ART26_Frame_MatteCharcoal',(.025,.025,.025));context=material('QA_Wall',(.72,.72,.72))
def box(name,loc,dim,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);return o
assets=[]
for a in m['artworks']:
 if not a['instantiate']:a['alias_of']='ART26_IMG_1869';a['role']='wider grouping reference only; not an additional main artwork';continue
 id=a['stable_id'];px=a['texture_size'];w=.9;h=w*px[1]/px[0]
 if h>1.05:h=1.05;w=h*px[0]/px[1]
 parts=[box(id+'_back',(0,.01,0),(w+.05,.025,h+.05),frame)]
 for x in [-1,1]:parts.append(box(id+'_side'+str(x),(x*(w/2+.0125),-.0125,0),(.025,.045,h+.05),frame))
 for z in [-1,1]:parts.append(box(id+'_rail'+str(z),(0,-.0125,z*(h/2+.0125)),(w,.045,.025),frame))
 img=bpy.data.images.load(str(ROOT/a['texture']));img.colorspace_settings.name='sRGB'
 mat=material(id+'_Photo',(.8,.8,.8));nodes=mat.node_tree.nodes;tex=nodes.new('ShaderNodeTexImage');tex.image=img;p=nodes.get('Principled BSDF');mat.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color']);p.inputs['Roughness'].default_value=1
 mesh=bpy.data.meshes.new(id+'_PhotoSurface');mesh.from_pydata([(-w/2,-.024,-h/2),(w/2,-.024,-h/2),(w/2,-.024,h/2),(-w/2,-.024,h/2)],[],[(0,1,2,3)]);mesh.uv_layers.new()
 for loop,uv in zip(mesh.uv_layers.active.data,[(0,0),(1,0),(1,1),(0,1)]):loop.uv=uv
 photo=bpy.data.objects.new(id+'_photo',mesh);s.collection.objects.link(photo);photo.data.materials.append(mat);parts.append(photo)
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name=id
 s.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');o['stable_id']=id;o['source_photo']=a['source'];o['reconstruction_status']=a['reconstruction_status']
 bpy.ops.export_scene.fbx(filepath=str(ROOT/'exports'/f'{id}.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',bake_anim=False,path_mode='RELATIVE',use_mesh_modifiers=True)
 bpy.ops.export_scene.gltf(filepath=str(ROOT/'exports'/f'{id}.glb'),use_selection=True,export_format='GLB',export_animations=False)
 i=len(assets);y=1.8+(i%6)*1.3;z=.95 if i<6 else 2.45
 a.update({'estimated_dimensions_m':[round(w+.05,5),.0575,round(h+.05,5)],'dimension_basis':'reversible presentation size; not measured artwork dimensions','pivot':'centre of photo, wall backing local y=0; front local -Y','fbx':'exports/'+id+'.fbx','glb':'exports/'+id+'.glb','material_slots':[slot.material.name for slot in o.material_slots],'collision':'Disable collision for shallow wall frames; no floor footprint','proposed_anchor':{'room':'G105 Gallery','support_object':'Lab_east_wall0','blender_position_m':[.15,y,z],'blender_rotation_deg':[0,0,90],'unreal_position_cm':[15,-y*100,z*100],'unreal_rotation_deg':{'pitch':0,'yaw':-90,'roll':0},'status':'PROPOSED_CURRENT_MAP_TRACE_REQUIRED','front_normal_blender':[1,0,0]}})
 assets.append((o,a));o.hide_render=True
bpy.ops.object.camera_add(location=(1,-3,1));camera=bpy.context.object;s.camera=camera
camera.data.type='ORTHO'
def aim(pos,target,scale):camera.location=pos;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=scale
bpy.ops.object.light_add(type='AREA',location=(1,-3,3));light=bpy.context.object;light.data.energy=120;light.data.shape='DISK';light.data.size=5;light.rotation_euler=(Vector((0,0,0))-light.location).to_track_quat('-Z','Y').to_euler()
for o,a in assets:
 o.hide_render=False;aim((.25,-3,.15),(0,0,0),max(a['estimated_dimensions_m'])*1.3);s.render.filepath=str(ROOT/'renders'/f"{o.name}.png");bpy.ops.render.render(write_still=True);o.hide_render=True
for o,a in assets:
 o.hide_render=False;o.location=a['proposed_anchor']['blender_position_m'];o.rotation_euler.z=math.pi/2
wall=box('QA_ONLY_Lab_east_wall0',(0,5.47895,2.1336),(.25,8.83016,4.2672),context)
floor=box('QA_ONLY_Gallery_floor',(5,5.5,-.06),(10,10,.1),context)
wall['qa_only']=True;floor['qa_only']=True
aim((14,3.9,4.4),(.15,5.05,1.85),10.2);light.location=(8,5,5);light.rotation_euler=(Vector((0,5,1.8))-light.location).to_track_quat('-Z','Y').to_euler();light.data.energy=450
s.render.filepath=str(ROOT/'renders/proposed_layout.png');bpy.ops.render.render(write_still=True)
m['layout_render_scope']='Art-only schematic with inventory-derived west wall and floor context. It is not a current furnished-room render.'
m['blender_version']=bpy.app.version_string;m['asset_count']=len(assets);m['three_dimensional_limits']='Volumetric sculpture/mannequin reconstructions remain deferred; these are honest photo presentations per planning inventory, not complete sculpture meshes.'
for o,a in assets: a['mesh_vertices']=len(o.data.vertices);a['mesh_faces']=len(o.data.polygons)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source/CampusCenter_Art26_R01.blend'))
(ROOT/'manifest.json').write_text(json.dumps(m,indent=2))
print('ART26_READY',len(assets),flush=True)
