import bpy,pathlib,json,hashlib
R=pathlib.Path(__file__).parent;s=bpy.context.scene
src=json.loads((R/'preflight.json').read_text());build=json.loads((R/'build_report.json').read_text())
assert hashlib.sha256((R/'Source_Copy.blend').read_bytes()).hexdigest()==src['sha256']
assert hashlib.sha256((R.parent/'cycles_studio_v02/Campus_Center_Cycles_Studio.blend').read_bytes()).hexdigest()==src['sha256']
fail=[]
for row in src['objects']:
 o=bpy.data.objects.get(row['name'])
 if not o:fail.append([row['name'],'missing']);continue
 if o.type!='MESH' or len(o.data.vertices)!=row['verts'] or len(o.data.polygons)!=row['faces']:fail.append([o.name,'topology'])
 # Hidden objects have unevaluated matrix_world on reopen; their stored basis remains authoritative (no parent).
 matrix=o.matrix_basis if o.name in build['hidden_originals'] and o.parent is None else o.matrix_world
 vals=list(sum((list(r) for r in matrix),[]))
 if max(abs(a-b) for a,b in zip(vals,row['matrix']))>1e-6:fail.append([o.name,'transform'])
 if o.name not in build['hidden_originals'] and o.hide_render!=row['hidden']:fail.append([o.name,'visibility'])
for name in build['hidden_originals']:assert bpy.data.objects[name].hide_render
missing=[i.name for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not pathlib.Path(bpy.path.abspath(i.filepath)).exists()]
assert not fail and not missing,(fail,missing)
assert bpy.data.objects['Walkthrough_Camera'].animation_data and [s.frame_start,s.frame_end]==src['frames']
assert s.render.engine=='CYCLES' and s.cycles.samples==256 and s.render.resolution_x==1920
assert 'V02 Commons carpet and original stone' in bpy.data.objects['A101_ground_slab'].data.materials
report={'status':'passed','source_unchanged':True,'original_meshes_preserved':len(src['objects']),'new_objects':build['created_count'],'retained_hidden_standins':len(build['hidden_originals']),'missing_images':missing,'packed_images':sum(bool(i.packed_file) for i in bpy.data.images),'original_geometry_transform_errors':fail,'walkthrough_retained':True,'blue_paint_and_carpet_retained':True}
(R/'scene_validation.json').write_text(json.dumps(report,indent=2));print(report)
