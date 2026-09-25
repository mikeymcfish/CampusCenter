"""Final scoped rendering cleanup: stable finish geometry and balanced fill."""
import unreal,pathlib,json
root=pathlib.Path(unreal.Paths.project_dir());ed=unreal.EditorAssetLibrary
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level('/Game/Campus/Maps/CampusCenter_Dusk_ArchitectFinishes_v03')
report={'geometry':[],'lights':[]}
dest='/Game/Campus/ArchitectFinishesV05'
if not ed.does_directory_exist(dest):
 task=unreal.AssetImportTask();task.filename=str(root.parent/'architect_finishes_v01/Architect_Finishes_v05.glb');task.destination_path=dest;task.automated=True;task.save=True
 unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
mesh=next(unreal.load_asset(p) for p in ed.list_assets(dest,recursive=True) if '/StaticMeshes/' in p)
for i,slot in enumerate(mesh.static_materials):
    material=unreal.load_asset('/Game/Campus/ArchitectFinishesV04/NativeMaterials/M_'+slot.material_interface.get_name().removeprefix('M_'))
    assert material
    mesh.set_material(i,material)
ed.save_loaded_asset(mesh)
for a in actors.get_all_level_actors():
 if a.get_actor_label()=='Architect_Finishes_v02':
  c=a.static_mesh_component;c.set_static_mesh(mesh)
  settings=mesh.get_editor_property('nanite_settings');settings.fallback_relative_error=0.0;settings.fallback_percent_triangles=1.0;settings.fallback_target=unreal.NaniteFallbackTarget.PERCENT_TRIANGLES
  settings.enabled=True;mesh.set_editor_property('nanite_settings',settings)
  c.set_editor_property('disallow_nanite',False);ed.save_loaded_asset(mesh);report['geometry'].append(mesh.get_path_name())
 if isinstance(a,unreal.RectLight):
  c=a.light_component;c.set_editor_property('samples_per_pixel',16)
  if a.get_actor_label()=='Architect_CRI_SoftFill':
   c.set_intensity(1600);c.set_cast_shadows(False)
  report['lights'].append(a.get_actor_label())
 if isinstance(a,unreal.PostProcessVolume):
  s=a.settings
  for k,v in {'lumen_scene_lighting_quality':4.0,'lumen_final_gather_quality':4.0,'lumen_reflection_quality':3.0,'auto_exposure_bias':.65}.items():
   s.set_editor_property('override_'+k,True);s.set_editor_property(k,v)
  a.set_editor_property('settings',s)
fill=actors.spawn_actor_from_class(unreal.RectLight,unreal.Vector(760,-2300,780),unreal.Rotator(pitch=-90,yaw=0,roll=0))
fill.set_actor_label('Architect_Commons_SoftFill')
c=fill.light_component;c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_intensity(1800);c.set_cast_shadows(False)
c.set_editor_property('source_width',1100.0);c.set_editor_property('source_height',1300.0);c.set_editor_property('attenuation_radius',2500.0)
c.set_editor_property('temperature',5600.0)
levels.save_current_level()
(root.parent/'architect_finishes_v01/round4_changes.json').write_text(json.dumps(report,indent=2))
unreal.log('ARCHITECT_ROUND4_COMPLETE')
exec((root/'validate_architect_delivery.py').read_text())
