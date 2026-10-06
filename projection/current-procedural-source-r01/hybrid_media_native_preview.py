import bpy,sys,json,numpy as np,argparse
from pathlib import Path
R=Path(__file__).parent;sys.path.insert(0,str(R));from uvprep_common import parse_obj,sha
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];ap=argparse.ArgumentParser();ap.add_argument('--folder',required=True);ap.add_argument('--pattern',required=True);ap.add_argument('--black-background',action='store_true');a=ap.parse_args(args)
D=R/a.folder;OBJ=R/'madmapper_hybrid_UV02/deliverables/CampusCenter_P02plusP03B3_Assembly_1_100_UV02.obj';v,u,n,parts=parse_obj(OBJ)
files=sorted(D.glob(a.pattern));assert files
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.obj_import(filepath=str(OBJ),forward_axis='Y',up_axis='Z',global_scale=1.,use_split_objects=True,use_split_groups=False)
objects={o.name:o for o in bpy.context.scene.objects if o.type=='MESH'};assert set(objects)==set(parts);checks=[]
for name,ob in objects.items():
    vv=np.array([ob.matrix_world@x.co for x in ob.data.vertices],np.float64);ff=np.array([p.vertices[:] for p in ob.data.polygons]);uv=np.array([l.uv[:] for l in ob.data.uv_layers.active.data],np.float64).reshape(-1,3,2)
    err=float(np.max(abs(vv[ff]-v[parts[name]['f']])));uerr=float(np.max(abs(uv-u[parts[name]['ft']])));assert err<.0001 and uerr<1e-6;assert np.array_equal(np.array(ob.matrix_world),np.eye(4))
    checks.append({'part':name,'triangles':len(ff),'world_error_mm':err,'UV_error_8192px':uerr*8192,'identity_world_transform':True})
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=4;scene.render.resolution_x=2048;scene.render.resolution_y=1572;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
if a.black_background:scene.render.dither_intensity=0.
world=bpy.data.worlds.new('Matched_Unlit_World');world.use_nodes=True;world.node_tree.nodes.get('Background').inputs['Color'].default_value=(0,0,0,1) if a.black_background else (.003,.005,.009,1);world.node_tree.nodes.get('Background').inputs['Strength'].default_value=0. if a.black_background else 1.;scene.world=world
bpy.ops.object.camera_add(location=(348.25,252.875,2000));cam=bpy.context.object;cam.rotation_euler=(0,0,0);cam.data.type='ORTHO';cam.data.ortho_scale=726.25;cam.data.clip_start=.1;cam.data.clip_end=5000;scene.camera=cam
mat=bpy.data.materials.new('Hybrid_common_atlas_Emission');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();tex=nodes.new('ShaderNodeTexImage');tex.interpolation='Closest';tex.extension='CLIP';em=nodes.new('ShaderNodeEmission');em.inputs['Strength'].default_value=1;output=nodes.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(tex.outputs['Color'],em.inputs['Color']);mat.node_tree.links.new(em.outputs[0],output.inputs['Surface'])
for ob in objects.values():ob.data.materials.clear();ob.data.materials.append(mat)
renders=[]
for png in files:
    im=bpy.data.images.load(str(png),check_existing=False);im.colorspace_settings.name='sRGB';tex.image=im
    target=D/(png.stem.replace('_Atlas_4096','').replace('_Atlas_8192','')+'_Native_Mapped_Preview.png');scene.render.filepath=str(target);bpy.ops.render.render(write_still=True)
    renders.append({'atlas':png.name,'atlas_sha256':sha(png),'native_preview':target.name})
    bpy.data.images.remove(im)
(D/'Native_Hybrid_Media_Reapplication_QA.json').write_text(json.dumps({'status':'PASS','Blender_version':bpy.app.version_string,'receiver_OBJ':str(OBJ),'receiver_OBJ_sha256':sha(OBJ),'fresh_factory_import':True,'import_checks':checks,'all_parts_one_common_unlit_atlas':True,'lights':0,'view':'Unchanged orthographic +Z canvas726.25mm center348.25,252.875','shader':'Emission strength1; sRGB; Standard; nearest','renders':renders,'physical_projection_or_MadMapper_playback_verified':False,'original_Blender_Unreal_receiver_or_media_saved':False},indent=2))
print('NATIVE MATCHED MEDIA REAPPLICATION PASS',len(files),flush=True)
