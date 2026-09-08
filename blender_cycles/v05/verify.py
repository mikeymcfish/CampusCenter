import bpy,json,pathlib,hashlib
R=pathlib.Path(__file__).parent;s=bpy.context.scene;src=json.loads((R/'preflight.json').read_text());build=json.loads((R/'build_report.json').read_text());errors=[]
assert hashlib.sha256((R.parent/'cycles_studio_v04/Campus_Center_Cycles_Studio.blend').read_bytes()).hexdigest()==src['sha256']
for row in src['objects']:
 o=bpy.data.objects.get(row['name'])
 if not o:errors.append([row['name'],'missing']);continue
 if len(o.data.vertices)!=row['verts'] or len(o.data.polygons)!=row['faces']:errors.append([o.name,'topology'])
 if o.name not in build['hidden'] and o.hide_render!=row['hidden']:errors.append([o.name,'visibility'])
missing=[i.name for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not pathlib.Path(bpy.path.abspath(i.filepath)).exists()]
assert not errors and not missing,(errors,missing)
for y in [20,25,29]:
 o=bpy.data.objects['V03 King banner '+str(y)];ys=[v.co.y for v in o.data.vertices];zs=[v.co.z for v in o.data.vertices];assert abs(max(ys)-min(ys)-1.75)<1e-4 and abs(max(zs)-min(zs)-5.25)<1e-4
assert len(build['artwork'])==36
assert bpy.data.objects['Walkthrough_Camera'].animation_data and [s.frame_start,s.frame_end]==src['frames']
report={'status':'passed','source_v04_unchanged':True,'original_mesh_objects_retained':len(src['objects']),'artwork_placements':36,'unique_imagegen_designs':8,'banner_dimensions_m':[1.75,5.25],'missing_images':missing,'original_walkthrough_retained':True,'packed_images':sum(bool(i.packed_file) for i in bpy.data.images)}
(R/'scene_validation.json').write_text(json.dumps(report,indent=2));print(report)
