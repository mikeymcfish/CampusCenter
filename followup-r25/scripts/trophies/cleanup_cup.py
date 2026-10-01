import bpy,bmesh,json,math,time,subprocess,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).parent
out=root/'cleaned';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'prototypes/cup.blend'))
source=next(o for o in bpy.data.objects if o.type=='MESH')
source.name='Trellis_Cup_Source_BakeOnly'
bpy.ops.object.select_all(action='DESELECT');source.select_set(True);bpy.context.view_layer.objects.active=source
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
source.location=(0,0,0)
bm=bmesh.new();bm.from_mesh(source.data)
tree=BVHTree.FromBMesh(bm)
original_hits={str((x,y)):list(tree.ray_cast(Vector((x,y,.4)),Vector((0,0,-1)))[0]) if tree.ray_cast(Vector((x,y,.4)),Vector((0,0,-1)))[0] is not None else None for x,y in [(0,0),(.03,0),(.04,0),(.075,0)]}
bm.free()
body=source.copy();body.data=source.data.copy();bpy.context.collection.objects.link(body);body.name='Trophy_SilverCup_LOD0'
bm=bmesh.new();bm.from_mesh(body.data)
bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.z<.098],context='VERTS')
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=0.000002)
bm.to_mesh(body.data);bm.free()
bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body
bm=bmesh.new();bm.from_mesh(body.data)
unseen=set(bm.verts);groups=[]
while unseen:
    todo=[unseen.pop()];group=[]
    while todo:
        v=todo.pop();group.append(v)
        for e in v.link_edges:
            w=e.other_vert(v)
            if w in unseen:unseen.remove(w);todo.append(w)
    groups.append(group)
groups.sort(key=len,reverse=True)
small=[g for g in groups if len(g)<30]
removed=sum(len(g) for g in small)
if small:bmesh.ops.delete(bm,geom=[v for g in small for v in g],context='VERTS')
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(body.data);bm.free()
bm=bmesh.new();bm.from_mesh(body.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(body.data);bm.free()
np.savez(out/'body_repair_input.npz',vertices=np.array([v.co[:] for v in body.data.vertices]),faces=np.array([p.vertices[:] for p in body.data.polygons]))
embedded='T:/AI/Comfy2601/ComfyUI/ComfyUI_TRELLIS2_portable/python_embeded/python.exe'
subprocess.run([embedded,'-s',str(root/'repair_meshlib.py'),str(out/'body_repair_input.npz'),'30000'],check=True)
repaired=np.load(out/'body_repair_input_repaired.npz')
newmesh=bpy.data.meshes.new('Repaired_Trellis_Cup');newmesh.from_pydata(repaired['vertices'].tolist(),[],repaired['faces'].tolist());newmesh.update();body.data=newmesh
for p in body.data.polygons:p.use_smooth=True
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=1.15,island_margin=.012);bpy.ops.object.mode_set(mode='OBJECT')
targetmat=bpy.data.materials.new('Trellis_Cup_Baked_PBR');targetmat.use_nodes=True;body.data.materials.clear();body.data.materials.append(targetmat)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8
scene.render.bake.use_selected_to_active=True;scene.render.bake.use_clear=True;scene.render.bake.cage_extrusion=.002;scene.render.bake.max_ray_distance=.004;scene.render.bake.margin=8
origmat=source.data.materials[0]
original_bsdf=next(n for n in origmat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
images={}
for label,socket in [('BaseColor','Base Color'),('Metallic','Metallic'),('Roughness','Roughness')]:
    image=bpy.data.images.new('Cup_'+label,width=1024,height=1024,alpha=False)
    if label!='BaseColor':image.colorspace_settings.name='Non-Color'
    node=targetmat.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;targetmat.node_tree.nodes.active=node
    mat=origmat.copy();mat.name='BakeSource_'+label
    bsdf=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    output=next(n for n in mat.node_tree.nodes if n.type=='OUTPUT_MATERIAL')
    emit=mat.node_tree.nodes.new('ShaderNodeEmission')
    if bsdf.inputs[socket].is_linked:mat.node_tree.links.new(bsdf.inputs[socket].links[0].from_socket,emit.inputs['Color'])
    else:
        value=bsdf.inputs[socket].default_value
        emit.inputs['Color'].default_value=value if hasattr(value,'__len__') else (value,value,value,1)
    mat.node_tree.links.new(emit.outputs[0],output.inputs['Surface']);source.data.materials[0]=mat
    bpy.ops.object.select_all(action='DESELECT');source.select_set(True);body.select_set(True);bpy.context.view_layer.objects.active=body
    bpy.ops.object.bake(type='EMIT')
    image.filepath_raw=str(out/('Cup_'+label+'.png'));image.file_format='PNG';image.save();image.pack();images[label]=node
source.data.materials[0]=origmat
target_bsdf=next(n for n in targetmat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
for label,socket in [('BaseColor','Base Color'),('Metallic','Metallic'),('Roughness','Roughness')]:targetmat.node_tree.links.new(images[label].outputs['Color'],target_bsdf.inputs[socket])
bpy.data.objects.remove(source,do_unlink=True)
def material(name,color,metal=0,rough=.3):
    m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
wood=material('Clean_Walnut_Plinth',(.085,.037,.019),0,.32)
# Object-coordinate wood grain avoids a dependency on external texture files.
n=wood.node_tree.nodes;t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=8;t.inputs['Detail'].default_value=2
tex=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(14,14,1)
wood.node_tree.links.new(tex.outputs['Generated'],mapping.inputs[0]);wood.node_tree.links.new(mapping.outputs[0],t.inputs[0])
ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.035,.014,.006,1);ramp.color_ramp.elements[1].color=(.14,.065,.027,1)
wood.node_tree.links.new(t.outputs['Fac'],ramp.inputs[0]);wood.node_tree.links.new(ramp.outputs['Color'],n.get('Principled BSDF').inputs['Base Color'])
silver=material('Blank_Silver_Plate',(.63,.65,.67),.8,.25)
parts=[body]
def box(name,loc,dims,mat,bevel):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
    if bevel:
        m=o.modifiers.new('Machined_Edge','BEVEL');m.width=bevel;m.segments=3;bpy.ops.object.modifier_apply(modifier=m.name)
    parts.append(o);return o
box('Cup_Plinth_Step',(0,0,.009),(.132,.119,.018),wood,.0015)
box('Cup_Plinth_Block',(0,0,.053),(.111,.106,.076),wood,.0012)
box('Cup_Plinth_Top',(0,0,.094),(.120,.113,.012),wood,.001)
box('Cup_Blank_Plate',(0,-.054,.052),(.091,.0015,.055),silver,.0005)
body['provenance']='Trellis.2-4B cup; Meshlib boundary repair, small islands removed, source PBR baked; plinth/blank plate manually rebuilt'
body['model_revision']='af44b45f2e35a493886929c6d786e563ec68364d'
body['prototype_status']='cleaned integration candidate; exact award text intentionally blank'
lodcol=bpy.data.collections.new('LOD Alternatives - hidden');scene.collection.children.link(lodcol)
for lod,target in [(1,12000),(2,4500)]:
    duplicate=body.copy();duplicate.data=body.data.copy();lodcol.objects.link(duplicate);duplicate.name='Trophy_SilverCup_LOD'+str(lod)
    bpy.ops.object.select_all(action='DESELECT');duplicate.select_set(True);bpy.context.view_layer.objects.active=duplicate
    m=duplicate.modifiers.new('Distance_LOD','DECIMATE');m.ratio=target/sum(len(p.vertices)-2 for p in duplicate.data.polygons);m.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=m.name)
    duplicate.hide_render=True;duplicate.hide_set(True)
    for p in parts:p.select_set(False)
    duplicate.hide_set(False);duplicate.hide_render=False
    duplicate.select_set(True)
    for p in parts[1:]:p.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(out/('SilverCup_LOD'+str(lod)+'.glb')),use_selection=True,export_format='GLB')
    duplicate.hide_render=True;duplicate.hide_set(True)
