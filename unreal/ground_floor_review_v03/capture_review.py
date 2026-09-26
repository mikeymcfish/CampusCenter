"""Independent read-only capture set for the art-director review agent."""
import unreal
import pathlib
import json
import time
import os

unreal.EditorPythonScripting.set_keep_python_script_alive(True)
project = pathlib.Path(unreal.Paths.project_dir())
round_number = os.environ.get('CRITIC_ROUND', '1')
out = project.parent / 'ground_floor_review_v03' / ('critic_round_' + round_number)
out.mkdir(parents=True, exist_ok=True)
unreal.log('CRITIC_CAPTURE_OUTPUT ' + str(out))
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level('/Game/Campus/Maps/CampusCenter_GroundFloorReview_v05')
unreal.SystemLibrary.execute_console_command(None, 'viewmode lit')
unreal.SystemLibrary.execute_console_command(None, 'r.HighResScreenshotDelay 64')

# Positions are chosen independently of the review and walkthrough cameras.
manifest=json.loads((project.parent/'ground_floor_review_v03/coverage_manifest.json').read_text(encoding='utf-8-sig'))
(out/'coverage_manifest.json').write_text(json.dumps(manifest,indent=2))
views=[(v['name'],v['position'],v['rotation'],v['fov']) for v in manifest['views']]
shots = []
for label, p, r, fov in views:
    c = actors.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*p), unreal.Rotator(pitch=r[0], yaw=r[1], roll=r[2]))
    c.set_actor_label('Critic_View_' + label)
    c.camera_component.set_field_of_view(float(fov))
    shots.append((c, out / (label + '.png')))

state = {'index': 0, 'phase':'position', 'next':time.monotonic()+60, 'started':time.monotonic()}
def tick(dt):
    now=time.monotonic()
    if now-state['started']>max(1200,len(shots)*45):
        (out/'capture_failed.txt').write_text(str(state))
        unreal.unregister_slate_post_tick_callback(handle);unreal.SystemLibrary.quit_editor();return
    if now<state['next']:return
    if state['index']==len(shots):
        missing=[str(p) for _,p in shots if not p.exists()]
        (out/('capture_failed.json' if missing else 'capture_complete.json')).write_text(json.dumps({'map':'CampusCenter_GroundFloorReview_v05','images':[str(p) for _,p in shots],'missing':missing},indent=2))
        unreal.unregister_slate_post_tick_callback(handle);unreal.SystemLibrary.quit_editor();return
    cam,path=shots[state['index']]
    if state['phase']=='position':
        state['phase']='capture';state['next']=now+6
        unreal.log('CRITIC_POSITION '+str(path))
        levels.pilot_level_actor(cam)
    elif state['phase']=='capture':
        state['requested']=now
        state['phase']='verify';state['next']=now+3
        unreal.log('CRITIC_REQUEST '+str(path))
        state['task']=unreal.AutomationLibrary.take_high_res_screenshot(1600,900,str(path),delay=0.0)
    elif path.exists() and path.stat().st_size>10000:
        unreal.log('CRITIC_VERIFIED '+str(path))
        state['index']+=1;state['phase']='position';state['next']=now+.5
        levels.eject_pilot_level_actor()
    else:
        if now-state['requested']>90:
            (out/'capture_failed.txt').write_text('Screenshot not written: '+str(path))
            unreal.unregister_slate_post_tick_callback(handle);unreal.SystemLibrary.quit_editor();return
        state['next']=now+5
handle=unreal.register_slate_post_tick_callback(tick)
