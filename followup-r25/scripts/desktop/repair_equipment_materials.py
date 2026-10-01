import unreal,pathlib,json,re
R=pathlib.Path(__file__).parent/'combined_r01';E=unreal.EditorAssetLibrary;L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);target='/Game/Campus/Maps/CampusCenter_FA26_Desktop_R24_CombinedReview';assert L.load_level(target);contract=json.loads((R/'equipment-contract.json').read_text());rows=[]
def norm(v):return re.sub(r'[^a-z0-9]','',re.sub(r'_\d+$','',str(v).lower().removeprefix('slot_')))
actors={a.get_name():a for a in A.get_all_level_actors()}
for row in contract['rows']:
 a=actors[row['actor_name']];c=a.static_mesh_component;n=c.static_mesh;slots=n.get_editor_property('static_materials');bindings={norm(x['gltf_name']):x['native_material'] for x in row['bindings']};mapped=[]
 for i,s in enumerate(slots):
  path=bindings[norm(s.material_slot_name)];mat=unreal.load_asset(path);assert mat;s.set_editor_property("material_interface",mat);slots[i]=s;mapped.append(mat)
 n.set_editor_property('static_materials',slots);c.set_editor_property('override_materials',mapped);assert E.save_loaded_asset(n,only_if_is_dirty=False)
 actual=[s.material_interface.get_path_name() for s in n.get_editor_property('static_materials')];expected=[m.get_path_name() for m in mapped];assert actual==expected;assert [c.get_material(i).get_path_name() for i in range(c.get_num_materials())]==expected;rows.append({'actor':a.get_name(),'slot_names':[str(s.material_slot_name) for s in slots],'native_materials':expected,'verified_asset_and_component':True})
assert L.save_current_level();actors.clear();del a,c;assert L.load_level(target)
for row in rows:
 a=next(a for a in A.get_all_level_actors() if a.get_name()==row['actor']);c=a.static_mesh_component;assert [c.get_material(i).get_path_name() for i in range(c.get_num_materials())]==row['native_materials'];assert [s.material_interface.get_path_name() for s in c.static_mesh.get_editor_property('static_materials')]==row['native_materials']
(R/'native-material-binding-repair.json').write_text(json.dumps(rows,indent=2));unreal.SystemLibrary.quit_editor()

