import unreal,json,pathlib,math,time
root=pathlib.Path(unreal.Paths.project_dir()); transfer=root.parent/'unreal_transfer/exports'
manifest=json.loads((transfer/'transfer_manifest.json').read_text())
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
task=unreal.AssetImportTask();task.filename=str(transfer/'Campus_Transfer.glb');task.destination_path='/Game/Campus/Imported';task.automated=True;task.save=True
paths=unreal.EditorAssetLibrary.list_assets('/Game/Campus/Imported',recursive=True)
if not paths:
 unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
 paths=list(task.imported_object_paths)
if not paths:paths=unreal.EditorAssetLibrary.list_assets('/Game/Campus/Imported',recursive=True)
report={'imported_paths':paths,'meshes':[],'lights':[],'warnings':[]}
meshes=[unreal.load_asset(p) for p in paths];meshes=[a for a in meshes if isinstance(a,unreal.StaticMesh)]
assert len(meshes)>=200,len(meshes)
for mesh in meshes:
 name=mesh.get_name();body=mesh.get_editor_property('body_setup')
 if body:body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 actor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0));actor.set_actor_label(name);component=actor.static_mesh_component;component.set_static_mesh(mesh)
 category=next((c for c in ['Students','Furniture','Equipment','Architecture','Doors','Roof','Screen'] if name.startswith(c)),'Architecture')
 actor.tags=[category];actor.set_folder_path(category)
 component.set_mobility(unreal.ComponentMobility.STATIC)
 component.set_collision_profile_name('NoCollision' if category in ['Students','Screen'] else 'BlockAll')
 if category=='Screen':actor.set_actor_hidden_in_game(True)
 unreal.EditorAssetLibrary.save_loaded_asset(mesh)
 bounds=mesh.get_bounds();report['meshes'].append({'name':name,'path':mesh.get_path_name(),'category':category,'origin':list(bounds.origin.to_tuple()),'extent':list(bounds.box_extent.to_tuple())})
def spawn(cls,name,p,rot=None):
 r=rot or [0,0,0];a=actors.spawn_actor_from_class(cls,unreal.Vector(*p),unreal.Rotator(pitch=r[0],yaw=r[1],roll=r[2]));a.set_actor_label(name);a.set_folder_path('Lighting');return a
sun=spawn(unreal.DirectionalLight,'Daylight_Sun',[0,0,2000],[-38,-125,0]);sun.light_component.set_editor_property('intensity',18000.0);sun.light_component.set_editor_property('atmosphere_sun_light',True);sun.light_component.set_editor_property('light_source_angle',2.0)
spawn(unreal.SkyAtmosphere,'Atmosphere',[0,0,0])
sky=spawn(unreal.SkyLight,'Daylight_Sky',[0,0,1500]);sky.light_component.set_editor_property('real_time_capture',True);sky.light_component.set_editor_property('intensity',1.0)
for info in manifest['lights']:
 if info['type']=='SUN':continue
 p=info['p'];a=spawn(unreal.RectLight,info['name'],[p[0]*100,-p[1]*100,p[2]*100],[-90,0,0]);c=a.light_component
 c.set_editor_property('intensity_units',unreal.LightUnits.LUMENS);c.set_editor_property('intensity',max(1800,min(14000,info['energy']*24)))
 c.set_editor_property('attenuation_radius',1100.0);c.set_editor_property('source_width',max(60,min(300,info['size']*100)));c.set_editor_property('source_height',100.0)
 c.set_editor_property('use_temperature',True);c.set_editor_property('temperature',4400.0);c.set_editor_property('cast_shadows',True)
 report['lights'].append(info['name'])
pp=spawn(unreal.PostProcessVolume,'Exposure_and_Color',[0,0,0]);pp.set_editor_property('unbound',True)
settings=pp.get_editor_property('settings')
for key,value in {'override_auto_exposure_min_brightness':True,'auto_exposure_min_brightness':5.0,'override_auto_exposure_max_brightness':True,'auto_exposure_max_brightness':11.0,'override_auto_exposure_bias':True,'auto_exposure_bias':0.5,'override_motion_blur_amount':True,'motion_blur_amount':0.0,'override_bloom_intensity':True,'bloom_intensity':0.15}.items():settings.set_editor_property(key,value)
pp.set_editor_property('settings',settings)
start=actors.spawn_actor_from_class(unreal.PlayerStart,unreal.Vector(2200,-1207,88),unreal.Rotator(yaw=180));start.set_actor_label('Entrance_PlayerStart')
rooms=json.loads((transfer/'rooms.json').read_text())
for i,r in enumerate(rooms):
 d=r['dir'];rot=unreal.Rotator(pitch=math.degrees(math.atan2(d[2],math.hypot(d[0],d[1]))),yaw=math.degrees(math.atan2(d[1],d[0])),roll=0)
 cam=actors.spawn_actor_from_class(unreal.CameraActor,unreal.Vector(*r['p']),rot);cam.set_actor_label('Review_%02d_%s'%(i,r['name']));cam.camera_component.set_field_of_view(78.0);cam.set_folder_path('Review cameras')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/Campus/Maps/CampusCenter')
unreal.EditorAssetLibrary.save_directory('/Game/Campus',only_if_is_dirty=True,recursive=True)
assert levels.load_level('/Game/Campus/Maps/CampusCenter')
assert len([a for a in actors.get_all_level_actors() if isinstance(a,unreal.StaticMeshActor)])==len(meshes)
(root/'import_report.json').write_text(json.dumps(report,indent=2,default=str));unreal.log('CAMPUS_IMPORT_COMPLETE '+str(len(meshes)))
