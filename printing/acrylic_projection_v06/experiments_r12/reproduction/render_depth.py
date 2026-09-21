import bpy,json,hashlib,time
import numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).parent; P=R.parent/'projection_acrylic_v06'
s=bpy.context.scene
inventory={'blender':bpy.app.version_string,'source_sha256':hashlib.sha256((P/'Source_Studio.blend').read_bytes()).hexdigest(),'working_copy':bpy.data.filepath,'objects':len(s.objects),'collections':list(bpy.data.collections.keys()),'original_engine':s.render.engine,'original_camera':s.camera.name if s.camera else None,'missing_external_images':[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and i.filepath and not Path(bpy.path.abspath(i.filepath)).exists()]}
(R/'depth_inventory.json').write_text(json.dumps(inventory,indent=2))
s.frame_set(1)
for o in s.objects:
    if o.type!='MESH':continue
    zmin=min((o.matrix_world@Vector(v)).z for v in o.bound_box)
    if zmin>=3.45 or any(c.name in ['ROOF','ROOF_DETAILS','UPPER','ROOM_LABELS','STUDENTS - toggle entire collection','V5_CEILING'] for c in o.users_collection) or any(k in o.name.lower() for k in ['ceiling','roof_top','roof_slab','bleacher']):o.hide_render=True
mat=bpy.data.materials.new('R12 measured camera depth in metres');mat.use_nodes=True
n=mat.node_tree.nodes;n.clear();camera=n.new('ShaderNodeCameraData');em=n.new('ShaderNodeEmission');out=n.new('ShaderNodeOutputMaterial')
mat.node_tree.links.new(camera.outputs['View Z Depth'],em.inputs['Color']);mat.node_tree.links.new(em.outputs[0],out.inputs['Surface'])
s.view_layers[0].material_override=mat
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=1;s.cycles.use_denoising=False
s.render.resolution_x=1024;s.render.resolution_y=1024;s.render.resolution_percentage=100
s.render.pixel_aspect_x=s.render.pixel_aspect_y=1;s.render.use_border=False;s.render.film_transparent=True;s.use_nodes=False
s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.image_settings.color_mode='RGBA'
d=bpy.data.cameras.new('R12 exact overhead depth');o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);s.camera=o;d.type='ORTHO';d.clip_start=.01;d.clip_end=100;d.dof.use_dof=False
report=[]
for r in json.loads((P/'rooms/room_contract.json').read_text()):
    if r['number'] not in ['108','102','121','122','GYM']:continue
    dest=R/'depth'/r['number'];dest.mkdir(parents=True,exist_ok=True)
    o.location=(*r['center_world_m'],3.5);o.rotation_euler=(0,0,0);d.ortho_scale=r['ortho_span_m']
    s.render.filepath=str(dest/'camera_depth_metres.exr');t=time.monotonic();bpy.ops.render.render(write_still=True)
    im=bpy.data.images.load(s.render.filepath,check_existing=False)
    pixels=np.asarray(im.pixels[:],dtype=np.float32).reshape(1024,1024,4)[::-1].copy()
    np.save(dest/'camera_depth_metres.npy',pixels[:,:,0]);bpy.data.images.remove(im)
    report.append({'room':r['number'],'camera_position':list(o.location),'ortho_span_m':d.ortho_scale,'resolution':[1024,1024],'seconds':time.monotonic()-t,'depth_semantics':'Blender Camera Data View Z Depth, metres, emission override, raw float EXR','raw_depth_units':'metres','guide_normalization_range_m':[0,4.5],'device':'CPU'})
    (R/'depth_render_report.json').write_text(json.dumps(report,indent=2));print('DEPTH_DONE',r['number'],flush=True)
assert hashlib.sha256((P/'Source_Studio.blend').read_bytes()).hexdigest()==inventory['source_sha256']

