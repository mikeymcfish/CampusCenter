"""Full-editor correction: displays, native finishes, correct closed-surface normals."""
import unreal,pathlib,json
R=pathlib.Path(__file__).parent
for name in ['install_decals.py','refine_displays.py','refine_architecture.py']:
 exec(compile((R/name).read_text(),str(R/name),'exec'))
E=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools()
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
dest='/Game/Campus/ArchitectFinishesV06'
if not E.does_directory_exist(dest):
 t=unreal.AssetImportTask();t.filename=str(R/'Architect_Finishes_v06.glb');t.destination_path=dest;t.automated=True;t.save=True;T.import_asset_tasks([t])
mesh=next(unreal.load_asset(p) for p in E.list_assets(dest,True) if '/StaticMeshes/' in p)
actor=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='Architect_Finishes_v02');c=actor.static_mesh_component
old={c.get_material(i).get_name().removeprefix('M_'):c.get_material(i) for i in range(c.get_num_materials())}
for i,slot in enumerate(mesh.static_materials):
 key=slot.material_interface.get_name().removeprefix('M_');assert key in old,(key,list(old));mesh.set_material(i,old[key])
c.set_static_mesh(mesh)
for i,slot in enumerate(mesh.static_materials):c.set_material(i,slot.material_interface)
settings=mesh.get_editor_property('nanite_settings');settings.enabled=True;settings.fallback_relative_error=0.;settings.fallback_percent_triangles=1.;settings.fallback_target=unreal.NaniteFallbackTarget.PERCENT_TRIANGLES
sub=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);assert sub;sub.set_nanite_settings(mesh,settings,True)
c.set_editor_property('disallow_nanite',False);E.save_loaded_asset(mesh)
# Plaster band above the cork, bounded by the same gallery run.
name='DD_Gallery_PlasterUpper';a=next((a for a in A.get_all_level_actors() if a.get_actor_label()==name),None)
if not a:a=A.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(-583,-1620.1,340));a.set_actor_label(name)
a.set_actor_scale3d(unreal.Vector(10.72,.018,1.56));a.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'));a.static_mesh_component.set_material(0,unreal.load_asset('/Game/Campus/ArchitectFinishesV04/NativeMaterials/M_AF_WarmWhitePlaster'));a.static_mesh_component.set_collision_profile_name('NoCollision')
L.save_current_level();(R/'round3_complete.json').write_text(json.dumps({'map':'CampusCenter_ArchitectDecals_v04','finish_mesh':mesh.get_path_name(),'full_detail_fallback':True},indent=2));unreal.log('ROUND3_COMPLETE')
# Let editor tool contexts finish initialization before shutdown.
import time
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
quit_at=time.monotonic()+30
def quit_tick(dt):
 if time.monotonic()>quit_at:
  unreal.unregister_slate_post_tick_callback(quit_handle);unreal.SystemLibrary.quit_editor()
quit_handle=unreal.register_slate_post_tick_callback(quit_tick)
