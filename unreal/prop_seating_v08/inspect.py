import unreal,json,pathlib
R=pathlib.Path(unreal.Paths.project_dir()).parent/'prop_seating_v08'
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert L.load_level('/Game/Campus/Maps/CampusCenter_StandardAssets_v07')
def vec(v):return [v.x,v.y,v.z]
rows=[]
for a in A.get_all_level_actors():
 o,e=a.get_actor_bounds(False)
 row={'label':a.get_actor_label(),'class':a.get_class().get_name(),'location':vec(a.get_actor_location()),'rotation':str(a.get_actor_rotation()),'scale':vec(a.get_actor_scale3d()),'center':vec(o),'extent':vec(e),'components':[]}
 for c in a.get_components_by_class(unreal.StaticMeshComponent):
  if c.static_mesh:row['components'].append({'name':c.get_name(),'mesh':c.static_mesh.get_path_name(),'materials':[m.get_path_name() if m else None for m in c.get_materials()]})
 rows.append(row)
(R/'actors.json').write_text(json.dumps(rows,indent=2))
(R/'assets.json').write_text(json.dumps(unreal.EditorAssetLibrary.list_assets('/Game',True),indent=2))
unreal.SystemLibrary.quit_editor()
