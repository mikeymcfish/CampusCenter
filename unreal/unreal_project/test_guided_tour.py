import unreal,json,pathlib,time,math
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
root=pathlib.Path(unreal.Paths.project_dir());levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
levels.load_level('/Game/Campus/Maps/Campus_GuidedTour');levels.editor_request_begin_play()
state={'next':time.monotonic()+12,'samples':[]}
def tick(dt):
 if time.monotonic()<state['next']:return
 try:
  world=unreal.EditorLevelLibrary.get_game_world();pc=unreal.GameplayStatics.get_player_controller(world,0)
  cam=pc.get_view_target();state['samples'].append({'target':cam.get_name(),'position':list(cam.get_actor_location().to_tuple())})
  if len(state['samples'])<2:state['next']=time.monotonic()+5;return
  state['distance_cm']=math.dist(state['samples'][0]['position'],state['samples'][1]['position'])
  state['status']='passed' if state['distance_cm']>30 and all('Camera' in s['target'] for s in state['samples']) else 'needs_review'
  (root/'guided_tour_test.json').write_text(json.dumps(state,indent=2))
 except Exception as e:(root/'guided_tour_test.json').write_text(json.dumps({'status':'error','error':str(e)}))
 levels.editor_request_end_play();unreal.unregister_slate_post_tick_callback(handle);unreal.SystemLibrary.quit_editor()
handle=unreal.register_slate_post_tick_callback(tick)
