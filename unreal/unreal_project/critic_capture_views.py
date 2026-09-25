"""Independent read-only capture set for the art-director review agent."""
import unreal
import pathlib
import json
import time
import os

unreal.EditorPythonScripting.set_keep_python_script_alive(True)
project = pathlib.Path(unreal.Paths.project_dir())
round_number = os.environ.get('CRITIC_ROUND', '1')
out = project.parent / 'architect_finishes_v01' / ('critic_round_' + round_number)
out.mkdir(parents=True, exist_ok=True)
unreal.log('CRITIC_CAPTURE_OUTPUT ' + str(out))
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level('/Game/Campus/Maps/CampusCenter_Dusk_ArchitectFinishes_v03')
unreal.SystemLibrary.execute_console_command(None, 'viewmode lit')
unreal.SystemLibrary.execute_console_command(None, 'r.HighResScreenshotDelay 64')

# Positions are chosen independently of the review and walkthrough cameras.
views = [
    ('01_commons_wide', (1410,-1530,172), (5,-143,0), 78),
    ('02_k_wall_close', (630,-2460,215), (13,-152,0), 68),
    ('03_cri_wide', (830,-210,172), (1,-100,0), 78),
    ('04_blue_floor_close', (900,-950,160), (-28,-90,0), 60),
    ('05_ceiling_close', (750,-2200,170), (78,-110,0), 68),
    ('06_upper_commons', (1200,-2100,520), (-5,-151,0), 78),
]
shots = []
for label, p, r, fov in views:
    c = actors.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*p), unreal.Rotator(pitch=r[0], yaw=r[1], roll=r[2]))
    c.set_actor_label('Critic_View_' + label)
    c.camera_component.set_field_of_view(float(fov))
    shots.append((c, out / (label + '.png')))

state = {'index': 0, 'task': None, 'next': time.monotonic()+75, 'started': time.monotonic(), 'retries': 0}
def tick(dt):
    now = time.monotonic()
    if now-state['started'] > 900:
        (out/'capture_failed.txt').write_text('Timed out at view %s' % state['index'])
        unreal.unregister_slate_post_tick_callback(handle)
        unreal.SystemLibrary.quit_editor()
        return
    if state['task'] is not None:
        if not state['task'].is_task_done(): return
        _, path = shots[state['index']-1]
        if not path.exists():
            state['task'] = None
            if state['retries'] >= 2:
                (out/'capture_failed.txt').write_text('No file after retries: '+str(path))
                unreal.unregister_slate_post_tick_callback(handle)
                unreal.SystemLibrary.quit_editor()
                return
            state['retries'] += 1
            state['index'] -= 1
            state['next'] = now+25
            return
        state['task'] = None
        state['retries'] = 0
        state['next'] = now+5
    if now < state['next']: return
    if state['index'] == len(shots):
        (out/'capture_complete.json').write_text(json.dumps({'map':'CampusCenter_Dusk_ArchitectFinishes_v03','images':[str(p) for _,p in shots]},indent=2))
        unreal.unregister_slate_post_tick_callback(handle)
        unreal.SystemLibrary.quit_editor()
        return
    cam,path = shots[state['index']]
    state['index'] += 1
    state['next'] = now+25
    state['task'] = unreal.AutomationLibrary.take_high_res_screenshot(1280,720,str(path),camera=cam,delay=10.0)

handle = unreal.register_slate_post_tick_callback(tick)
