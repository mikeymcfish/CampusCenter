import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).parent/'cleaned'
results=[]
for filename in ['SilverCup.blend','SilverCup.glb','SilverCup.fbx','SilverCup_LOD1.glb','SilverCup_LOD2.glb']:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    path=root/filename
    if path.suffix=='.blend':bpy.ops.wm.open_mainfile(filepath=str(path))
    elif path.suffix=='.fbx':bpy.ops.import_scene.fbx(filepath=str(path))
    else:bpy.ops.import_scene.gltf(filepath=str(path))
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render]
    bounds=[o.matrix_world@Vector(v) for o in objects for v in o.bound_box]
    low=[min(v[i] for v in bounds) for i in range(3)];high=[max(v[i] for v in bounds) for i in range(3)]
    stats=[]
    for o in objects:
        images=[]
        for m in o.data.materials:
            if m and m.use_nodes:
                for n in m.node_tree.nodes:
                    if n.type=='TEX_IMAGE' and n.image:images.append({'name':n.image.name,'size':list(n.image.size),'packed':bool(n.image.packed_file)})
        bm=bmesh.new();bm.from_mesh(o.data)
        before={'boundary':sum(e.is_boundary for e in bm.edges),'nonmanifold':sum(not e.is_manifold for e in bm.edges)}
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0000001)
        stats.append({'name':o.name,'triangles':sum(len(p.vertices)-2 for p in o.data.polygons),'uv_layers':len(o.data.uv_layers),'images':images,'raw_topology':before,'welded_boundary_edges':sum(e.is_boundary for e in bm.edges),'welded_nonmanifold_edges':sum(not e.is_manifold for e in bm.edges)});bm.free()
    results.append({'filename':filename,'mesh_count':len(objects),'total_triangles':sum(x['triangles'] for x in stats),'dimensions_m':[high[i]-low[i] for i in range(3)],'minimum_z':low[2],'objects':stats})
# Render the actual imported GLB using the verified Blend's studio setup.
bpy.ops.wm.open_mainfile(filepath=str(root/'SilverCup.blend'))
scene=bpy.context.scene
for o in list(scene.objects):
    if o.type=='MESH':bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(root/'SilverCup.glb'))
scene.render.filepath=str(root/'SilverCup_GLBreimport.png')
bpy.ops.render.render(write_still=True)
(root/'export_validation.json').write_text(json.dumps(results,indent=2))
print('EXPORT VALIDATIONS',len(results))
