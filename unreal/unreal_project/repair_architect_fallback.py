"""Run in the full editor: rebuild the finish mesh with a complete RT fallback."""
import unreal,pathlib,json
root=pathlib.Path(unreal.Paths.project_dir())
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level('/Game/Campus/Maps/CampusCenter_Dusk_ArchitectFinishes_v03')
sub=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
assert sub is not None,'Requires full editor, not commandlet'
a=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Architect_Finishes_v02')
c=a.static_mesh_component;mesh=c.static_mesh
s=mesh.get_editor_property('nanite_settings')
s.enabled=True;s.fallback_relative_error=0.0;s.fallback_percent_triangles=1.0
s.fallback_target=unreal.NaniteFallbackTarget.PERCENT_TRIANGLES
sub.set_nanite_settings(mesh,s,True)
c.set_editor_property('disallow_nanite',False)
unreal.EditorAssetLibrary.save_loaded_asset(mesh)
levels.save_current_level()
(root.parent/'architect_finishes_v01/fallback_repair.json').write_text(json.dumps({'mesh':mesh.get_path_name(),'nanite_enabled':True,'fallback_percent_triangles':1.0,'fallback_relative_error':0.0,'component_disallow_nanite':False},indent=2))
unreal.log('ARCHITECT_FALLBACK_REBUILT')
unreal.SystemLibrary.quit_editor()
