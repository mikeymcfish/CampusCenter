import unreal,pathlib,json
R=pathlib.Path(__file__).parent
for name in ['refine_architecture.py','refine_round4.py']:
 exec(compile((R/name).read_text(),str(R/name),'exec'))
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
for a in A.get_all_level_actors():
 if a.get_actor_label()=='Architect_Commons_SoftFill':a.light_component.set_intensity(2600)
 if isinstance(a,unreal.DirectionalLight):a.light_component.set_editor_property('light_source_angle',1.25)
name='DD_Commons_WallFill';a=next((a for a in A.get_all_level_actors() if a.get_actor_label()==name),None)
if not a:a=A.spawn_actor_from_class(unreal.RectLight,unreal.Vector(800,-2320,540),unreal.Rotator(pitch=0,yaw=180,roll=0));a.set_actor_label(name)
c=a.light_component;c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_intensity(700);c.set_cast_shadows(False);c.set_editor_property('source_width',1000.);c.set_editor_property('source_height',600.);c.set_editor_property('attenuation_radius',2000.);c.set_editor_property('use_temperature',True);c.set_editor_property('temperature',5600.)
L.save_current_level();unreal.log('ROUND4_SAVED')
