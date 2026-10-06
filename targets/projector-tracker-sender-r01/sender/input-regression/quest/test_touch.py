import unreal,pathlib,json,time
r=pathlib.Path(__file__).parent;L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
ctx=unreal.load_asset('/Game/Campus/ProjectorQA/IMC_ViveTriggerWalk')
rows=ctx.get_editor_property('default_key_mappings').get_editor_property('mappings')
touch={str(x.get_editor_property('key').get_editor_property('key_name')):x for x in rows if str(x.get_editor_property('key').get_editor_property('key_name')).startswith('OculusTouch_')}
assert len(rows)==10 and len(touch)==4
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ep=actors.spawn_actor_from_class(unreal.Character,unreal.Vector(0,0,1000))
ep.set_editor_property('auto_possess_player',unreal.AutoReceiveInput.PLAYER0)
ep.character_movement.gravity_scale=0
eh=actors.spawn_actor_from_class(unreal.load_class(None,'/Script/CampusCrowdFix.CampusViveTriggerWalk'),unreal.Vector())
eh.mapping_context=ctx;eh.left_action=unreal.load_asset('/Game/Campus/ViveTriggerWalkR01/IA_TriggerWalk_Left');eh.right_action=unreal.load_asset('/Game/Campus/ViveTriggerWalkR01/IA_TriggerWalk_Right')
# name,leftGrip,rightGrip,leftTrigger,rightTrigger,focus,leftTracked,rightTracked,count,walking
cases=[('startup-held',1,0,0,0,1,1,1,0,False),('neutral',0,0,0,0,1,1,1,0,False),('resting-squeeze',.5,0,0,0,1,1,1,0,False),('left-press',.8,0,0,0,1,1,1,1,False),('held',1,0,0,0,1,1,1,1,False),('partial-release-no-rearm',.54,0,0,0,1,1,1,1,False),('squeeze-again-no-repeat',.8,0,0,0,1,1,1,1,False),('release',.5,0,0,0,1,1,1,1,False),('right-press',0,.8,0,0,1,1,1,2,False),('release2',0,0,0,0,1,1,1,2,False),('both-suppressed',.8,.8,0,0,1,1,1,2,False),('one-held-after-both',.8,0,0,0,1,1,1,2,False),('neutral2',0,0,0,0,1,1,1,2,False),('focus-lost',.8,0,0,0,0,1,1,2,False),('refocus-held',.8,0,0,0,1,1,1,2,False),('release3',0,0,0,0,1,1,1,2,False),('tracking-lost',0,.8,0,0,1,1,0,2,False),('tracking-restored-held',0,.8,0,0,1,1,1,2,False),('release4',0,0,0,0,1,1,1,2,False),('left-after-rearm',.8,0,0,0,1,1,1,3,False),('trigger-neutral',0,0,0,0,1,1,1,3,False),('left-trigger',0,0,.7,0,1,1,1,3,True),('right-trigger',0,0,0,.7,1,1,1,3,True),('both-triggers',0,0,.7,.7,1,1,1,3,True),('trigger-focus-lost',0,0,.7,.7,0,1,1,3,False),('trigger-refocus-held',0,0,.7,.7,1,1,1,3,False),('trigger-release',0,0,0,0,1,1,1,3,False),('right-trigger-rearmed',0,0,0,.7,1,1,1,3,True),('final-neutral',0,0,0,0,1,1,1,3,False)]
report={'method':'Reopened saved context; real EnhancedInput injection with exact saved Touch modifiers and unchanged native helper; simulated focus/tracking, no XR session or hardware.','cases':[]}
state={'phase':'play','next':time.monotonic()+3,'i':0,'busy':False}
def finish():
 (r/'touch-validation.json').write_text(json.dumps(report,indent=2));unreal.unregister_slate_post_tick_callback(handle);L.editor_request_end_play();end=time.monotonic()+5
 def quit_tick(dt):
  if time.monotonic()>end:unreal.unregister_slate_post_tick_callback(qh);unreal.SystemLibrary.quit_editor()
 qh=unreal.register_slate_post_tick_callback(quit_tick)
def tick(dt):
 if state['busy'] or time.monotonic()<state['next']:return
 state['busy']=True
 try:
  now=time.monotonic()
  if state['phase']=='play':L.editor_request_begin_play();state.update(phase='init',next=now+8);return
  w=unreal.EditorLevelLibrary.get_game_world();pc=unreal.GameplayStatics.get_player_controller(w,0)
  if state['phase']=='init':
   assert pc
   pawn=unreal.GameplayStatics.get_player_character(w,0);assert pawn
   h=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.load_class(None,'/Script/CampusCrowdFix.CampusViveTriggerWalk'))[0]
   subs=[x for x in unreal.ObjectIterator(unreal.EnhancedInputLocalPlayerSubsystem) if x.get_outer().get_class()==unreal.LocalPlayer.static_class()];report['subsystems']=[x.get_path_name() for x in subs]
   assert len(subs)==1,report['subsystems'];sub=subs[0]
   assert sub;state.update(helper=h,sub=sub,phase='begin',next=now+1);return
  h=state['helper'];sub=state['sub'];name,lg,rg,lt,rt,focus,trackedL,trackedR,count,walking=cases[state['i']]
  if state['phase']=='begin':state.update(phase='sample',began=now,beforeYaw=pc.get_control_rotation().yaw,beforeCount=h.grip_turn_count)
  assert h.diagnostic_frame(0,False,0,False,bool(focus),bool(trackedL),bool(trackedR),pc.get_control_rotation().yaw)
  for key,value in [('OculusTouch_Left_Grip_Axis',lg),('OculusTouch_Right_Grip_Axis',rg),('OculusTouch_Left_Trigger_Axis',lt),('OculusTouch_Right_Trigger_Axis',rt)]:
   row=touch[key];sub.inject_input_vector_for_action(row.get_editor_property('action'),unreal.Vector(value,0,0),row.get_editor_property('modifiers'),[])
  if now-state['began']<.6:state['next']=now;return
  actual=h.grip_turn_count;delta=(pc.get_control_rotation().yaw-state['beforeYaw']+180)%360-180
  report['cases'].append({'name':name,'count':actual,'expected':count,'walking':h.walking,'expected_walking':walking,'grip_values':[h.left_grip_value,h.right_grip_value],'trigger_values':[h.left_value,h.right_value],'yaw_delta':delta,'pass':actual==count and h.walking==walking})
  state['i']+=1
  if state['i']==len(cases):h.diagnostic_stop();report['passed']=all(x['pass'] for x in report['cases']);finish();return
  state.update(phase='begin',next=now)
 except Exception as e:report['error']=repr(e);finish()
 finally:state['busy']=False
handle=unreal.register_slate_post_tick_callback(tick)