bpy.ops.object.select_all(action='DESELECT')
for p in parts:p.select_set(True)
bpy.context.view_layer.objects.active=body
bpy.ops.export_scene.gltf(filepath=str(out/'SilverCup.glb'),use_selection=True,export_format='GLB')
bpy.ops.export_scene.fbx(filepath=str(out/'SilverCup.fbx'),use_selection=True,axis_forward='-Z',axis_up='Y',path_mode='COPY',embed_textures=True)
scene.cycles.samples=32;scene.cycles.use_denoising=True
camera=scene.camera;camera.data.ortho_scale=.496
views=[('front',0,.21),('side',math.pi/2,.21),('rear',math.pi,.21),('oblique',math.pi/4,.21),('bowl',math.pi/6,.6)]
for view,angle,z in views:
    camera.location=(math.sin(angle),-math.cos(angle),z);camera.rotation_euler=(Vector((0,0,.16))-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(out/('SilverCup_'+view+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'SilverCup.blend'))
stats=[]
for p in parts+[o for o in lodcol.objects]:
    bm=bmesh.new();bm.from_mesh(p.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
    stats.append({'name':p.name,'triangles':sum(len(q.vertices)-2 for q in p.data.polygons),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'uv_layers':len(p.data.uv_layers),'dimensions_m':list(p.dimensions)});bm.free()
(out/'cleanup_manifest.json').write_text(json.dumps({'source':'prototypes/cup.blend','repair_method':'Meshlib min-area hole filling; no voxel remesh','meshlib':json.loads((out/'body_repair_input_repair.json').read_text()),'removed_small_island_vertices':removed,'original_vertical_ray_hits':original_hits,'manual_changes':['reconstructed plinth and blank plate','boundary repair of Trellis metal body','source PBR baked to new UVs at 1024','LOD variants'],'parts':stats,'rejected_assets':{'figure':'fragmented ornaments and poor fine geometry; not integration ready','plaque':'holes and reconstructed text relief; not integration ready'}},indent=2))
print('CLEANUP COMPLETE')
