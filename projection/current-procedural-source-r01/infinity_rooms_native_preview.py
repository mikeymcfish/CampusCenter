import bpy,sys,json,numpy as np,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).parent;sys.path.insert(0,str(R));from uvprep_common import parse_obj,sha
D=R/'madmapper_infinity_rooms_R02/deliverables';OBJ=R/'madmapper_hybrid_UV02/deliverables/CampusCenter_P02plusP03B3_Assembly_1_100_UV02.obj'
v,u,n,parts=parse_obj(OBJ);files=sorted(D.glob('*_Lossless_Atlas_4096.png'));assert len(files)==5
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.obj_import(filepath=str(OBJ),forward_axis='Y',up_axis='Z',global_scale=1.,use_split_objects=True,use_split_groups=False)
objects={o.name:o for o in bpy.context.scene.objects if o.type=='MESH'};assert set(objects)==set(parts);checks=[]
for name,ob in objects.items():
    vv=np.array([ob.matrix_world@x.co for x in ob.data.vertices],np.float64);ff=np.array([p.vertices[:] for p in ob.data.polygons]);uv=np.array([l.uv[:] for l in ob.data.uv_layers.active.data],np.float64).reshape(-1,3,2)
    err=float(np.max(abs(vv[ff]-v[parts[name]['f']])));ue=float(np.max(abs(uv-u[parts[name]['ft']])));assert err<.0001 and ue<1e-6
    assert np.array_equal(np.array(ob.matrix_world),np.eye(4));checks.append({'part':name,'triangles':len(ff),'world_vertex_error_mm':err,'UV_error':ue,'identity_world_transform':True})
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=4;scene.render.resolution_x=1024;scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.dither_intensity=0.;scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
world=bpy.data.worlds.new('Infinity_Exact_Black_World');world.use_nodes=True;world.node_tree.nodes.get('Background').inputs['Color'].default_value=(0,0,0,1);world.node_tree.nodes.get('Background').inputs['Strength'].default_value=0.;scene.world=world
eye=Vector((348.25,-600.,850.));target=Vector((348.25,252.875,12.))
bpy.ops.object.camera_add(location=eye);cam=bpy.context.object;cam.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.sensor_fit='HORIZONTAL';cam.data.sensor_width=36.;cam.data.lens=36./(2*math.tan(math.radians(42/2)));cam.data.clip_start=.1;cam.data.clip_end=5000;scene.camera=cam
mat=bpy.data.materials.new('Original_UV02_Infinity_One_Atlas_Emission');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();tex=nodes.new('ShaderNodeTexImage');tex.interpolation='Closest';tex.extension='CLIP';em=nodes.new('ShaderNodeEmission');em.inputs['Strength'].default_value=1;out=nodes.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(tex.outputs['Color'],em.inputs['Color']);mat.node_tree.links.new(em.outputs[0],out.inputs['Surface'])
for ob in objects.values():ob.data.materials.clear();ob.data.materials.append(mat)
renders=[]
for file in files:
    im=bpy.data.images.load(str(file),check_existing=False);im.colorspace_settings.name='sRGB';tex.image=im
    output=D/(file.stem.replace('_Lossless_Atlas_4096','')+'_Native_Fixed_Front_1024.png');assert not output.exists();scene.render.filepath=str(output);bpy.ops.render.render(write_still=True)
    renders.append({'atlas':file.name,'atlas_SHA256':sha(file),'native_preview':output.name});bpy.data.images.remove(im)
q={'status':'PASS','receiver_SHA256':sha(OBJ),'Blender_version':bpy.app.version_string,'factory_scene_fresh_OBJ_import':True,'original_parts_and_UVs_verified':checks,'all_four_parts_one_common_atlas':True,'shader':'Emission1, nearest original UV02 texture, sRGB Standard; no lights; exact black world; dither0','eye_mm':list(eye),'target_mm':list(target),'HFOV_degrees':42,'fixed_camera_no_orbit_or_geometry_animation':True,'resolution':[1024,768],'renders':renders,'original_Blender_Unreal_MadMapper_or_print_projects_saved':False,'physical_projection_or_MadMapper_playback_tested':False}
(D/'Native_Fixed_Front_Reapplication_QA.json').write_text(json.dumps(q,indent=2),encoding='utf-8');print('INFINITY NATIVE FIXED FRONT PASS',len(files),flush=True)
