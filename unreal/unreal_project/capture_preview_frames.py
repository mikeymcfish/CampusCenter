import unreal,json,pathlib,time,math
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
root=pathlib.Path(unreal.Paths.project_dir());out=root/'PreviewVerified';out.mkdir(exist_ok=True)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Campus/Maps/CampusCenter')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
camera=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Guided_Tour_Camera')
samples=json.loads((root.parent/'unreal_transfer/exports/transfer_manifest.json').read_text())['camera_samples']
state={'index':0,'next':time.monotonic()+15,'task':None,'busy':False,'started':time.monotonic()}
def tick(dt):
 if state['busy']:return
 now=time.monotonic()
 if now-state['started']>1000:unreal.SystemLibrary.quit_editor();return
 if state['task'] is not None:
  if not state['task'].is_task_done():return
  state['task']=None;state['next']=now+.12
 if now<state['next']:return
 i=state['index']
 if i>=240:
  (root/'preview_render_result.json').write_text(json.dumps({'success':True,'files':240,'method':'settled camera screenshots along exported route','fps':12}));unreal.unregister_slate_post_tick_callback(handle);unreal.SystemLibrary.quit_editor();return
 sample=samples[round(i/239*(len(samples)-1))];d=sample['dir']
 camera.set_actor_location(unreal.Vector(*sample['p']),False,False)
 camera.set_actor_rotation(unreal.Rotator(pitch=math.degrees(math.atan2(d[2],math.hypot(d[0],d[1]))),yaw=math.degrees(math.atan2(d[1],d[0])),roll=0),False)
 state['busy']=True;state['index']+=1;state['next']=now+10
 state['task']=unreal.AutomationLibrary.take_high_res_screenshot(640,360,str(out/('frame_%04d.png'%i)),camera=camera,delay=.4)
 state['busy']=False
handle=unreal.register_slate_post_tick_callback(tick)
