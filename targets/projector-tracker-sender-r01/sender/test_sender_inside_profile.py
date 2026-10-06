import unreal,json,time
from pathlib import Path
root=Path(__file__).parent
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
# Transient software fixture, never saved. Existing input/source/map assets are not edited.
cube=unreal.load_asset('/Engine/BasicShapes/Cube')
for x,z in [(-1000,0),(-1000,426.72)]:
    platform=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(x,-3800,z-10))
    platform.static_mesh_component.set_static_mesh(cube)
    platform.set_actor_scale3d(unreal.Vector(20,20,.2))
pawn_class=unreal.load_class(None,'/Game/FirstPerson/Blueprints/BP_FirstPersonCharacter.BP_FirstPersonCharacter_C')
p=actors.spawn_actor_from_class(pawn_class,unreal.Vector(-1000,-3800,100))
p.set_editor_property('auto_possess_player',unreal.AutoReceiveInput.PLAYER0)
state=dict(phase='play',next=time.monotonic()+2,index=0,busy=False)
report=dict(scope='Software PIE fixture using actual R29 pawn/camera and actual CharacterMovement floor; focus explicitly simulated; HMD/projector unverified.',cases=[])
cases=['ground','roomscale-tall-gym','upper','focus-loss','focus-recovery','unsupported']
def finish():
    (root/'sender-pie-inside-profile-validation.json').write_text(json.dumps(report,indent=2))
    unreal.unregister_slate_post_tick_callback(handle);level.editor_request_end_play()
    stop=time.monotonic()+5
    def quit_tick(dt):
        if time.monotonic()>stop:
            unreal.unregister_slate_post_tick_callback(qh);unreal.SystemLibrary.quit_editor()
    qh=unreal.register_slate_post_tick_callback(quit_tick)
def tick(dt):
    if state['busy'] or time.monotonic()<state['next']:return
    state['busy']=True
    try:
        now=time.monotonic()
        if state['phase']=='play':level.editor_request_begin_play();state.update(phase='init',next=now+8);return
        world=unreal.EditorLevelLibrary.get_game_world()
        pc=unreal.GameplayStatics.get_player_controller(world,0)
        pawn=unreal.GameplayStatics.get_player_pawn(world,0)
        if state['phase']=='init':
            assert -1100<pawn.get_actor_location().x<-900,pawn.get_actor_location()
            subsystem=next(s for s in unreal.ObjectIterator(unreal.CampusProjectorSender) if s.get_outer()==world)
            camera=pawn.get_components_by_class(unreal.CameraComponent)[0]
            original=unreal.Vector(*camera.get_editor_property('relative_location').to_tuple())
            state.update(subsystem=subsystem,camera=camera,original=original,phase='begin')
        name=cases[state['index']];subsystem=state['subsystem'];camera=state['camera']
        if state['phase']=='begin':
            subsystem.diagnostic_focus(name!='focus-loss')
            camera.set_relative_location(state['original'],False,True)
            if name=='roomscale-tall-gym':camera.set_world_location(camera.get_world_location()+unreal.Vector(123,-45,600),False,True)
            if name=='upper':pawn.set_actor_location(unreal.Vector(-1000,-3800,526.72),False,True)
            if name=='unsupported':pawn.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING)
            state.update(phase='sample',began=now,next=now+1.2)
            return
        camera_location=camera.get_world_location();manager=pc.player_camera_manager
        report['cases'].append(dict(name=name,start=state['began'],end=now,pawn=list(pawn.get_actor_location().to_tuple()),camera=list(camera_location.to_tuple()),manager=list(manager.get_camera_location().to_tuple()),yaw=manager.get_camera_rotation().yaw))
        state['index']+=1
        if state['index']==len(cases):finish();return
        state.update(phase='begin',next=now)
    except Exception as e:report['error']=repr(e);finish()
    finally:state['busy']=False
handle=unreal.register_slate_post_tick_callback(tick)
