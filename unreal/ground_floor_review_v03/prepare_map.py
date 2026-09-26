import unreal,pathlib,json,hashlib
R=pathlib.Path(__file__).parent;root=pathlib.Path(unreal.Paths.project_dir())
E=unreal.EditorAssetLibrary;L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
source='/Game/Campus/Maps/CampusCenter_ArchitectDecals_v04';target='/Game/Campus/Maps/CampusCenter_GroundFloorReview_v05'
assert not E.does_asset_exist(target),'New cycle must start from an isolated map'
assert E.duplicate_asset(source,target);assert L.load_level(target)
rows=[];lights=[]
for a in A.get_all_level_actors():
 if isinstance(a,unreal.StaticMeshActor):
  c=a.static_mesh_component;p,e=a.get_actor_bounds(False)
  rows.append({'label':a.get_actor_label(),'mesh':c.static_mesh.get_path_name() if c.static_mesh else None,'position':list(a.get_actor_location().to_tuple()),'rotation':list(a.get_actor_rotation().to_tuple()),'scale':list(a.get_actor_scale3d().to_tuple()),'center':list(p.to_tuple()),'extent':list(e.to_tuple()),'materials':[c.get_material(i).get_path_name() if c.get_material(i) else None for i in range(c.get_num_materials())]})
 if isinstance(a,unreal.Light):
  c=a.light_component;lights.append({'label':a.get_actor_label(),'class':a.get_class().get_name(),'position':list(a.get_actor_location().to_tuple()),'intensity':c.intensity})
(R/'baseline_actors.json').write_text(json.dumps(rows,indent=2));(R/'baseline_lights.json').write_text(json.dumps(lights,indent=2))
sourcefile=root/'Content/Campus/Maps/CampusCenter_ArchitectDecals_v04.umap'
(R/'preflight.json').write_text(json.dumps({'source':source,'target':target,'source_sha256':hashlib.sha256(sourcefile.read_bytes()).hexdigest(),'mesh_actors':len(rows)},indent=2))
L.save_current_level();unreal.log('GROUND_FLOOR_PREPARED')
