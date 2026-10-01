import unreal,json,pathlib,hashlib
r=pathlib.Path(__file__).parent;p=pathlib.Path(unreal.Paths.project_dir());base='/Game/Campus/Maps/CampusCenter_Vive_EQ27_R06_TriggerWalk';target='/Game/Campus/Maps/CampusCenter_Vive_EQ27_R07_OpenXR'
bp=p/'Content/Campus/Maps/CampusCenter_Vive_EQ27_R06_TriggerWalk.umap';assert hashlib.sha256(bp.read_bytes()).hexdigest()=='3a7fcfd88c55e218e4f7cc309acacfddc5b56a4e49627af40ff51a3192b69954'
exists=unreal.EditorAssetLibrary.does_asset_exist(target)
if not exists:assert unreal.EditorAssetLibrary.duplicate_asset(base,target)
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert L.load_level(target);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);before=len(A.get_all_level_actors())
cls=unreal.load_class(None,'/Script/CampusCrowdFix.CampusViveXROrigin');assert cls
if not exists:
 helper=A.spawn_actor_from_class(cls,unreal.Vector(0,0,0));helper.set_actor_label('Vive_OpenXR_Local_Origin_R01');helper.set_actor_enable_collision(False);assert L.save_current_level()
else:
 assert len([a for a in A.get_all_level_actors() if a.get_actor_label()=='Vive_OpenXR_Local_Origin_R01'])==1;before-=1
helper=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='Vive_OpenXR_Local_Origin_R01');assert helper.context_registered_for_open_xr();mapping='/Game/Campus/ViveTriggerWalkR01/IMC_ViveTriggerWalk.IMC_ViveTriggerWalk'
report={'map':target,'baseline':base,'actors_before':before,'actors_after':len(A.get_all_level_actors()),'default_xr_context':str(mapping),'context_auto_add':False,'context_registered_before_session':True,'camera_contract':'Existing first-person camera locks to HMD; new map sets Local tracking origin to avoid adding floor height to elevated camera; no recenter/world-scale/speed/turning change','plugin_class_available':bool(unreal.load_class(None,'/Script/OpenXRInput.OpenXRInputFunctionLibrary'))}
(r/'map-created.json').write_text(json.dumps(report,indent=2));mp=p/'Content'/target[6:];mp=pathlib.Path(str(mp)+'.umap');(r/'frozen-final.json').write_text(json.dumps({'map':target,'baseline_map':base,'map_file':str(mp),'map_sha256':hashlib.sha256(mp.read_bytes()).hexdigest()},indent=2))

