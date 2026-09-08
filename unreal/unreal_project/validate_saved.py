import unreal,json,pathlib
root=pathlib.Path(unreal.Paths.project_dir());levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level('/Game/Campus/Maps/CampusCenter')
allactors=actors.get_all_level_actors();meshes=[a for a in allactors if isinstance(a,unreal.StaticMeshActor)]
report={'mesh_groups':len(meshes),'review_cameras':len([a for a in allactors if a.get_actor_label().startswith('Review_')]),'missing_meshes':[],'missing_material_slots':[],'collision_groups':0,'students_groups':0,'maps':[],'sequences':[]}
for a in meshes:
 c=a.static_mesh_component
 if not c.static_mesh:report['missing_meshes'].append(a.get_actor_label())
 for i,m in enumerate(c.get_materials()):
  if m is None:report['missing_material_slots'].append([a.get_actor_label(),i])
 if str(c.get_collision_profile_name())=='BlockAll':report['collision_groups']+=1
 if a.actor_has_tag('Students'):report['students_groups']+=1
for p in unreal.EditorAssetLibrary.list_assets('/Game/Campus/Maps',recursive=True):report['maps'].append(str(p))
for p in unreal.EditorAssetLibrary.list_assets('/Game/Campus/Tours',recursive=True):report['sequences'].append(str(p))
report['status']='passed' if report['mesh_groups']==233 and report['review_cameras']==9 and not report['missing_meshes'] and not report['missing_material_slots'] else 'needs_review'
(root/'saved_validation.json').write_text(json.dumps(report,indent=2))
assert report['status']=='passed',report
