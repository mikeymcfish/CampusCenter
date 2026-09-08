import bpy,json,pathlib,hashlib
R=pathlib.Path(__file__).parent;s=bpy.context.scene;r=json.loads((R/'build_report.json').read_text())
assert hashlib.sha256((R/'Source_Copy.blend').read_bytes()).hexdigest()==r['source_sha256']
assert hashlib.sha256((R.parent/'cycles_studio_v01/Campus_Center_Cycles_Studio.blend').read_bytes()).hexdigest()==r['source_sha256']
assert sum(o.type=='MESH' for o in s.objects)==3422
assert bpy.data.objects['Walkthrough_Camera'].animation_data
missing=[i.name for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not pathlib.Path(bpy.path.abspath(i.filepath)).exists()]
assert not missing
assert s.cycles.samples==256 and s.render.resolution_x==1920
assert r['paint_faces']>0
report={'status':'passed','source_v01_unchanged':True,'meshes':3422,'painted_faces':r['paint_faces'],'painted_objects':len(r['paint_objects']),'walkthrough_retained':True,'missing_images':missing,'packed_images':sum(bool(i.packed_file) for i in bpy.data.images)}
(R/'scene_validation.json').write_text(json.dumps(report,indent=2));print(report)
