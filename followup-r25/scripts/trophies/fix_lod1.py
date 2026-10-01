import bpy,bmesh,json,hashlib
from pathlib import Path
root=Path(__file__).parent/'cleaned'
bpy.ops.wm.open_mainfile(filepath=str(root/'SilverCup.blend'))
ob=bpy.data.objects['Trophy_SilverCup_LOD1'];bm=bmesh.new();bm.from_mesh(ob.data)
edges=[e for e in bm.edges if e.is_boundary]
print('BOUNDARY_LENGTHS',[e.calc_length() for e in edges])
boundary_verts=list({v for e in edges for v in e.verts})
isolated_faces={f for e in edges for f in e.link_faces if all(edge.is_boundary for edge in f.edges)}
if isolated_faces:
    tiny_verts={v for f in isolated_faces for v in f.verts}
    bmesh.ops.delete(bm,geom=list(isolated_faces),context='FACES')
    bmesh.ops.delete(bm,geom=[v for v in tiny_verts if v.is_valid and not v.link_faces],context='VERTS')
    boundary_verts=list({v for e in bm.edges if e.is_boundary for v in e.verts})
bmesh.ops.remove_doubles(bm,verts=boundary_verts,dist=.0000001)
edges=[e for e in bm.edges if e.is_boundary]
bmesh.ops.dissolve_degenerate(bm,edges=edges,dist=.0000001)
edges=[e for e in bm.edges if e.is_boundary]
new=bmesh.ops.holes_fill(bm,edges=edges,sides=4)['faces']
bmesh.ops.triangulate(bm,faces=new);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
    if o.name.startswith('Trophy_SilverCup_LOD'):o.hide_set(True);o.hide_render=True
ob.hide_set(False);ob.hide_render=False;ob.select_set(True)
for o in bpy.data.objects:
    if o.name.startswith('Cup_Plinth') or o.name=='Cup_Blank_Plate':o.select_set(True)
bpy.context.view_layer.objects.active=ob
bpy.ops.export_scene.gltf(filepath=str(root/'SilverCup_LOD1.glb'),use_selection=True,export_format='GLB')
scene=bpy.context.scene;scene.render.filepath=str(root/'SilverCup_LOD1_oblique.png');bpy.ops.render.render(write_still=True)
ob.hide_set(True);ob.hide_render=True;main=bpy.data.objects['Trophy_SilverCup_LOD0'];main.hide_set(False);main.hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=str(root/'SilverCup.blend'))
bm=bmesh.new();bm.from_mesh(ob.data)
manifest=json.loads((root/'ready_manifest.json').read_text())
entry=next(x for x in manifest['surface_stats_before_welding_UV_seams'] if x['name']==ob.name)
entry.update(triangles=sum(len(p.vertices)-2 for p in ob.data.polygons),boundary_edges=sum(e.is_boundary for e in bm.edges),nonmanifold_edges=sum(not e.is_manifold for e in bm.edges))
bm.free();manifest['LOD1_last_repair']='filled one three-edge boundary after decimation'
for entry in manifest['files']:
    p=root/entry['name'];entry.update(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
(root/'ready_manifest.json').write_text(json.dumps(manifest,indent=2))
print('LOD1 PATCH',len(new))
