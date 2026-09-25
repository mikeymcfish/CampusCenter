"""Import the isolated wall/ceiling/floor finish layer into a separate walkable map."""
import unreal
import pathlib
import json

root = pathlib.Path(unreal.Paths.project_dir())
source_map = '/Game/Campus/Maps/CampusCenter_Dusk'
target_map = '/Game/Campus/Maps/CampusCenter_Dusk_ArchitectFinishes_v03'
asset_dir = '/Game/Campus/ArchitectFinishesV02'
glb = root.parent / 'architect_finishes_v01' / 'Architect_Finishes_v02.glb'
assert glb.is_file(), str(glb)

ed = unreal.EditorAssetLibrary
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not ed.does_asset_exist(target_map):
    assert ed.duplicate_asset(source_map, target_map)
assert levels.load_level(target_map)

meshes = [unreal.load_asset(p) for p in ed.list_assets(asset_dir, recursive=True)] if ed.does_directory_exist(asset_dir) else []
meshes = [a for a in meshes if isinstance(a, unreal.StaticMesh)]
if not meshes:
    task = unreal.AssetImportTask()
    task.filename = str(glb)
    task.destination_path = asset_dir
    task.automated = True
    task.save = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    meshes = [unreal.load_asset(p) for p in ed.list_assets(asset_dir, recursive=True)]
    meshes = [a for a in meshes if isinstance(a, unreal.StaticMesh)]
assert len(meshes) == 1, [a.get_path_name() for a in meshes]
mesh = meshes[0]

existing = [a for a in actors.get_all_level_actors() if a.get_actor_label() == 'Architect_Finishes_v02']
assert len(existing) <= 1
actor = existing[0] if existing else actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, 0))
actor.set_actor_label('Architect_Finishes_v02')
actor.set_folder_path('Architecture/Architect_Finishes_v02')
actor.tags = ['Architecture', 'Architect_Finishes_v02']
component = actor.static_mesh_component
component.set_static_mesh(mesh)
component.set_mobility(unreal.ComponentMobility.STATIC)
component.set_collision_profile_name('NoCollision')
assert levels.save_current_level()

b = mesh.get_bounds()
report = {
    'map': target_map,
    'mesh': mesh.get_path_name(),
    'mesh_bounds_cm': {'origin': list(b.origin.to_tuple()), 'extent': list(b.box_extent.to_tuple())},
    'actor_count': len(actors.get_all_level_actors()),
    'furniture_actors': len([a for a in actors.get_all_level_actors() if isinstance(a, unreal.StaticMeshActor) and a.get_actor_label().startswith('Furniture_')]),
    'finish_actors': len([a for a in actors.get_all_level_actors() if a.get_actor_label() == 'Architect_Finishes_v02']),
}
(root.parent / 'architect_finishes_v01' / 'unreal_import_report_v03.json').write_text(json.dumps(report, indent=2))
unreal.log('ARCHITECT_FINISHES_SAVED ' + str(report))
