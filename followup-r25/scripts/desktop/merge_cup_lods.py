import bpy,pathlib,json,hashlib
from mathutils import Vector
ROOT=pathlib.Path(__file__).parent;SRC=pathlib.Path(r'C:\Users\mikef\Documents\Codex\2026-10-01\task-2\trophy_preflight\ready');OUT=ROOT/'combined_r01/trophies/cup_merged';OUT.mkdir(parents=True,exist_ok=True);records=[]
files=['SilverCup.glb','SilverCup_LOD1.glb','SilverCup_LOD2.glb'];expected=[23312,12750,5252]
source_hashes={f:hashlib.sha256((SRC/f).read_bytes()).hexdigest() for f in files};assert source_hashes['SilverCup.glb']=='00cf6e236841ff500a83f988bdeeed56915fb6c51e60c892f7ae8b9e967a0a65'
for index,f in enumerate(files):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(SRC/f));originals=[o for o in bpy.data.objects if o.type=='MESH'];assert len(originals)==5,len(originals)
 inventory=[{'name':o.name,'matrix':[list(row) for row in o.matrix_world],'materials':[s.material.name if s.material else None for s in o.material_slots],'uv_layers':len(o.data.uv_layers),'modifiers':[m.type for m in o.modifiers]} for o in originals]
 bpy.ops.object.select_all(action='DESELECT');copies=[]
 for o in originals:
  c=o.copy();c.data=o.data.copy();bpy.context.scene.collection.objects.link(c);c.select_set(True);copies.append(c);o.hide_render=True;o.hide_set(True)
 bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();ob=bpy.context.object;ob.name=f'SilverCup_Assembly_LOD{index}';bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);ob.data.calc_loop_triangles();tri=len(ob.data.loop_triangles);assert tri==expected[index],(tri,expected[index]);points=[ob.matrix_world@v.co for v in ob.data.vertices];bounds=[[min(p[k] for p in points) for k in range(3)],[max(p[k] for p in points) for k in range(3)]];assert abs(bounds[0][2])<1e-6 and abs(bounds[1][2]-.320)<.0001
 path=OUT/f'SilverCup_Assembly_LOD{index}.glb';bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_yup=True,export_materials='EXPORT',export_apply=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/f'SilverCup_Assembly_LOD{index}.blend'))
 records.append({'source':f,'source_sha256':source_hashes[f],'export':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'triangles':tri,'bounds_m':bounds,'source_parts':inventory,'merged_materials':[s.material.name for s in ob.material_slots],'uv_layers':len(ob.data.uv_layers),'operation':'Join duplicated objects, apply world transforms; no welding/remeshing/material baking/topology edits'})
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(path));meshes=[o for o in bpy.data.objects if o.type=='MESH'];assert len(meshes)==1;meshes[0].data.calc_loop_triangles();assert len(meshes[0].data.loop_triangles)==tri
assert all(hashlib.sha256((SRC/f).read_bytes()).hexdigest()==h for f,h in source_hashes.items());(OUT/'merge-validation.json').write_text(json.dumps({'blender':bpy.app.version_string,'records':records,'source_files_unchanged':True,'exports_reopened':True},indent=2));print('CUP_ASSEMBLY_THREE_LODS_VALIDATED')
