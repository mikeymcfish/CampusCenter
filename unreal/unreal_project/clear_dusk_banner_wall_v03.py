"""Remove only the three existing full-height wall graphics from the finish map."""
import unreal
import json
import pathlib

root = pathlib.Path(unreal.Paths.project_dir()).parent / 'architect_finishes_v01'
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level('/Game/Campus/Maps/CampusCenter_Dusk_ArchitectFinishes_v03')
names = {'King_FullHeight_V5_Banner_20', 'King_FullHeight_V5_Banner_25', 'King_FullHeight_V5_Banner_29'}
found = [a for a in actors.get_all_level_actors() if a.get_actor_label() in names]
assert {a.get_actor_label() for a in found} == names, [a.get_actor_label() for a in found]
report = []
for actor in found:
    report.append({'label': actor.get_actor_label(), 'class': actor.get_class().get_name()})
    assert actors.destroy_actor(actor)
assert levels.save_current_level()
assert not any(a.get_actor_label() in names for a in actors.get_all_level_actors())
(root / 'banner_wall_replacement_v03.json').write_text(json.dumps({'removed_from_finish_map': report}, indent=2))
unreal.log('BANNER_WALL_CLEARED ' + str(report))
