import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).parent;out=root/'cleaned'
bpy.ops.wm.open_mainfile(filepath=str(out/'SilverCup.blend'))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8
silver=bpy.data.materials.new('Clean_Polished_Silver');silver.use_nodes=True
bsdf=silver.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(.68,.70,.72,1);bsdf.inputs['Metallic'].default_value=.96;bsdf.inputs['Roughness'].default_value=.19
bodies=[o for o in scene.objects if o.name.startswith('Trophy_SilverCup_LOD')]
for body in bodies:
    body.data.materials.append(silver)
    for p in body.data.polygons:p.material_index=len(body.data.materials)-1
    body['finish']='Clean silver PBR; new UVs on cleaned hybrid; original UVs/materials preserved in raw assets and companion baked map archive'
parts=[o for o in scene.objects if o.name.startswith('Cup_Plinth') or o.name=='Cup_Blank_Plate']
scene.render.bake.use_selected_to_active=False;scene.render.bake.margin=8;scene.render.bake.use_clear=True
for ob in parts:
    if not ob.name.startswith('Cup_Plinth'):continue
    mat=ob.data.materials[0].copy();ob.data.materials[0]=mat
    nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=nodes.get('Principled BSDF');output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL')
    emit=nodes.new('ShaderNodeEmission');links.new(bs.inputs['Base Color'].links[0].from_socket,emit.inputs['Color']);links.new(emit.outputs[0],output.inputs['Surface'])
    img=bpy.data.images.new(ob.name+'_Wood',width=512,height=512,alpha=False);tex=nodes.new('ShaderNodeTexImage');tex.image=img;nodes.active=tex
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=1.15,island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.bake(type='EMIT');img.filepath_raw=str(out/(ob.name+'_Wood.png'));img.file_format='PNG';img.save();img.pack()
    links.new(tex.outputs['Color'],bs.inputs['Base Color']);links.new(bs.outputs[0],output.inputs['Surface'])
    for node in list(nodes):
        if node not in [bs,output,tex]:nodes.remove(node)
def select_lod(lod):
    bpy.ops.object.select_all(action='DESELECT')
    for body in bodies:body.hide_set(True);body.hide_render=True
    body=next(o for o in bodies if o.name.endswith(str(lod)));body.hide_set(False);body.hide_render=False;body.select_set(True)
    for p in parts:p.select_set(True)
    bpy.context.view_layer.objects.active=body
    return body
for lod in [0,1,2]:
    body=select_lod(lod)
    suffix='' if lod==0 else '_LOD'+str(lod)
    bpy.ops.export_scene.gltf(filepath=str(out/('SilverCup'+suffix+'.glb')),use_selection=True,export_format='GLB')
    if lod==0:bpy.ops.export_scene.fbx(filepath=str(out/'SilverCup.fbx'),use_selection=True,axis_forward='-Z',axis_up='Y',path_mode='COPY',embed_textures=True)
select_lod(0)
scene.cycles.samples=32;scene.cycles.use_denoising=True;camera=scene.camera
for view,angle,z in [('front',0,.21),('side',math.pi/2,.21),('rear',math.pi,.21),('oblique',math.pi/4,.21),('bowl',math.pi/6,.6)]:
    camera.location=(math.sin(angle),-math.cos(angle),z);camera.rotation_euler=(Vector((0,0,.16))-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(out/('SilverCup_'+view+'.png'));bpy.ops.render.render(write_still=True)
for lod in [1,2]:
    select_lod(lod);camera.location=(.707,-.707,.21);camera.rotation_euler=(Vector((0,0,.16))-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(out/('SilverCup_LOD'+str(lod)+'_oblique.png'));bpy.ops.render.render(write_still=True)
body=select_lod(0)
scene['asset_status']='Ready for architectural display-case integration as generic blank-plate trophy; not a certified real award replica'
bpy.ops.wm.save_as_mainfile(filepath=str(out/'SilverCup.blend'))
bm=bmesh.new();bm.from_mesh(body.data);tree=BVHTree.FromBMesh(bm)
def hit(origin,direction):
    p=tree.ray_cast(Vector(origin),Vector(direction))[0];return list(p) if p is not None else None
tests={'bowl_center_downward_hit':hit((0,0,.4),(0,0,-1)),'left_handle_gap_ray':hit((-.06,-.2,.25),(0,1,0)),'right_handle_gap_ray':hit((.06,-.2,.25),(0,1,0))}
bm.free()
stats=[]
for ob in bodies+parts:
    bm=bmesh.new();bm.from_mesh(ob.data)
    stats.append({'name':ob.name,'triangles':sum(len(p.vertices)-2 for p in ob.data.polygons),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'uv_layers':len(ob.data.uv_layers),'material_slots':[m.name for m in ob.data.materials],'dimensions_m':list(ob.dimensions),'min_world_z':min((ob.matrix_world@v.co).z for v in ob.data.vertices)})
    bm.free()
checks={'surface_stats_before_welding_UV_seams':stats,'opening_ray_checks':tests,'files':[{ 'name':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in out.iterdir() if p.suffix in ['.blend','.glb','.fbx'] and not p.name.endswith('.blend1')],'quality_limits':['Generic blank plaque, no real award assertion','Original Trellis silver material archive retained; clean uniform PBR silver exported','Small sculptural trim is inferred from one image','Separate closed components overlap at stem/plinth contact; not a fabrication union'],'rejected':['figure','plaque']}
(out/'ready_manifest.json').write_text(json.dumps(checks,indent=2))
print('FINALIZATION COMPLETE')
