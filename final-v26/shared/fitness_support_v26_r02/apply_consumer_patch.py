import unreal,pathlib,json,hashlib
# Consumer supplies RELEASE_ROOT, BASE_MAP and NEW_MAP explicitly.
root=pathlib.Path(RELEASE_ROOT);m=json.loads((root/'manifest.json').read_text());E=unreal.EditorAssetLibrary;L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not E.does_asset_exist(NEW_MAP);assert E.duplicate_asset(BASE_MAP,NEW_MAP);assert L.load_level(NEW_MAP)
a=[x for x in A.get_all_level_actors() if x.get_actor_label()==m['actor_label']];assert len(a)==1;a=a[0];c=a.static_mesh_component;assert c.static_mesh.get_path_name() in m['allowed_old_meshes'];before=(a.get_actor_location().to_tuple(),a.get_actor_scale3d().to_tuple(),a.get_actor_enable_collision(),str(c.get_collision_enabled()))
n=unreal.load_asset(m['new_mesh']);assert n;assert n.get_editor_property('body_setup').get_editor_property('collision_trace_flag')==unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE;c.set_static_mesh(n)
for i,s in enumerate(m['materials']):
 material=unreal.load_asset(s['path']);assert material and material.get_base_material().get_editor_property('used_with_nanite');c.set_material(i,material)
assert L.save_current_level();assert L.load_level(NEW_MAP);a=next(x for x in A.get_all_level_actors() if x.get_actor_label()==m['actor_label']);c=a.static_mesh_component;assert c.static_mesh.get_path_name()==m['new_mesh'];assert before==(a.get_actor_location().to_tuple(),a.get_actor_scale3d().to_tuple(),a.get_actor_enable_collision(),str(c.get_collision_enabled()))
assert [c.get_material(i).get_path_name() for i in range(c.get_num_materials())]==[x['path'] for x in m['materials']]
print('FITNESS_SUPPORT_PATCH_SAVED',NEW_MAP)
