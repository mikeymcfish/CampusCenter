import unreal,json,pathlib,time,math
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
root=pathlib.Path(unreal.Paths.project_dir());route=json.loads((root.parent/'unreal_transfer/source/walkthrough_route.json').read_text())['keys']
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);levels.load_level('/Game/Campus/Maps/CampusCenter');levels.editor_request_begin_play()
state={'start':time.monotonic(),'index':1,'last_progress':time.monotonic(),'best':1e9,'stuck':[],'reached':[]}
def done():
 state['status']='passed' if not state['stuck'] else 'needs_review';(root/'route_movement_test.json').write_text(json.dumps(state,indent=2));levels.editor_request_end_play();unreal.unregister_slate_post_tick_callback(handle);unreal.SystemLibrary.quit_editor()
def tick(dt):
 now=time.monotonic()
 if now-state['start']<12:return
 world=unreal.EditorLevelLibrary.get_game_world()
 if not world:return
 char=unreal.GameplayStatics.get_player_character(world,0)
 if not char:return
 if now-state['start']>480:state['stuck'].append({'reason':'overall timeout','index':state['index']});done();return
 if state['index']>=len(route):done();return
 k=route[state['index']];p=k['p'];goal=unreal.Vector(p[0]*100,-p[1]*100,p[2]*100-77);pos=char.get_actor_location();dist=math.hypot(goal.x-pos.x,goal.y-pos.y)
 if dist<25 and abs(goal.z-pos.z)<55:
  state['reached'].append(state['index']);state['index']+=1;state['best']=1e9;state['last_progress']=now;return
 if dist<state['best']-10:state['best']=dist;state['last_progress']=now
 if now-state['last_progress']>7:
  state['stuck'].append({'index':state['index'],'label':k['label'],'position':list(pos.to_tuple()),'goal':list(goal.to_tuple()),'distance':dist})
  char.set_actor_location(goal+unreal.Vector(0,0,2),False,True);state['index']+=1;state['best']=1e9;state['last_progress']=now;return
 char.character_movement.set_editor_property('max_walk_speed',250.0)
 if dist>1:char.add_movement_input(unreal.Vector((goal.x-pos.x)/dist,(goal.y-pos.y)/dist,0),1,False)
handle=unreal.register_slate_post_tick_callback(tick)
