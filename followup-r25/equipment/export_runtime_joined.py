import bpy,json,pathlib,hashlib
O=pathlib.Path(__file__).parent;m=json.loads((O/'replacement_manifest.json').read_text());deps=bpy.context.evaluated_depsgraph_get();runtime=[]
def export(name,names,actor):
 bpy.ops.object.select_all(action='DESELECT');copies=[]
 for n in names:
  orig=bpy.data.objects[n];mesh=bpy.data.meshes.new_from_object(orig.evaluated_get(deps));c=bpy.data.objects.new(name+'_part',mesh);bpy.context.scene.collection.objects.link(c);c.matrix_world=orig.matrix_world.copy();c.select_set(True);copies.append(c)
 bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();ob=bpy.context.object;ob.name=name;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);ob['target_actor_label']=actor;ob['collision_contract']='CTF_USE_COMPLEX_AS_SIMPLE; QUERY_AND_PHYSICS';ob['dimension_status']='Estimated mechanics; traced approved footprints'
 path=O/'exports'/f'{name}_RuntimeJoined.glb';bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_yup=True,export_materials='EXPORT',export_extras=True,export_apply=True)
 runtime.append({'file':path.name,'actor_label':actor,'source_parts':names,'mesh_count':1,'transform':'Identity; world positions baked in meters','material_policy':'Bind by named slots from material_compatibility.json, not prior raw slot indices'})
 bpy.data.objects.remove(ob,do_unlink=True)
export('R25_U218_Furniture_EQ27_R01',m['complete_legacy_export_parts'],'R25_U218_Furniture')
for num in ('027','029','030'):
 r=next(r for r in m['replacements'] if r['id'].endswith('_'+num));export(r['id'],r['parts'],'FA26_PH02_Fitness218_'+num)
m['runtime_joined_exports']=runtime;m['exports']=[{'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted((O/'exports').glob('*.glb'))]
(O/'replacement_manifest.json').write_text(json.dumps(m,indent=2));print('RUNTIME_JOINED_OK',len(runtime))
