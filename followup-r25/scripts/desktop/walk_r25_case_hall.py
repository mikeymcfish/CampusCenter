import unreal,pathlib,json,time,math,hashlib
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
ROOT=pathlib.Path(__file__).parent;OUT=ROOT/'combined_r01/r25-case-hall-walking';OUT.mkdir(exist_ok=True);REF=pathlib.Path(r'C:\Users\mikef\Documents\Codex\2026-09-30\task\CampusCenter-new-plans\downstream\shared_v25_r01');L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
rows={v['name']:v for v in json.loads((REF/'accepted-source-doors-and-floors.json').read_text())['rows']};rows.update({n:{'name':n,'bounds_m':v['bounds_m']} for n,v in json.loads((REF/'accepted-source-object-bounds.json').read_text())['objects'].items()})
cases=[{'zone':'AthleticsHall','name':'CaseFront_Northbound','start':(-2720,-2490),'end':(-2720,-1990),'floor_cm':0},{'zone':'AthleticsHall','name':'CaseFront_Southbound','start':(-2720,-1990),'end':(-2720,-2490),'floor_cm':0}]
maps=[('before','/Game/Campus/Maps/CampusCenter_FA26_Desktop_R22_ReceptionSlides'),('after','/Game/Campus/Maps/CampusCenter_FA26_Desktop_R25_CombinedReview')]
report={'maps':{},'cases':cases,'method':'Actual baseline Character Movement and capsule; teleports initialize probes; walking uses add_movement_input. Existing twelve source-door probes plus two fitness aisles. No project/map save.','limits':'Not full route/headset/manufacturer clearance certification.'};state={'map':0,'case':0,'phase':'load','next':time.monotonic(),'busy':False,'start':time.monotonic(),'last':0}
def flush(): (OUT/'validation.json').write_text(json.dumps(report,indent=2))
def log(s):
 with (OUT/'progress.txt').open('a') as f:f.write(s+'\n')
def physics_probes(world,pawn):
 result=[]
 for i,x in enumerate([-3587.3783,-3363.0913,-3139.9426,-2916.7940,-2693.6455]):
  start=(x,-2720,570);end=(x,-2760,570)
  raw=unreal.SystemLibrary.line_trace_single_by_profile(world,unreal.Vector(*start),unreal.Vector(*end),'BlockAll',False,[pawn],unreal.DrawDebugTrace.NONE,True)
  hit=next((v for v in raw if isinstance(v,unreal.HitResult)),None) if isinstance(raw,(tuple,list)) else raw;v=hit.to_tuple() if hit else None
  result.append({'name':f'Rack{i+1}_interior_opening_simple_query','start':start,'end':end,'blocking':bool(v and v[0]),'actor':v[9].get_actor_label() if v and v[9] else None,'pass':not bool(v and v[0]),'trace_complex':False})
 start=(-4284,-2818,520);end=(-4284,-2818,426)
 raw=unreal.SystemLibrary.line_trace_single_by_profile(world,unreal.Vector(*start),unreal.Vector(*end),'BlockAll',False,[pawn],unreal.DrawDebugTrace.NONE,True);hit=next((v for v in raw if isinstance(v,unreal.HitResult)),None) if isinstance(raw,(tuple,list)) else raw;v=hit.to_tuple() if hit else None
 result.append({'name':'Treadmill_deck_blocks_simple_query','blocking':bool(v and v[0]),'actor':v[9].get_actor_label() if v and v[9] else None,'pass':bool(v and v[0] and v[9] and v[9].get_actor_label()=='R25_U218_Furniture'),'trace_complex':False})
 return result
def end():
 flush();unreal.unregister_slate_post_tick_callback(handle);L.editor_request_end_play();unreal.SystemLibrary.quit_editor()
def tick(dt):
 if state['busy'] or time.monotonic()<state['next']:return
 state['busy']=True
 try:
  now=time.monotonic();label,mapname=maps[state['map']]
  if now-state['start']>900:report['error']='Timeout';end();return
  if state['phase']=='load':assert L.load_level(mapname);state['phase']='play';state['next']=now+15;log('Load '+label);return
  if state['phase']=='play':L.editor_request_begin_play();state['phase']='init';state['next']=now+25;return
  world=unreal.EditorLevelLibrary.get_game_world();assert world;pawn=unreal.GameplayStatics.get_player_character(world,0);assert pawn;mov=pawn.character_movement;cap=pawn.capsule_component
  if state['phase']=='init':
   report['maps'][label]={'map':mapname,'pawn':pawn.get_class().get_path_name(),'radius_cm':cap.get_scaled_capsule_radius(),'half_height_cm':cap.get_scaled_capsule_half_height(),'step_height_cm':mov.get_editor_property('max_step_height'),'speed_cm_s':mov.get_editor_property('max_walk_speed'),'physics_probes':physics_probes(world,pawn),'tests':[]};state['phase']='start'
  case=cases[state['case']]
  if state['phase']=='start':
   mov.stop_movement_immediately();pawn.consume_movement_input_vector();pawn.set_actor_location(unreal.Vector(case['start'][0],case['start'][1],case['floor_cm']+cap.get_scaled_capsule_half_height()+5),False,True);state['row']={**case,'samples':[]};state['phase']='settle';state['next']=now+1.5;return
  if state['phase']=='settle':state['row']['settled']=pawn.get_actor_location().to_tuple();state['began']=now;state['phase']='walk'
  if state['phase']=='walk':
   pos=pawn.get_actor_location();dx=case['end'][0]-pos.x;dy=case['end'][1]-pos.y;dist=math.hypot(dx,dy)
   if now-state['last']>0.2:state['row']['samples'].append(pos.to_tuple());state['last']=now
   if dist<20 or now-state['began']>5:
    mov.stop_movement_immediately();pawn.consume_movement_input_vector();row=state['row'];row.update({'final':pos.to_tuple(),'distance_to_goal_cm':dist,'reached':dist<20,'elapsed_s':now-state['began']});report['maps'][label]['tests'].append(row);flush();log(label+' '+case['name']+' reached='+str(row['reached']));state['case']+=1
    if state['case']==len(cases):
     L.editor_request_end_play();state['map']+=1;state['case']=0
     if state['map']==len(maps):
      b={x['name']:x for x in report['maps']['before']['tests']};a=report['maps']['after']['tests'];report['regressions']=[x['name'] for x in a if b[x['name']]['reached'] and not x['reached']];end();return
     state['phase']='load';state['next']=now+8;return
    state['phase']='start';state['next']=now+0.5;return
   pawn.add_movement_input(unreal.Vector(dx/dist,dy/dist,0),1,True)
 except Exception as e:report['error']=repr(e);log('ERROR '+repr(e));end()
 finally:state['busy']=False
handle=unreal.register_slate_post_tick_callback(tick)



