import unreal,json,pathlib,math
root=pathlib.Path(unreal.Paths.project_dir());levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels.load_level('/Game/Campus/Maps/CampusCenter')
cls=unreal.EditorAssetLibrary.load_blueprint_class('/Game/FirstPerson/Blueprints/BP_FirstPersonCharacter')
char=actors.spawn_actor_from_class(cls,unreal.Vector(2200,-1207,90),unreal.Rotator(yaw=180));char.set_actor_label('Campus_Explorer');char.set_editor_property('auto_possess_player',unreal.AutoReceiveInput.PLAYER0)
char.capsule_component.set_capsule_size(24,88)
char.character_movement.set_editor_property('max_walk_speed',140.0);char.character_movement.set_editor_property('max_step_height',32.0)
report={'components':[],'materials':[]}
for c in char.get_components_by_class(unreal.ActorComponent):
 report['components'].append({'name':c.get_name(),'class':c.get_class().get_name()})
 if isinstance(c,unreal.SkeletalMeshComponent):c.set_hidden_in_game(True)
 if isinstance(c,unreal.CameraComponent):
  c.set_field_of_view(78.0)
  c.attach_to_component(char.capsule_component,'',unreal.AttachmentRule.KEEP_RELATIVE,unreal.AttachmentRule.KEEP_RELATIVE,unreal.AttachmentRule.KEEP_RELATIVE,False)
  c.set_relative_location(unreal.Vector(0,0,77),False,False)
  report['camera']=c.get_name()
for p in unreal.EditorAssetLibrary.list_assets('/Game/Campus/Imported',recursive=True):
 a=unreal.load_asset(p)
 if isinstance(a,unreal.MaterialInterface):report['materials'].append({'name':a.get_name(),'path':p,'class':a.get_class().get_name()})
levels.save_current_level()
(root/'navigation_setup.json').write_text(json.dumps(report,indent=2,default=str))
unreal.log('CAMPUS_NAVIGATION_SAVED')
