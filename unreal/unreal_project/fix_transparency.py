import unreal,pathlib,json
root=pathlib.Path(unreal.Paths.project_dir());sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
fixed=[]
for path in unreal.EditorAssetLibrary.list_assets('/Game/Campus/Maps',recursive=True):
 if not path.endswith(path.split('.')[-1]):continue
 if not isinstance(unreal.load_asset(path),unreal.World):continue
 sub.load_level(path.split('.')[0]);n=0
 for a in actors.get_all_level_actors():
  if isinstance(a,unreal.StaticMeshActor):
   c=a.static_mesh_component
   if any(m and 'glazing' in m.get_name().lower() for m in c.get_materials()):c.set_editor_property('disallow_nanite',True);n+=1
 sub.save_current_level();fixed.append({'map':path,'transparent_mesh_groups':n})
(root/'transparency_fix.json').write_text(json.dumps(fixed,indent=2))
