"""Independent read-only capture set for the art-director review agent."""
import unreal
import pathlib
import json
import time
import os

unreal.EditorPythonScripting.set_keep_python_script_alive(True)
project = pathlib.Path(unreal.Paths.project_dir())
round_number = os.environ.get('CRITIC_ROUND', '1')
out = project.parent / 'decal_update_v02' / ('critic_round_' + round_number)
out.mkdir(parents=True, exist_ok=True)
unreal.log('CRITIC_CAPTURE_OUTPUT ' + str(out))
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level('/Game/Campus/Maps/CampusCenter_ArchitectDecals_v04')
unreal.SystemLibrary.execute_console_command(None, 'viewmode lit')
unreal.SystemLibrary.execute_console_command(None, 'r.HighResScreenshotDelay 64')

# Positions are chosen independently of the review and walkthrough cameras.
views = [
 ('01_art_gallery_wide',(-590,-1050,168),(0,-90,0),92),
 ('02_art_gallery_detail',(-819,-1430,173),(0,-90,0),65),
 ('03_art_gallery_oblique',(-75,-1190,170),(0,-142,0),76),
 ('04_trophy_shelf_wide',(-2990,-2305,162),(0,0,0),108),
 ('05_trophy_shelf_detail',(-2875,-2200,215),(-3,0,0),62),
 ('06_trophy_shelf_oblique',(-2850,-1760,165),(0,-62,0),76),
 ('07_commons_wide',(1410,-1530,172),(5,-143,0),78),
 ('08_k_wall_close',(630,-2460,215),(13,-152,0),68),
 ('09_ceiling_detail',(750,-2200,170),(78,-110,0),68),
 ('10_floor_detail',(900,-950,160),(-28,-90,0),60),
]
shots = []
for label, p, r, fov in views:
    c = actors.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*p), unreal.Rotator(pitch=r[0], yaw=r[1], roll=r[2]))
    c.set_actor_label('Critic_View_' + label)
    c.camera_component.set_field_of_view(float(fov))
    shots.append((c, out / (label + '.png')))

state = {'index': 0, 'phase':'position', 'next':time.monotonic()+75, 'started':time.monotonic()}
def tick(dt):
    now=time.monotonic()
    if now-state['started']>900:
        (out/'capture_failed.txt').write_text(str(state))
        unreal.unregister_slate_post_tick_callback(handle);unreal.SystemLibrary.quit_editor();return
    if now<state['next']:return
    if state['index']==len(shots):
        missing=[str(p) for _,p in shots if not p.exists()]
        (out/('capture_failed.json' if missing else 'capture_complete.json')).write_text(json.dumps({'map':'CampusCenter_ArchitectDecals_v04','images':[str(p) for _,p in shots],'missing':missing},indent=2))
        unreal.unregister_slate_post_tick_callback(handle);unreal.SystemLibrary.quit_editor();return
    cam,path=shots[state['index']]
    if state['phase']=='position':
        state['phase']='capture';state['next']=now+12
        unreal.log('CRITIC_POSITION '+str(path))
        levels.pilot_level_actor(cam)
    elif state['phase']=='capture':
        state['requested']=now
        state['phase']='verify';state['next']=now+12
        unreal.log('CRITIC_REQUEST '+str(path))
        state['task']=unreal.AutomationLibrary.take_high_res_screenshot(1600,900,str(path),delay=0.0)
    elif path.exists() and path.stat().st_size>10000:
        unreal.log('CRITIC_VERIFIED '+str(path))
        state['index']+=1;state['phase']='position';state['next']=now+2
        levels.eject_pilot_level_actor()
    else:
        if now-state['requested']>90:
            (out/'capture_failed.txt').write_text('Screenshot not written: '+str(path))
            unreal.unregister_slate_post_tick_callback(handle);unreal.SystemLibrary.quit_editor();return
        state['next']=now+5
handle=unreal.register_slate_post_tick_callback(tick)
