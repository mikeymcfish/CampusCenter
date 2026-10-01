import bpy,json,pathlib,hashlib
O=pathlib.Path(__file__).parent;ROOT=pathlib.Path('C:/Users/mikef/Documents/Codex/2026-09-30/task/CampusCenter-new-plans')
m=json.loads((O/'replacement_manifest.json').read_text())
for name in ('Dark metal','V8 plain rubber','V8 plain sage upholstery','Brushed stainless hardware','V8 plain dark screen'):
 material=bpy.data.materials[name];bs=material.node_tree.nodes.get('Principled BSDF');values={key:bs.inputs[key].default_value[:] if key=='Base Color' else bs.inputs[key].default_value for key in ('Base Color','Metallic','Roughness')};material.node_tree.nodes.clear();bs=material.node_tree.nodes.new('ShaderNodeBsdfPrincipled');output=material.node_tree.nodes.new('ShaderNodeOutputMaterial');material.node_tree.links.new(bs.outputs['BSDF'],output.inputs['Surface'])
 for key,value in values.items():bs.inputs[key].default_value=value
renames={}
for ob in bpy.data.objects:
 if ob.name.endswith('.001') and ob.name.startswith(('RE07_','FA26_')):
  old=ob.name;ob.name=old[:-4];renames[old]=ob.name
for r in m['replacements']:r['parts']=[renames.get(n,n) for n in r['parts']]
for r in m['replacements']:
 for row in r['topology']:row['name']=renames.get(row['name'],row['name'])
m['native_central_actor_evidence']={'FA26_PH02_Fitness218_027':'StaticMeshActor_2035','FA26_PH02_Fitness218_029':'StaticMeshActor_2036','FA26_PH02_Fitness218_030':'StaticMeshActor_2037','source':'native-properties-r15.json; verify IDs in isolated integration map'}
bpy.ops.wm.save_as_mainfile(filepath=str(O/'CampusCenter_Equipment_Editable_EQ27_R01.blend'))
def export(path,obs):
 bpy.ops.object.select_all(action='DESELECT')
 for ob in obs:ob.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_yup=True,export_materials='EXPORT',export_extras=True,export_apply=True)
cols=[bpy.data.collections[r['id']] for r in m['replacements']]
export(O/'exports/Equipment_EQ27_R01_World.glb',[o for c in cols for o in c.objects])
for c in cols:export(O/'exports'/f'{c.name}_World.glb',list(c.objects))
sm=json.loads((ROOT/'downstream/furniture_art_v26_r01/fitness_support_patch_r01/source-manifest.json').read_text());used={n for r in m['replacements'] for n in r['replaces_objects']};complete=[bpy.data.objects[n] for n in sm['complete_group_membership'] if n not in used]
complete += [o for c in cols if int(c.name[-3:])<19 for o in c.objects]
export(O/'exports/R25_U218_Furniture_EQ27_R01_Complete.glb',complete)
m['complete_legacy_export_parts']=[o.name for o in complete]
m['exports']=[{'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted((O/'exports').glob('*.glb'))]
(O/'replacement_manifest.json').write_text(json.dumps(m,indent=2));print('FINALIZE_OK',len(complete))
