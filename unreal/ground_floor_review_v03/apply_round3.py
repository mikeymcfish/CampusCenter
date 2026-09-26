"""Apply ranked round-two fixes, then save only isolated review map."""
import pathlib,json,unreal
R=pathlib.Path(__file__).parent
previous=(R/'round2_changes.json').read_bytes()
for script in ['refine_round2.py','refine_surfaces.py','refine_corridor_oak.py','refine_architect_oak.py']:
    path=R/script;exec(compile(path.read_text(),str(path),'exec'),{'__file__':str(path),'__name__':'__main__'})
(R/'round3_rebuild_changes.json').write_bytes((R/'round2_changes.json').read_bytes())
(R/'round2_changes.json').write_bytes(previous)
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert L.load_level('/Game/Campus/Maps/CampusCenter_GroundFloorReview_v05')
levels={'109':1800,'111':2300,'118':1600,'119':2500,'120':2800,'124':2600,'125':3300,'126':2600,'127':2600,'128':2200,'129':4000}
report={'lights':[],'environment_relocations':[]}
for a in A.get_all_level_actors():
    name=a.get_actor_label()
    if isinstance(a,unreal.RectLight) and name.startswith('GF_Light_'):
        c=a.light_component;c.set_editor_property('temperature',5200.)
        key=name.removeprefix('GF_Light_')
        if key in levels:c.set_intensity(levels[key])
        if key.startswith('Gym_'):c.set_intensity(17500)
        if key.startswith('130_'):c.set_intensity(2300)
        report['lights'].append({'label':name,'lumens':c.intensity,'temperature':5200})
    if isinstance(a,unreal.RectLight) and (name=='V8_Classroom_area' or name.startswith('Wet_room_')):a.light_component.set_editor_property('temperature',5600.)
    if name=='Site_Tree_08_00':
        before=list(a.get_actor_location().to_tuple());a.set_actor_location(unreal.Vector(-400,-5400,-5),False,False)
        report['environment_relocations'].append({'actor':name,'before':before,'after':[-400,-5400,-5],'reason':'Exterior tree intersected gym court and ceiling'})
# Soft architectural gallery fill; shadow-casting, below the suspended entry panels.
name='GF_CRI_GalleryFill';a=next((a for a in A.get_all_level_actors() if a.get_actor_label()==name),None)
if not a:a=A.spawn_actor_from_class(unreal.RectLight,unreal.Vector(640,-360,365),unreal.Rotator(pitch=-90,yaw=0,roll=0));a.set_actor_label(name)
c=a.light_component;c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_editor_property('intensity_units',unreal.LightUnits.LUMENS);c.set_intensity(2300);c.set_cast_shadows(True)
for key,value in {'source_width':450.,'source_height':350.,'attenuation_radius':850.,'use_temperature':True,'temperature':5600.}.items():c.set_editor_property(key,value)
name='GF_StairLowerFill';a=next((a for a in A.get_all_level_actors() if a.get_actor_label()==name),None)
if not a:a=A.spawn_actor_from_class(unreal.RectLight,unreal.Vector(440,-860,310),unreal.Rotator(pitch=-28,yaw=180,roll=0));a.set_actor_label(name)
c=a.light_component;c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_editor_property('intensity_units',unreal.LightUnits.LUMENS);c.set_intensity(1800);c.set_cast_shadows(True)
for key,value in {'source_width':200.,'source_height':100.,'attenuation_radius':650.,'use_temperature':True,'temperature':5600.}.items():c.set_editor_property(key,value)
L.save_current_level();(R/'round3_changes.json').write_text(json.dumps(report,indent=2));unreal.log('GROUND_FLOOR_ROUND3_SAVED')
