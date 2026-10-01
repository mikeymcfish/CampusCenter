import unreal,pathlib,json
R=pathlib.Path(__file__).parent/'combined_r01';E=unreal.EditorAssetLibrary;L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);base='/Game/Campus/Maps/CampusCenter_FA26_Desktop_R24_CombinedReview';target='/Game/Campus/Maps/CampusCenter_FA26_Desktop_R25_CombinedReview';assert L.load_level(base);assert not E.does_asset_exist(target);assert E.duplicate_asset(base,target);assert L.load_level(target);rows=[]
for a in A.get_all_level_actors():
 if a.get_actor_label() not in ['SilverCup_AthleticsCase_TR27R01','RegionalPlaque_AthleticsCase_TR27R01']:continue
 c=a.static_mesh_component;before={'profile':str(c.get_collision_profile_name()),'enabled':str(c.get_collision_enabled())};c.set_collision_profile_name('NoCollision');c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION);assert c.get_collision_profile_name()=='NoCollision';assert c.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION;rows.append({'actor':a.get_name(),'label':a.get_actor_label(),'before':before});
assert len(rows)==2;assert L.save_current_level();del a,c;assert L.load_level(target);actors={a.get_name():a for a in A.get_all_level_actors()};assert len(actors)==2231
for row in rows:
 c=actors[row['actor']].static_mesh_component;assert c.get_collision_profile_name()=='NoCollision';assert c.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION;row['saved_reopened']={'profile':str(c.get_collision_profile_name()),'enabled':str(c.get_collision_enabled())}
for name in ['StaticMeshActor_1813','StaticMeshActor_1814']:
 c=actors[name].static_mesh_component;assert c.get_collision_enabled()==unreal.CollisionEnabled.QUERY_AND_PHYSICS;assert c.get_collision_profile_name()=='BlockAll'
(R/'r25-trophy-collision-proof.json').write_text(json.dumps({'map':target,'actor_count':len(actors),'trophy_components':rows,'original_cases_remain_BlockAll':True,'R24_map_and_R01_zip_unchanged':True},indent=2));unreal.SystemLibrary.quit_editor()
