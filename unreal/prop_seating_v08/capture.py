shots=json.loads((R/'shots.json').read_text())
capture_state={'i':0,'phase':0,'next':time.monotonic()+10}
def capture_tick(dt):
 s=capture_state
 if time.monotonic()<s['next']:return
 if s['i']>=len(shots):
  L.eject_pilot_level_actor();A.destroy_actor(s['cam']);unreal.unregister_slate_post_tick_callback(capture_handle);(R/'capture_done.txt').write_text(str(len(shots)));return
 name,pos,rot,fov=shots[s['i']]
 if s['phase']==0:
  if 'cam' not in s:s['cam']=A.spawn_actor_from_class(unreal.CameraActor,unreal.Vector(*pos))
  L.eject_pilot_level_actor()
  c=s['cam'];c.set_actor_location(unreal.Vector(*pos),False,False);c.set_actor_rotation(unreal.Rotator(pitch=rot[0],yaw=rot[1],roll=rot[2]),False);c.camera_component.set_field_of_view(fov);L.pilot_level_actor(c);s['phase']=1;s['next']=time.monotonic()+8
 elif s['phase']==1:
  s['task']=unreal.AutomationLibrary.take_high_res_screenshot(1600,900,str(R/(name+'.png')),camera=s['cam'],delay=0.0);s['phase']=2;s['next']=time.monotonic()+5;s['requested']=time.monotonic()
 else:
  if (R/(name+'.png')).exists():s['phase']=0;s['i']+=1;s['next']=time.monotonic()+2
  elif time.monotonic()-s['requested']>120:
   (R/'capture_failed.txt').write_text(name);unreal.unregister_slate_post_tick_callback(capture_handle)
  else:s['next']=time.monotonic()+5
capture_handle=unreal.register_slate_post_tick_callback(capture_tick)
