import unreal,pathlib,json
root=pathlib.Path(unreal.Paths.project_dir());exec((root/'validate_saved.py').read_text())
ed=unreal.MaterialEditingLibrary;checks=[]
for path in unreal.EditorAssetLibrary.list_assets('/Game/Campus/PolishV03/Materials',recursive=True)+unreal.EditorAssetLibrary.list_assets('/Game/Campus/PolishV02/Materials',recursive=True):
 m=unreal.load_asset(path)
 if not isinstance(m,unreal.Material):continue
 base=ed.get_material_property_input_node(m,unreal.MaterialProperty.MP_BASE_COLOR);assert base,path
 checks.append({'material':path,'base_color_connected':True})
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);maps=[]
for path in unreal.EditorAssetLibrary.list_assets('/Game/Campus/Maps',recursive=True):
 assert levels.load_level(path.split('.')[0])
 pp=[a for a in actors.get_all_level_actors() if isinstance(a,unreal.PostProcessVolume)]
 assert pp,path
 s=pp[0].settings;assert abs(s.auto_exposure_bias-.2)<.001,(path,s.auto_exposure_bias)
 maps.append(path)
assert len(maps)==12,len(maps)
(root/'validation_v03.json').write_text(json.dumps({'status':'passed','materials':checks,'maps':maps,'layout_validation':'saved_validation.json'},indent=2))
