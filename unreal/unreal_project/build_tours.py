import unreal,json,pathlib,math
root=pathlib.Path(unreal.Paths.project_dir());exports=root.parent/'unreal_transfer/exports'
samples=json.loads((exports/'transfer_manifest.json').read_text())['camera_samples'];rooms=json.loads((exports/'rooms.json').read_text())
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels.load_level('/Game/Campus/Maps/CampusCenter')
def rot(d):return [math.degrees(math.atan2(d[2],math.hypot(d[0],d[1]))),math.degrees(math.atan2(d[1],d[0])),0]
camera=actors.spawn_actor_from_class(unreal.CameraActor,unreal.Vector(*samples[0]['p']));camera.set_actor_label('Guided_Tour_Camera');camera.camera_component.set_field_of_view(78)
def sequence(name,rate,frames):
 seq=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,'/Game/Campus/Tours',unreal.LevelSequence,unreal.LevelSequenceFactoryNew())
 seq.set_display_rate(unreal.FrameRate(rate,1));seq.set_playback_start(0);seq.set_playback_end(frames)
 binding=seq.add_possessable(camera);track=binding.add_track(unreal.MovieScene3DTransformTrack);section=track.add_section();section.set_range(0,frames);channels=section.get_all_channels()
 last_yaw=None
 for i in range(frames):
  if rate==24 and i%6 and i!=frames-1:continue
  idx=min(len(samples)-1,round(i/(frames-1)*(len(samples)-1)));sample=samples[idx];pitch,yaw,roll=rot(sample['dir'])
  if last_yaw is not None:
   while yaw-last_yaw>180:yaw-=360
   while yaw-last_yaw<-180:yaw+=360
  last_yaw=yaw
  vals=sample['p']+[roll,pitch,yaw,1,1,1]
  for c,v in zip(channels,vals):c.add_key(unreal.FrameNumber(i),float(v))
 cut=seq.add_track(unreal.MovieSceneCameraCutTrack);cs=cut.add_section();cs.set_range(0,frames);bid=unreal.MovieSceneObjectBindingID();bid.set_editor_property('guid',binding.get_id());cs.set_camera_binding_id(bid)
 unreal.EditorAssetLibrary.save_loaded_asset(seq);return seq
full=sequence('Campus_Guided_Tour',24,8994);preview=sequence('Campus_Preview_20s',12,240)
levels.save_current_level()
# Separate launch maps share mesh assets; only starting pose / visibility differs.
char=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Campus_Explorer')
start=next(a for a in actors.get_all_level_actors() if isinstance(a,unreal.PlayerStart))
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for i,r in enumerate(rooms):
 p=r['p'];location=unreal.Vector(p[0],p[1],p[2]-77+2);angles=rot(r['dir']);rotation=unreal.Rotator(pitch=0,yaw=angles[1],roll=0)
 char.set_actor_location(location,False,False);char.set_actor_rotation(rotation,False);start.set_actor_location(location,False,False);start.set_actor_rotation(rotation,False)
 unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/Campus/Maps/Room_%02d'%i)
levels.load_level('/Game/Campus/Maps/CampusCenter');world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for a in actors.get_all_level_actors():
 if a.actor_has_tag('Students'):a.set_actor_hidden_in_game(True)
unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/Campus/Maps/Campus_NoStudents')
levels.load_level('/Game/Campus/Maps/CampusCenter');world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
tour=actors.spawn_actor_from_class(unreal.LevelSequenceActor,unreal.Vector());tour.set_actor_label('Automatic_Guided_Tour');tour.set_sequence(full);settings=tour.get_editor_property('playback_settings');settings.set_editor_property('auto_play',True);settings.set_editor_property('loop_count',unreal.MovieSceneSequenceLoopCount(-1));tour.set_editor_property('playback_settings',settings)
camera=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Guided_Tour_Camera')
bid=unreal.MovieSceneObjectBindingID();bid.set_editor_property('guid',full.get_bindings()[0].get_id())
entry=unreal.MovieSceneBindingOverrideData();entry.set_editor_property('object_binding_id',bid);entry.set_editor_property('object',camera);entry.set_editor_property('overrides_default',True)
tour.get_editor_property('binding_overrides').set_editor_property('binding_data',[entry])
unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/Campus/Maps/Campus_GuidedTour')
(root/'tour_setup.json').write_text(json.dumps({'full_sequence':full.get_path_name(),'preview_sequence':preview.get_path_name(),'rooms':rooms},indent=2))
unreal.log('CAMPUS_TOURS_SAVED')
