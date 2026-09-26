"""Saved-map preservation and dependency validation for ground-floor review."""
import unreal,pathlib,json,hashlib
R=pathlib.Path(__file__).parent;root=pathlib.Path(unreal.Paths.project_dir())
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
target='/Game/Campus/Maps/CampusCenter_GroundFloorReview_v05'
assert L.load_level(target)
before={a['label']:a for a in json.loads((R/'baseline_actors.json').read_text())}
after={};errors=[]
for a in A.get_all_level_actors():
    if not isinstance(a,unreal.StaticMeshActor):continue
    c=a.static_mesh_component
    after[a.get_actor_label()]={'mesh':c.static_mesh.get_path_name() if c.static_mesh else None,'position':list(a.get_actor_location().to_tuple()),'rotation':list(a.get_actor_rotation().to_tuple()),'scale':list(a.get_actor_scale3d().to_tuple()),'materials':[c.get_material(i).get_path_name() if c.get_material(i) else None for i in range(c.get_num_materials())]}
    if not c.static_mesh or any(c.get_material(i) is None for i in range(c.get_num_materials())):errors.append('Missing mesh/material: '+a.get_actor_label())
changed=[];relocations=[]
allowed_material_actors={'Commons_Honed_Floor','Architecture_Ground_08_13','DD_GalleryFloor_Oak','DD_TrophyFloor_Oak','ILab_Designed_Details','Repair_StairRisers'}
for name,b in before.items():
    if name not in after:errors.append('Removed existing actor: '+name);continue
    a=after[name]
    if any(b[k]!=a[k] for k in ['mesh','position','rotation','scale']):
        if name=='Site_Tree_08_00' and a['position']==[-400.,-5400.,-5.] and all(b[k]==a[k] for k in ['mesh','rotation','scale']):relocations.append({'actor':name,'before':b['position'],'after':a['position']})
        else:errors.append('Existing geometry/transform changed: '+name)
    if b['materials']!=a['materials']:
        changed.append(name)
        if name not in allowed_material_actors and not name.startswith(('Architecture_','Doors_Ground_')) and name!='Architect_Finishes_v02':errors.append('Unexpected material edit: '+name)
        for old,new in zip(b['materials'],a['materials']):
            if old!=new and not new.startswith('/Game/Campus/GroundFloorV03/'):errors.append('Unexpected material namespace: '+name)
added=sorted(set(after)-set(before))
if any(not n.startswith('GF_') for n in added):errors.append('Unexpected actor additions')
art=[n for n in after if n.startswith('DD_Artwork_')]
trophies=[n for n in after if n.startswith('DD_Trophy_') and n[-2:].isdigit()]
if len(art)!=9 or len(trophies)!=10:errors.append('Decal count changed')
pre=json.loads((R/'preflight.json').read_text())
source=root/'Content/Campus/Maps/CampusCenter_ArchitectDecals_v04.umap'
if hashlib.sha256(source.read_bytes()).hexdigest()!=pre['source_sha256']:errors.append('Source map hash changed')
registry=unreal.AssetRegistryHelpers.get_asset_registry();registry.search_all_assets(True)
opt=unreal.AssetRegistryDependencyOptions();opt.include_hard_package_references=True;opt.include_soft_package_references=True
todo=[target,'/Game/FirstPerson/Blueprints/BP_FirstPersonGameMode'];seen=set()
while todo:
    p=todo.pop()
    if p in seen or not p.startswith('/Game/'):continue
    seen.add(p);todo.extend(str(x) for x in registry.get_dependencies(p,opt))
files=[]
for p in sorted(seen):
    rel='Content/'+p[6:];f=next((root/(rel+e) for e in ['.uasset','.umap'] if (root/(rel+e)).is_file()),None)
    if f:files.append(str(f.relative_to(root)).replace('\\','/'))
    else:errors.append('Missing dependency: '+p)
report={'map':target,'source_preserved':not any('Source map' in e for e in errors),'existing_actor_count':len(before),'existing_geometry_and_transforms_preserved_except_listed_environment_relocation':not any('geometry/transform' in e or 'Removed' in e for e in errors),'environment_relocations':relocations,'material_overrides':sorted(changed),'added':added,'artworks':len(art),'trophies':len(trophies),'errors':errors,'dependency_files':files}
(R/'delivery_validation.json').write_text(json.dumps(report,indent=2))
unreal.log('GROUND_FLOOR_VALIDATION '+str({k:v for k,v in report.items() if k not in ['dependency_files','added']}))
assert not errors,errors
