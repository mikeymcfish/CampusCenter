import unreal,json,pathlib,hashlib
root=pathlib.Path(unreal.Paths.project_dir());out=pathlib.Path('C:/Users/mikef/Documents/Codex/2026-09-30/task-3/vr-openxr-r07-r01');out.mkdir(exist_ok=True)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);assert levels.load_level('/Game/Campus/Maps/CampusCenter_Vive_EQ27_R07_OpenXR')
def value(v):
 if v is None:return None
 if isinstance(v,(bool,int,float,str)):return v
 if isinstance(v,unreal.Object):return v.get_path_name()
 if hasattr(v,'to_tuple'):return [value(x) for x in v.to_tuple()]
 try:return [value(x) for x in v]
 except:return str(v)
keys=['static_mesh','skeletal_mesh_asset','asset','template','decal_material','material','intensity','light_color','temperature','use_temperature','cast_shadows','attenuation_radius','source_radius','source_width','source_height','mobility','visible','hidden_in_game','auto_activate','override_materials','collision_profile_name','collision_enabled','settings','unbound','priority','blend_radius','blend_weight','field_of_view','post_process_settings','post_process_blend_weight','world_scale','custom_primitive_data','receives_decals']
rows=[];refs=set()
for a in actors.get_all_level_actors():
 row={'label':a.get_actor_label(),'name':a.get_name(),'class':a.get_class().get_path_name(),'transform':{'location':value(a.get_actor_location()),'rotation':value(a.get_actor_rotation()),'scale':value(a.get_actor_scale3d())},'tags':value(a.tags),'folder':str(a.get_folder_path()),'actor_collision':a.get_actor_enable_collision(),'hidden':bool(a.get_editor_property('hidden')),'components':[],'disposition':'retain unchanged pending explicit accepted delta mapping'}
 for c in a.get_components_by_class(unreal.ActorComponent):
  cr={'name':c.get_name(),'class':c.get_class().get_path_name(),'properties':{}}
  for k in keys:
   try:cr['properties'][k]=value(c.get_editor_property(k))
   except:pass
  if isinstance(c,unreal.PrimitiveComponent):cr['properties']['collision_profile_name']=str(c.get_collision_profile_name());cr['properties']['collision_enabled']=str(c.get_collision_enabled())
  if isinstance(c,unreal.MeshComponent):
   cr['materials']=[value(c.get_material(i)) for i in range(c.get_num_materials())]
   if isinstance(c,unreal.StaticMeshComponent) and c.static_mesh:cr['mesh_material_slots']=[{'name':str(x.material_slot_name),'material':value(x.material_interface)} for x in c.static_mesh.get_editor_property('static_materials')]
  try:cr['transform']=value(c.get_world_transform())
  except:pass
  if isinstance(c,unreal.LightComponent):
   for k in ['indirect_lighting_intensity','volumetric_scattering_intensity','affect_translucent_lighting','lighting_channels','specular_scale','lightmass_settings']:
    try:cr['properties'][k]=value(c.get_editor_property(k))
    except:pass
  row['components'].append(cr)
 try:
  origin,extent=a.get_actor_bounds(False);row['bounds_cm']={'origin':value(origin),'extent':value(extent)}
 except:pass
 row['actor_properties']={}
 for k in keys:
  try:row['actor_properties'][k]=value(a.get_editor_property(k))
  except:pass
 rows.append(row)
registry=unreal.AssetRegistryHelpers.get_asset_registry();registry.search_all_assets(True);opt=unreal.AssetRegistryDependencyOptions();opt.include_hard_package_references=True;opt.include_soft_package_references=True;pending=['/Game/Campus/Maps/CampusCenter_Vive_EQ27_R07_OpenXR'];seen=set();deps=[]
while pending:
 p=pending.pop()
 if p in seen or not p.startswith('/Game/'):continue
 seen.add(p);pending.extend(str(x) for x in registry.get_dependencies(p,opt));base=root/'Content'/p[6:];path=next((pathlib.Path(str(base)+ext) for ext in ['.uasset','.umap'] if pathlib.Path(str(base)+ext).exists()),None)
 deps.append({'package':p,'file':str(path) if path else None,'sha256':hashlib.sha256(path.read_bytes()).hexdigest() if path else None})
report={'map':'/Game/Campus/Maps/CampusCenter_Vive_EQ27_R07_OpenXR','actors':rows,'dependencies':deps,'actor_count':len(rows),'read_only':'No actor modifications or saves','settings_limit':'Struct representations recorded along with unchanged source package hashes; baseline packages remain rollback authority'}
(out/'final-inventory.json').write_text(json.dumps(report,indent=2,default=str));unreal.log('BASELINE_INVENTORY_READY '+str(len(rows)))



helper=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Vive_Trigger_Walk_R01'); assert not helper.diagnostic_frame(1,True,1,True,True,True,True,0); (out/'diagnostic-gate-check.json').write_text(json.dumps({'without_explicit_qa_flag_rejected':True}))
