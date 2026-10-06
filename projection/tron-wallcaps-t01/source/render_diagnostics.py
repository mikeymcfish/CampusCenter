import bpy,sys,json,numpy as np,time,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'source'))
from inspect_receiver import parse_obj,sha,SRC,OBJ,ORIGINAL_SRC
OUT=ROOT/'deliverables';QA=ROOT/'qa';INPUT=ROOT/'receiver_copy';INPUT.mkdir(exist_ok=True)
for name in [OBJ.name,'CampusCenter_P02_Assembly_1_100_UV01.mtl','Atlas_Diagnostic.png']:
    if (SRC/name).resolve()!=(INPUT/name).resolve():shutil.copy2(SRC/name,INPUT/name)
    elif not (INPUT/name).exists():shutil.copy2(ORIGINAL_SRC/name,INPUT/name)
v,u,parts=parse_obj(INPUT/OBJ.name);sel=np.load(ROOT/'cache/face_selection.npz')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=str(INPUT/OBJ.name),forward_axis='Y',up_axis='Z',global_scale=1.,use_split_objects=True,use_split_groups=False)
objects={o.name:o for o in bpy.context.scene.objects if o.type=='MESH'};assert set(objects)==set(parts)
checks=[]
for name,ob in objects.items():
    vv=np.array([ob.matrix_world@x.co for x in ob.data.vertices]);ff=np.array([p.vertices[:] for p in ob.data.polygons]);uv=np.array([l.uv[:] for l in ob.data.uv_layers.active.data]).reshape(-1,3,2)
    ce=float(np.max(abs(vv[ff]-v[parts[name]['f']])));ue=float(np.max(abs(uv-u[parts[name]['ft']])));assert ce<.0001 and ue<1e-6
    checks.append({'part':name,'faces':len(ff),'world_coordinate_error_mm':ce,'UV_error_in_8192_pixels':ue*8192,'identity_transform':bool(np.allclose(np.array(ob.matrix_world),np.eye(4),atol=0,rtol=0))})
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8
scene.render.threads_mode='FIXED';scene.render.threads=8;scene.render.resolution_x=1024;scene.render.resolution_y=786;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='8';scene.render.film_transparent=False
scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
world=bpy.data.worlds.new('Black_Unlit_World');world.use_nodes=True;world.node_tree.nodes.get('Background').inputs['Color'].default_value=(0,0,0,1);world.node_tree.nodes.get('Background').inputs['Strength'].default_value=0;scene.world=world
bpy.ops.object.camera_add(location=(348.25,252.875,2000));front=bpy.context.object;front.name='FrontNormal_PlusZ_Assumption';front.rotation_euler=(0,0,0);front.data.type='ORTHO';front.data.ortho_scale=726.25;front.data.clip_start=.1;front.data.clip_end=5000
bpy.ops.object.camera_add(location=(870,-550,830));oblique=bpy.context.object;oblique.name='Oblique_DIAGNOSTIC_Not_Projector'
from mathutils import Vector
oblique.rotation_euler=(Vector((348.25,252.875,20))-oblique.location).to_track_quat('-Z','Y').to_euler();oblique.data.type='ORTHO';oblique.data.ortho_scale=860;oblique.data.clip_end=5000
mat=bpy.data.materials.new('Full_Fixed_UV02_Atlas_Unlit');mat.use_nodes=True;n=mat.node_tree.nodes;n.clear();tex=n.new('ShaderNodeTexImage');tex.interpolation='Closest';tex.extension='CLIP';im=bpy.data.images.load(str(OUT/'Tron_UV02_QA_Atlas_00_8192.png'));im.pack();tex.image=im
em=n.new('ShaderNodeEmission');em.inputs['Strength'].default_value=1.;o=n.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(tex.outputs['Color'],em.inputs['Color']);mat.node_tree.links.new(em.outputs[0],o.inputs['Surface'])
for ob in objects.values():ob.data.materials.clear();ob.data.materials.append(mat)
scene.frame_start=1;scene.frame_end=240;scene.render.fps=24;scene.camera=front
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Tron_UV02_Receiver_Preview.blend'))
renders=[]
for camera,name in [(front,'Tron_QA_NativeBlender_FrontNormal_1024.png'),(oblique,'Tron_QA_NativeBlender_Oblique_1024.png')]:
    scene.camera=camera;scene.render.filepath=str(OUT/name);bpy.ops.render.render(write_still=True);renders.append(name)
def solid(name,color):
    mat=bpy.data.materials.new(name);mat.use_nodes=True;n=mat.node_tree.nodes;n.clear();em=n.new('ShaderNodeEmission');em.inputs[0].default_value=(*color,1);out=n.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(em.outputs[0],out.inputs['Surface']);return mat
excluded=solid('DIAGNOSTIC_Excluded',(0.018,0.023,0.030));caps=solid('DIAGNOSTIC_WallCaps_Cyan',(0.02,.65,.8));sides=solid('DIAGNOSTIC_WallSides_Violet',(.38,.05,.65))
for name,ob in objects.items():
    ob.data.materials.clear();ob.data.materials.append(excluded);ob.data.materials.append(caps);ob.data.materials.append(sides)
    if name=='Opaque':
        for i,p in enumerate(ob.data.polygons):p.material_index=1 if sel['cap'][i] else (2 if sel['sides'][i] else 0)
scene.camera=oblique;scene.render.filepath=str(OUT/'WallSelection_Oblique_DIAGNOSTIC_1024.png');bpy.ops.render.render(write_still=True);renders.append(Path(scene.render.filepath).name)
(QA/'Native_Blender_QA.json').write_text(json.dumps({'version':bpy.app.version_string,'source_sha256':sha(OBJ),'isolated_receiver_copy_sha256':sha(INPUT/OBJ.name),'parts':checks,'geometry_edits':[],'UV_edits':[],'renders':renders,'render_engine':'Cycles CPU','samples':8,'resolution':[1024,786],'color_management':'Standard / sRGB / emission only','preview_blend':'Tron_UV02_Receiver_Preview.blend','packed_atlas':'QA time0 frame','physical_projection_verified':False},indent=2))
print('NATIVE DIAGNOSTICS COMPLETE',flush=True)
