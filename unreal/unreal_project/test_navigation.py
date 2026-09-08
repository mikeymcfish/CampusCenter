import unreal,json,pathlib,time,math
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
root=pathlib.Path(unreal.Paths.project_dir());rooms=json.loads((root.parent/'unreal_transfer/exports/rooms.json').read_text())
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);levels.load_level('/Game/Campus/Maps/CampusCenter');levels.editor_request_begin_play()
state={'start':time.monotonic(),'stage':-1,'next':time.monotonic()+12,'results':[],'walking':False}
def tick(dt):
 try:
  now=time.monotonic()
  if now-state['start']>150:raise RuntimeError('Navigation test timed out')
  world=unreal.EditorLevelLibrary.get_game_world()
  if not world:return
  char=unreal.GameplayStatics.get_player_character(world,0)
  if not char:return
  if state['walking']:char.add_movement_input(unreal.Vector(-1,0,0),1.0,False)
  if now<state['next']:return
  if state['stage']==-1:
   state['walk_start']=list(char.get_actor_location().to_tuple());state['walking']=True;state['stage']=0;state['next']=now+5;return
  if state['walking']:
   state['walking']=False;state['walk_end']=list(char.get_actor_location().to_tuple());state['walk_distance_cm']=math.dist(state['walk_start'],state['walk_end'])
  elif state['stage']>0:
   pos=list(char.get_actor_location().to_tuple());r=rooms[state['stage']-1];expected=r['p'][2]-77
   state['results'].append({'room':r['name'],'position_cm':pos,'expected_capsule_z':expected,'height_error_cm':pos[2]-expected,'floor_ok':abs(pos[2]-expected)<35})
  if state['stage']>=len(rooms):
   state['status']='passed' if all(r['floor_ok'] for r in state['results']) and state.get('walk_distance_cm',0)>300 else 'needs_review'
   (root/'navigation_test.json').write_text(json.dumps(state,indent=2));levels.editor_request_end_play();unreal.unregister_slate_post_tick_callback(handle);unreal.SystemLibrary.quit_editor();return
  r=rooms[state['stage']];p=r['p'];char.set_actor_location(unreal.Vector(p[0],p[1],p[2]-75),False,True);char.character_movement.stop_movement_immediately();state['stage']+=1;state['next']=now+3
 except Exception as e:
  (root/'navigation_test_error.txt').write_text(str(e));unreal.unregister_slate_post_tick_callback(handle);unreal.SystemLibrary.quit_editor()
handle=unreal.register_slate_post_tick_callback(tick)
