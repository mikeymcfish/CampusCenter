import unreal
import pathlib
import json
import time

unreal.EditorPythonScripting.set_keep_python_script_alive(True)
root = pathlib.Path(unreal.Paths.project_dir()).parent / 'architect_finishes_v01'
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level('/Game/Campus/Maps/CampusCenter_Dusk_ArchitectFinishes_v03')
unreal.SystemLibrary.execute_console_command(None, 'r.HighResScreenshotDelay 64')
shots = []
for label, position, rotation in [
    ('Commons_K_Unreal_v03_final', (1410,-1530,172), (5,-143,0)),
    ('CRI_Unreal_v03_final', (830,-210,172), (1,-100,0)),
]:
    cam = actors.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*position), unreal.Rotator(pitch=rotation[0], yaw=rotation[1], roll=rotation[2]))
    cam.set_actor_label('Temporary_' + label)
    cam.camera_component.set_field_of_view(78.0)
    shots.append((cam, root / (label + '.png')))
state = {'index': 0, 'task': None, 'next': time.monotonic() + 90, 'started': time.monotonic(), 'retries': 0}

def tick(dt):
    now = time.monotonic()
    if now - state['started'] > 600:
        (root / 'unreal_capture_timeout.txt').write_text(str(state))
        unreal.SystemLibrary.quit_editor()
        return
    if state['task'] is not None:
        if not state['task'].is_task_done():
            return
        _, last_file = shots[state['index'] - 1]
        if not last_file.exists():
            state['task'] = None
            if state['retries'] >= 2:
                (root / 'unreal_capture_failed_v03.txt').write_text('No screenshot file after three attempts: ' + str(last_file))
                unreal.unregister_slate_post_tick_callback(handle)
                unreal.SystemLibrary.quit_editor()
                return
            state['retries'] += 1
            state['index'] -= 1
            state['next'] = now + 30
            return
        state['task'] = None
        state['retries'] = 0
        state['next'] = now + 8
    if now < state['next']:
        return
    if state['index'] >= len(shots):
        (root / 'unreal_capture_complete_v03_final.json').write_text(json.dumps({'shots': [str(p) for _, p in shots]}))
        unreal.unregister_slate_post_tick_callback(handle)
        unreal.SystemLibrary.quit_editor()
        return
    cam, filename = shots[state['index']]
    state['index'] += 1
    state['next'] = now + 20
    state['task'] = unreal.AutomationLibrary.take_high_res_screenshot(1200, 675, str(filename), camera=cam, delay=12.0)

handle = unreal.register_slate_post_tick_callback(tick)
