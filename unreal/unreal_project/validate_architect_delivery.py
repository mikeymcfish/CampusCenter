"""Saved-map comparison and recursive asset dependency manifest for Git delivery."""
import unreal,pathlib,json
root=pathlib.Path(unreal.Paths.project_dir()); out=root.parent/'architect_finishes_v01'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
source='/Game/Campus/Maps/CampusCenter_Dusk'
target='/Game/Campus/Maps/CampusCenter_Dusk_ArchitectFinishes_v03'
def snapshot(path):
 assert levels.load_level(path)
 result={}
 for a in actors.get_all_level_actors():
  if not isinstance(a,unreal.StaticMeshActor):continue
  c=a.static_mesh_component
  result[a.get_actor_label()]={'mesh':c.static_mesh.get_path_name() if c.static_mesh else None,
   'location':list(a.get_actor_location().to_tuple()),'rotation':list(a.get_actor_rotation().to_tuple()),'scale':list(a.get_actor_scale3d().to_tuple()),
   'materials':[c.get_material(i).get_path_name() if c.get_material(i) else None for i in range(c.get_num_materials())]}
 return result
before=snapshot(source); after=snapshot(target)
allowed_removed={'King_FullHeight_V5_Banner_20','King_FullHeight_V5_Banner_25','King_FullHeight_V5_Banner_29'}
removed=set(before)-set(after); added=set(after)-set(before)
changed=[k for k in before.keys()&after.keys() if before[k]!=after[k]]
errors=[]
if removed-allowed_removed:errors.append('Unexpected removed actors: '+str(removed-allowed_removed))
if added-{'Architect_Finishes_v02'}:errors.append('Unexpected added mesh actors: '+str(added))
if changed:errors.append('Existing mesh actors changed: '+str(changed))
registry=unreal.AssetRegistryHelpers.get_asset_registry();registry.search_all_assets(True)
options=unreal.AssetRegistryDependencyOptions()
options.set_editor_property('include_hard_package_references',True)
options.set_editor_property('include_soft_package_references',True)
pending=[target,source,'/Game/FirstPerson/Blueprints/BP_FirstPersonGameMode'];seen=set()
while pending:
 p=pending.pop()
 if p in seen or not p.startswith('/Game/'):continue
 seen.add(p)
 pending.extend(str(x) for x in registry.get_dependencies(p,options))
files=[]
for p in sorted(seen):
 rel='Content/'+p[len('/Game/'):]
 choices=[root/(rel+ext) for ext in ['.uasset','.umap']]
 found=next((p for p in choices if p.is_file()),None)
 if found:files.append(str(found.relative_to(root)).replace('\\','/'))
 else:errors.append('Missing package '+p)
report={'map':target,'unchanged_existing_mesh_actors':len(before.keys()&after.keys())-len(changed),'removed':sorted(removed),'added':sorted(added),'changed':changed,'errors':errors,'dependency_files':files}
(out/'delivery_validation.json').write_text(json.dumps(report,indent=2))
unreal.log('DELIVERY_VALIDATION '+str({k:v for k,v in report.items() if k!='dependency_files'}))
assert not errors,errors
