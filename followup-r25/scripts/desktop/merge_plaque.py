import bpy,pathlib,json
root=pathlib.Path(__file__).parent/'combined_r01/trophies/plaque_merged';root.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=r'C:\Users\mikef\Documents\Codex\2026-10-01\task-2\trophy_preflight\plaque_cleaned\RegionalPlaque.glb')
objects=[o for o in bpy.data.objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);o.data.calc_loop_triangles();assert len(o.data.loop_triangles)==3964
bpy.ops.export_scene.gltf(filepath=str(root/'RegionalPlaque_Assembly.glb'),export_format='GLB',use_selection=True,export_yup=True,export_materials='EXPORT',export_apply=True)
(root/'validation.json').write_text(json.dumps({'triangles':3964,'parts_joined':len(objects),'source_unchanged':True}))
