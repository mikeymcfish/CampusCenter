import unreal,json,pathlib,time,math
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
OUT=pathlib.Path(__file__).parent;L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert L.load_level('/Game/Campus/Maps/CampusCenter_Vive_R29_TrophyTrainerGymCorrections_r02')
state={'phase':'play','next':time.monotonic()+12,'start':time.monotonic(),'case':0,'busy':False}
# Each transition exercises the real EnhancedInput key pipeline and CharacterMovement.
cases=[('neutral',1,0,False,0,False,True,True,True,0,False),('keyboard_only',1.2,0,False,0,False,True,True,True,0,False),('keyboard_plus_trigger',1.2,1,True,0,False,True,True,True,0,True),('trigger_release_keyboard_continues',1.2,0,False,0,False,True,True,True,0,False),('keyboard_release',1,0,False,0,False,True,True,True,0,False)]
report={'method':'PIE real raw Vive input keys via development-only diagnostic flag, real EnhancedInput and collision-aware CharacterMovement. Focus/tracking simulated explicitly; hardware unverified.','tests':[]}
def finish():
 (OUT/'keyboard-validation.json').write_text(json.dumps(report,indent=2));unreal.unregister_slate_post_tick_callback(handle);L.editor_request_end_play();quit_at=time.monotonic()+5
 def exit_tick(dt):
  if time.monotonic()>=quit_at:unreal.unregister_slate_post_tick_callback(exit_handle);unreal.SystemLibrary.quit_editor()
 exit_handle=unreal.register_slate_post_tick_callback(exit_tick)
def tick(dt):
 if state['busy'] or time.monotonic()<state['next']:return
 state['busy']=True
 try:
  now=time.monotonic()
  if now-state['start']>240:raise RuntimeError('timeout')
  if state['phase']=='play':L.editor_request_begin_play();state['phase']='init';state['next']=now+15;return
  world=unreal.EditorLevelLibrary.get_game_world();pawn=unreal.GameplayStatics.get_player_character(world,0);assert pawn
  helper=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor) if a.get_class().get_path_name()=='/Script/CampusCrowdFix.CampusViveTriggerWalk')
  if state['phase']=='init':
   pc=unreal.GameplayStatics.get_player_controller(world,0);report['controller_class']=pc.get_class().get_path_name()
   report['movement']={'speed':pawn.character_movement.max_walk_speed,'pawn':pawn.get_class().get_path_name(),'radius':pawn.capsule_component.get_scaled_capsule_radius()};state['phase']='begin'
  case=cases[state['case']];name,duration,la,lc,ra,rc,focused,lt,rt,yaw,expected=case
  if state['phase']=='begin':
   unreal.GameplayStatics.get_player_controller(world,0).set_control_rotation(unreal.Rotator(pitch=0,yaw=0,roll=0))
   helper.diagnostic_key('W',name in ['keyboard_only','keyboard_plus_trigger','trigger_release_keyboard_continues'])
   # Initialize all probes in open Commons; no walking uses teleport.
   pawn.character_movement.stop_movement_immediately();pawn.set_actor_location(unreal.Vector(-3100,-2380,496),False,True)
   state['row']={'name':name,'expected_walking':expected,'samples':[]};state['began']=now;state['phase']='run'
  assert helper.diagnostic_frame(la,lc,ra,rc,focused,lt,rt,yaw)
  if now-state['began']>.3:
   vel=pawn.get_velocity();state['row']['samples'].append({'walking':helper.walking,'scale':helper.last_input_scale,'left':helper.left_value,'right':helper.right_value,'velocity':vel.to_tuple(),'speed_horizontal':math.hypot(vel.x,vel.y),'location':pawn.get_actor_location().to_tuple()})
  if now-state['began']>=duration:
   row=state['row'];row['pass']=bool(row['samples']) and all(s['walking']==expected and s['scale']==(1 if expected else 0) for s in row['samples']);row['max_speed']=max(x['speed_horizontal'] for x in row['samples']);row['pass']=row['pass'] and row['max_speed']<=report['movement']['speed']+.01 and (row['max_speed']>1 if 'keyboard' in name and name!='keyboard_release' else True);report['tests'].append(row);state['case']+=1
   if state['case']==len(cases):helper.diagnostic_stop();report['passed']=all(x['pass'] for x in report['tests']);finish();return
   state['phase']='begin'
 except Exception as e:report['error']=repr(e);finish()
 finally:state['busy']=False
handle=unreal.register_slate_post_tick_callback(tick)
