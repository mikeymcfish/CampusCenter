import unreal,pathlib,json
root=pathlib.Path(unreal.Paths.project_dir());sub=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);rows=[]
for p in unreal.EditorAssetLibrary.list_assets('/Game/Campus/Imported',recursive=True):
 m=unreal.load_asset(p)
 if not isinstance(m,unreal.StaticMesh):continue
 settings=m.get_editor_property('nanite_settings')
 old=settings.fallback_relative_error
 settings.fallback_relative_error=0.0;settings.fallback_percent_triangles=1.0
 settings.fallback_target=unreal.NaniteFallbackTarget.PERCENT_TRIANGLES
 sub.set_nanite_settings(m,settings,True);unreal.EditorAssetLibrary.save_loaded_asset(m)
 rows.append({'mesh':m.get_name(),'previous_error':old,'new_error':0,'fallback_triangles':1})
(root/'rt_geometry_v03.json').write_text(json.dumps(rows,indent=2))
