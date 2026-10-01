import unreal,json,pathlib,time,math
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
OUT=pathlib.Path(__file__).parent;L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert L.load_level('/Game/Campus/Maps/CampusCenter_Vive_EQ27_R07_OpenXR')
state={'phase':'play','next':time.monotonic()+12,'start':time.monotonic(),'case':0,'busy':False}
# Each transition exercises the real EnhancedInput key pipeline and CharacterMovement.
cases=[('neutral',1,0,False,0,False,True,True,True,0,False),('left_hold',1.2,1,False,0,False,True,True,True,0,True),('release',1,0,False,0,False,True,True,True,0,False),('right_click',1.2,0,False,0,True,True,True,True,0,True),('both_hands',1.2,1,True,1,True,True,True,True,0,True),('left_release_right_holds',1,0,False,1,True,True,True,True,0,True),('focus_loss',1,0,False,1,True,False,True,True,0,False),('refocus_held',1,0,False,1,True,True,True,True,0,False),('neutral_rearm',1,0,False,0,False,True,True,True,0,False),('yaw90',1.2,1,True,0,False,True,True,True,90,True),('disconnect',1,1,True,0,False,True,False,True,90,False),('reconnect_held',1,1,True,0,False,True,True,True,90,False),('final_release',1,0,False,0,False,True,True,True,90,False)]
raw_cases=list(cases);cases=raw_cases+[(name+'_OpenXRInjection',duration,la,lc,ra,rc,focus,lt,rt,yaw,expected) for name,duration,la,lc,ra,rc,focus,lt,rt,yaw,expected in raw_cases]
report={'method':'PIE real raw Vive input keys via development-only diagnostic flag, real EnhancedInput and collision-aware CharacterMovement. Focus/tracking simulated explicitly; hardware unverified.','tests':[]}
def finish():
 (OUT/'input-validation.json').write_text(json.dumps(report,indent=2));unreal.unregister_slate_post_tick_callback(handle);L.editor_request_end_play();unreal.SystemLibrary.quit_editor()
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
   report['movement']={'speed':pawn.character_movement.max_walk_speed,'pawn':pawn.get_class().get_path_name(),'radius':pawn.capsule_component.get_scaled_capsule_radius()};state['phase']='begin'
  case=cases[state['case']];name,duration,la,lc,ra,rc,focused,lt,rt,yaw,expected=case
  if state['phase']=='begin':
   # Initialize all probes in open Commons; no walking uses teleport.
   pawn.character_movement.stop_movement_immediately();pawn.set_actor_location(unreal.Vector(-3100,-2380,496),False,True)
   state['row']={'name':name,'expected_walking':expected,'samples':[]};state['began']=now;state['phase']='run'
  if name.endswith('_OpenXRInjection'):
   origin=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor) if a.get_class().get_path_name()=='/Script/CampusCrowdFix.CampusViveXROrigin')
   assert helper.diagnostic_frame(0,False,0,False,focused,lt,rt,yaw)
   assert origin.diagnostic_inject(max(la,float(lc)),max(ra,float(rc)))
  else:assert helper.diagnostic_frame(la,lc,ra,rc,focused,lt,rt,yaw)
  if now-state['began']>.3:
   vel=pawn.get_velocity();state['row']['samples'].append({'walking':helper.walking,'scale':helper.last_input_scale,'left':helper.left_value,'right':helper.right_value,'velocity':vel.to_tuple(),'speed_horizontal':math.hypot(vel.x,vel.y),'location':pawn.get_actor_location().to_tuple()})
  if now-state['began']>=duration:
   row=state['row'];row['pass']=bool(row['samples']) and all(s['walking']==expected and s['scale']==(1 if expected else 0) for s in row['samples']);report['tests'].append(row);state['case']+=1
   if state['case']==len(cases):helper.diagnostic_stop();report['passed']=all(x['pass'] for x in report['tests']);finish();return
   state['phase']='begin'
 except Exception as e:report['error']=repr(e);finish()
 finally:state['busy']=False
handle=unreal.register_slate_post_tick_callback(tick)
