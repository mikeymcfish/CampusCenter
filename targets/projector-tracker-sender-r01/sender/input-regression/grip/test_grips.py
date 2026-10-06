import unreal,pathlib,json,time,math
r=pathlib.Path(__file__).parent;unreal.EditorPythonScripting.set_keep_python_script_alive(True);L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert L.load_level('/Game/Campus/Maps/CampusCenter_Vive_R29_TrophyTrainerGymCorrections_r02')
# name,left,right,focus,leftTracked,rightTracked,expected cumulative snap count,expected last direction
cases=[('startup-neutral',0,0,1,1,1,0,0),('left-press',1,0,1,1,1,1,-30),('left-held-no-repeat',1,0,1,1,1,1,-30),('release',0,0,1,1,1,1,-30),('right-press',0,1,1,1,1,2,30),('right-held-no-repeat',0,1,1,1,1,2,30),('release2',0,0,1,1,1,2,30),('both-suppressed',1,1,1,1,1,2,30),('one-held-after-both',1,0,1,1,1,2,30),('neutral-rearm',0,0,1,1,1,2,30),('left-after-release',1,0,1,1,1,3,-30),('focus-lost',0,1,0,1,1,3,-30),('focus-recovered-held',0,1,1,1,1,3,-30),('release3',0,0,1,1,1,3,-30),('right-after-refocus',0,1,1,1,1,4,30),('tracking-lost',1,0,1,0,1,4,30),('tracking-recovered-held',1,0,1,1,1,4,30),('release4',0,0,1,1,1,4,30),('left-after-retracking',1,0,1,1,1,5,-30),('final-release',0,0,1,1,1,5,-30)]
report={'map':'R29 current source, sender opt-in enabled','hardware_tested':False,'cases':[]};state={'phase':'play','next':time.monotonic()+10,'start':time.monotonic(),'i':0,'busy':False}
def finish():
 (r/'grip-validation.json').write_text(json.dumps(report,indent=2));unreal.unregister_slate_post_tick_callback(handle);L.editor_request_end_play();quit_at=time.monotonic()+5
 def exit_tick(dt):
  if time.monotonic()>=quit_at:unreal.unregister_slate_post_tick_callback(exit_handle);unreal.SystemLibrary.quit_editor()
 exit_handle=unreal.register_slate_post_tick_callback(exit_tick)
def tick(dt):
 if state['busy'] or time.monotonic()<state['next']:return
 state['busy']=True
 try:
  now=time.monotonic();assert now-state['start']<200
  if state['phase']=='play':L.editor_request_begin_play();state['phase']='init';state['next']=now+15;return
  w=unreal.EditorLevelLibrary.get_game_world();pawn=unreal.GameplayStatics.get_player_character(w,0);pc=unreal.GameplayStatics.get_player_controller(w,0);assert pawn
  helper=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Actor) if a.get_class().get_path_name()=='/Script/CampusCrowdFix.CampusViveTriggerWalk')
  if state['phase']=='init':
   report['helper_tick_enabled']=helper.is_actor_tick_enabled(); report['helper_class']=helper.get_class().get_path_name(); unreal.log('GRIP_HELPER_TICK '+str(report['helper_tick_enabled']))
   pawn.set_actor_location(unreal.Vector(-3100,-2380,496),False,True);pawn.character_movement.stop_movement_immediately();state['phase']='begin';state['next']=now+1;return
  row=cases[state['i']];name,left,right,focus,lt,rt,count,direction=row
  if state['phase']=='begin':
   state['before_yaw']=pc.get_control_rotation().yaw;state['before_count']=helper.grip_turn_count;state['camera_before']=pc.player_camera_manager.get_camera_location();state['phase']='sample';state['began']=now
  assert helper.diagnostic_frame(0,False,0,False,bool(focus),bool(lt),bool(rt),pc.get_control_rotation().yaw)
  assert helper.diagnostic_grips(bool(left),bool(right))
  if now-state['began']<.8:state['next']=now+.1;return
  current=helper.grip_turn_count;delta=(pc.get_control_rotation().yaw-state['before_yaw']+180)%360-180;expected_delta=direction if count>state['before_count'] else 0
  cam=pc.player_camera_manager.get_camera_location();pivot_drift=math.hypot(cam.x-state['camera_before'].x,cam.y-state['camera_before'].y)
  good=current==count and helper.last_grip_turn_degrees==direction and abs(delta-expected_delta)<.1 and pivot_drift<1
  report['cases'].append({'name':name,'expected_count':count,'actual_count':current,'control_yaw_delta':delta,'expected_delta':expected_delta,'horizontal_head_pivot_drift_cm':pivot_drift,'left_grip':helper.left_grip_value,'right_grip':helper.right_grip_value,'pass':good});state['i']+=1
  if state['i']==len(cases):helper.diagnostic_grips(False,False);helper.diagnostic_stop();report['passed']=all(x['pass'] for x in report['cases']);finish();return
  state['phase']='begin';state['next']=now+.1
 except Exception as e:report['error']=repr(e);finish()
 finally:state['busy']=False
handle=unreal.register_slate_post_tick_callback(tick)
