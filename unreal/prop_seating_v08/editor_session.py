import unreal,pathlib,json,time,traceback
R=pathlib.Path(unreal.Paths.project_dir()).parent/'prop_seating_v08'
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert L.load_level('/Game/Campus/Maps/CampusCenter_StandardAssets_v07')
state={'after':time.monotonic()+30}
def tick(dt):
 if time.monotonic()<state['after']:return
 p=R/'command.py'
 if p.exists():
  code=p.read_text();p.unlink()
  try:exec(compile(code,str(p),'exec'),globals());(R/'command_done.txt').write_text('OK')
  except: (R/'command_done.txt').write_text(traceback.format_exc())
 state['after']=time.monotonic()+1
handle=unreal.register_slate_post_tick_callback(tick)
(R/'ready.txt').write_text('ready')
