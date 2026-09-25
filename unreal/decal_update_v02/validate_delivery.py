"""Compare saved source/new maps, verify supplied assets, and collect dependencies."""
import unreal,json,pathlib,hashlib
R=pathlib.Path(__file__).parent;root=pathlib.Path(unreal.Paths.project_dir())
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
source='/Game/Campus/Maps/CampusCenter_Dusk_ArchitectFinishes_v03';target='/Game/Campus/Maps/CampusCenter_ArchitectDecals_v04'
def snap(path):
 assert L.load_level(path)
 rows={}
 for a in A.get_all_level_actors():
  if isinstance(a,unreal.StaticMeshActor):
   c=a.static_mesh_component
   rows[a.get_actor_label()]={'mesh':c.static_mesh.get_path_name() if c.static_mesh else None,'position':list(a.get_actor_location().to_tuple()),'scale':list(a.get_actor_scale3d().to_tuple()),'rotation':list(a.get_actor_rotation().to_tuple()),'materials':[c.get_material(i).get_path_name() if c.get_material(i) else None for i in range(c.get_num_materials())]}
 return rows
before=snap(source);after=snap(target);errors=[]
changed=[k for k in before.keys()&after.keys() if before[k]!=after[k]]
removed=sorted(before.keys()-after.keys());added=sorted(after.keys()-before.keys())
unexpected=[]
for k in changed:
 if k!='Architect_Finishes_v02' or any(before[k][p]!=after[k][p] for p in ['position','scale','rotation']):unexpected.append(k)
 elif before[k]['mesh']!=after[k]['mesh'] and not after[k]['mesh'].startswith('/Game/Campus/ArchitectFinishesV06/'):unexpected.append(k)
 elif any(a!=b and not b.startswith('/Game/Campus/DisplayDecalsV02/ArchitectureMaterials/') for a,b in zip(before[k]['materials'],after[k]['materials'])):unexpected.append(k)
if unexpected:errors.append({'unexpected_existing_mesh_changes':unexpected})
if removed:errors.append({'removed_existing_mesh_actors':removed})
if any(not n.startswith('DD_') for n in added):errors.append('Unexpected additions')
art=[k for k in after if k.startswith('DD_Artwork_')];trophy=[k for k in after if k.startswith('DD_Trophy_') and k[-2:].isdigit()]
if len(art)!=9 or len(trophy)!=10:errors.append('Wrong decal count')
display_bounds={}
for a in A.get_all_level_actors():
 k=a.get_actor_label()
 if isinstance(a,unreal.StaticMeshActor) and k.startswith('DD_'):
  c=a.static_mesh_component
  if not c.static_mesh or any(c.get_material(i) is None for i in range(c.get_num_materials())):errors.append('Missing display mesh/material '+k)
  if str(c.get_collision_profile_name())!='NoCollision':errors.append('Unexpected display collision '+k)
  center,extent=a.get_actor_bounds(False)
  display_bounds[k]={'center_cm':list(center.to_tuple()),'extent_cm':list(extent.to_tuple()),'bottom_cm':center.z-extent.z,'top_cm':center.z+extent.z}
  if k in art+trophy:
   mat=c.get_material(0)
   if mat.get_editor_property('blend_mode')!=unreal.BlendMode.BLEND_MASKED:errors.append('Non-masked decal '+k)
shelf_top=display_bounds['DD_Trophy_Shelf']['top_cm']
for k in trophy:
 if abs(display_bounds[k]['bottom_cm']-shelf_top)>.2:errors.append('Trophy does not meet shelf '+k)
for item in json.loads((R/'asset_inventory.json').read_text()):
 if hashlib.sha256((R/item['file']).read_bytes()).hexdigest()!=item['sha256']:errors.append('Source changed '+item['file'])
pre=json.loads((R/'preflight.json').read_text());sourcefile=root/'Content/Campus/Maps/CampusCenter_Dusk_ArchitectFinishes_v03.umap'
if hashlib.sha256(sourcefile.read_bytes()).hexdigest()!=pre['sha256']:errors.append('Source map changed')
registry=unreal.AssetRegistryHelpers.get_asset_registry();registry.search_all_assets(True)
opt=unreal.AssetRegistryDependencyOptions();opt.set_editor_property('include_hard_package_references',True);opt.set_editor_property('include_soft_package_references',True)
todo=[target,'/Game/FirstPerson/Blueprints/BP_FirstPersonGameMode'];seen=set()
while todo:
 p=todo.pop()
 if p in seen or not p.startswith('/Game/'):continue
 seen.add(p);todo.extend(str(x) for x in registry.get_dependencies(p,opt))
files=[]
for p in sorted(seen):
 rel='Content/'+p[6:];f=next((root/(rel+e) for e in ['.uasset','.umap'] if (root/(rel+e)).is_file()),None)
 if f:files.append(str(f.relative_to(root)).replace('\\','/'))
 else:errors.append('Missing package '+p)
report={'map':target,'artworks':len(art),'trophies':len(trophy),'unchanged_existing_mesh_actors':len(before)-len(changed),'changed_existing':changed,'permitted_architecture_material_override':changed==['Architect_Finishes_v02'],'removed':removed,'added':added,'errors':errors,'dependency_files':files,'display_actors':{k:after[k] for k in added},'display_bounds_cm':display_bounds,'trophy_shelf_top_cm':shelf_top}
(R/'delivery_validation.json').write_text(json.dumps(report,indent=2));unreal.log('DISPLAY_VALIDATION '+str({k:v for k,v in report.items() if k not in ['dependency_files','added','display_actors','display_bounds_cm']}));assert not errors,errors
