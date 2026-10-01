import unreal,pathlib,json
E=unreal.EditorAssetLibrary;r=pathlib.Path(__file__).parent/'combined_r01';rows=[]
for asset in E.list_assets('/Game/Campus/EquipmentEQ27R01/Runtime',recursive=True):
 n=unreal.load_asset(asset)
 if not isinstance(n,unreal.StaticMesh):continue
 settings=n.get_editor_property('nanite_settings');settings.set_editor_property('enabled',False);n.set_editor_property('nanite_settings',settings);assert E.save_loaded_asset(n,only_if_is_dirty=False);rows.append(n.get_path_name())
(r/'nanite-isolation-test.json').write_text(json.dumps({'new_meshes_only':rows,'baseline_meshes_and_renderer_unchanged':True,'purpose':'Isolate visual artifacts in new equipment meshes'},indent=2));unreal.SystemLibrary.quit_editor()
