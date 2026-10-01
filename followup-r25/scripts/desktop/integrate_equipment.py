import unreal,pathlib,json,re,hashlib
ROOT=pathlib.Path(__file__).parent;OUT=ROOT/'combined_r01';SRC=pathlib.Path(r'C:\Users\mikef\Documents\Codex\2026-10-01\task-3\equipment_staging');P=pathlib.Path(unreal.Paths.project_dir());contract=json.loads((OUT/'equipment-contract.json').read_text())
E=unreal.EditorAssetLibrary;AT=unreal.AssetToolsHelpers.get_asset_tools();L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
BASE='/Game/Campus/Maps/CampusCenter_FA26_Desktop_R22_ReceptionSlides';TARGET='/Game/Campus/Maps/CampusCenter_FA26_Desktop_R23_EquipmentBSOD';NS='/Game/Campus/EquipmentEQ27R01'
assert not (P/'Content/Campus/Maps/CampusCenter_FA26_Desktop_R23_EquipmentBSOD.umap').exists(),'Preserve existing version'
assert L.load_level(BASE);assert E.duplicate_asset(BASE,TARGET);assert L.load_level(TARGET)
def norm(v):return re.sub(r'[^a-z0-9]','',re.sub(r'_\d+$','',str(v).lower().removeprefix('slot_')))
def snap():
 rows={}
 for a in A.get_all_level_actors():
  c=getattr(a,'static_mesh_component',None)
  rows[a.get_name()]={'label':a.get_actor_label(),'location':a.get_actor_location().to_tuple(),'rotation':a.get_actor_rotation().to_tuple(),'scale':a.get_actor_scale3d().to_tuple(),'hidden':bool(a.get_editor_property('hidden')),'tags':[str(t) for t in a.tags],'mesh':c.static_mesh.get_path_name() if c and c.static_mesh else None,'materials':[c.get_material(i).get_path_name() if c.get_material(i) else None for i in range(c.get_num_materials())] if c else [],'collision_enabled':str(c.get_collision_enabled()) if c else None,'collision_profile':str(c.get_collision_profile_name()) if c else None,'cast_shadow':bool(c.get_editor_property('cast_shadow')) if c else None}
 return rows
before=snap();(OUT/'baseline-actors-r22.json').write_text(json.dumps(before,indent=2));records=[]
for row in contract['rows']:
 a=next(a for a in A.get_all_level_actors() if a.get_actor_label()==row['actor_label']);assert a.get_name()==row['actor_name'];c=a.static_mesh_component;old=c.static_mesh
 assert a.get_actor_location().to_tuple()==(0,0,0) and a.get_actor_scale3d().to_tuple()==(1,1,1)
 oldmap={norm(s.material_slot_name):c.get_material(i) for i,s in enumerate(old.get_editor_property('static_materials'))}
 f=SRC/'exports'/row['export'];assert hashlib.sha256(f.read_bytes()).hexdigest()==row['source_sha256']
 task=unreal.AssetImportTask();task.filename=str(f);task.destination_path=NS+'/Import/'+row['actor_label'];task.automated=True;task.save=True;task.replace_existing=True
 AT.import_asset_tasks([task]);assets=[unreal.load_asset(p) for p in E.list_assets(task.destination_path,recursive=True)];meshes=[n for n in assets if isinstance(n,unreal.StaticMesh)];assert len(meshes)==1,(row['export'],len(meshes))
 runtime=NS+'/Runtime/'+row['actor_label']+'_EQ27_R01';n=unreal.load_asset(runtime) if E.does_asset_exist(runtime) else E.duplicate_asset(meshes[0].get_path_name(),runtime);assert n
 slots=n.get_editor_property('static_materials');bindings={norm(x['gltf_name']):x for x in row['bindings']};mapped=[]
 for i,s in enumerate(slots):
  key=norm(s.material_slot_name);assert key in bindings,(key,list(bindings));binding=bindings[key];mat=unreal.load_asset(binding['native_material']);assert mat
  if key in oldmap:assert oldmap[key].get_path_name()==mat.get_path_name(),('Existing material override mismatch',key)
  base=mat
  while isinstance(base,unreal.MaterialInstanceConstant):base=base.get_editor_property('parent')
  assert base.get_editor_property('used_with_nanite'),('Existing material lacks Nanite usage',mat.get_path_name())
  s.material_interface=mat;mapped.append({'slot':i,'name':str(s.material_slot_name),'material':mat.get_path_name(),'preserved_existing_named_override':key in oldmap})
 assert len(slots)==len(bindings);n.set_editor_property('static_materials',slots)
 nan=old.get_editor_property('nanite_settings');nan.set_editor_property('fallback_relative_error',0.0);n.set_editor_property('nanite_settings',nan)
 body=n.get_editor_property('body_setup');oldbody=old.get_editor_property('body_setup');body.set_editor_property('collision_trace_flag',oldbody.get_editor_property('collision_trace_flag'));body.set_editor_property('agg_geom',oldbody.get_editor_property('agg_geom'))
 n.set_editor_property('asset_import_data',unreal.AssetImportData(outer=n,name='ProvenanceInExternalEquipmentContract'))
 assert E.save_loaded_asset(n,only_if_is_dirty=False);c.set_static_mesh(n);c.set_editor_property('override_materials',[s.material_interface for s in slots])
 d=n.get_static_mesh_description(0);positions=[d.get_vertex_position(unreal.VertexID(id_value=i)).to_tuple() for i in range(d.get_vertex_count())];actual=[[min(v[j] for v in positions) for j in range(3)],[max(v[j] for v in positions) for j in range(3)]]
 error=max(abs(actual[k][j]-row['expected_bounds_cm'][k][j]) for k in range(2) for j in range(3));assert error<0.05,('Units/axis mismatch',row['actor_label'],actual,row['expected_bounds_cm'])
 trace=body.get_editor_property('collision_trace_flag');assert trace==unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE
 assert c.get_collision_enabled()==unreal.CollisionEnabled.QUERY_AND_PHYSICS
 agg=body.get_editor_property('agg_geom');counts={k:len(agg.get_editor_property(k)) for k in ['sphere_elems','box_elems','sphyl_elems','convex_elems']};assert sum(counts.values())==1
 records.append({'actor_name':a.get_name(),'actor_label':a.get_actor_label(),'old_mesh':old.get_path_name(),'new_mesh':n.get_path_name(),'source_export':row['export'],'source_sha256':row['source_sha256'],'bounds_cm':actual,'source_bound_error_cm':error,'vertices':d.get_vertex_count(),'triangles':d.get_triangle_count(),'materials':mapped,'nanite_enabled':bool(n.get_editor_property('nanite_settings').enabled),'collision_trace_flag':str(trace),'simple_collision':counts,'fallback_relative_error':0.0})
 unreal.log('EQUIPMENT_REPLACED '+a.get_actor_label())
exec((ROOT/'install_bsod.py').read_text())
assert L.save_current_level();assert L.load_level(TARGET);after=snap();equipment_allowed={x['actor_name'] for x in records};allowed=equipment_allowed|{screen_name};changes={k:{'before':v,'after':after.get(k)} for k,v in before.items() if after.get(k)!=v};assert set(changes)==allowed,(set(changes),allowed)
for k in allowed:
 for field,value in before[k].items():
  allowed_fields=['mesh','materials'] if k in equipment_allowed else ['label','tags','materials']
  if field not in allowed_fields:assert after[k][field]==value,(k,field)
assert len(after)==len(before)==2229
manifest={'schema':'CampusCenter.combined-equipment-bsod.v1','baseline_map':BASE,'map':TARGET,'map_sha256':hashlib.sha256((P/'Content/Campus/Maps/CampusCenter_FA26_Desktop_R23_EquipmentBSOD.umap').read_bytes()).hexdigest(),'replacement_actors':records,'actor_count':len(after),'other_actor_changes':[],'reception_screen':bsod_manifest,'r22_slideshow_preserved_in_prior_version':True,'scene_configuration_unchanged':True,'mesh_local_collision_fidelity':'New meshes retain source Nanite settings except fallback_relative_error=0 to preserve open rack/cable collision triangles. Existing assets unchanged.','source_b05_bench_geometry':'All seven corrected donors preserved exactly by source payload validation; native import scale/axis checked within 0.05 cm.','trophy_integration':'Reserved until validated payload arrives','cooking':'Not started','verification':'Saved/reopened; collision/walking and rendered QA pending'}
(OUT/'equipment-integration-manifest.json').write_text(json.dumps(manifest,indent=2));(OUT/'allowed-actor-differences.json').write_text(json.dumps(changes,indent=2));unreal.SystemLibrary.quit_editor()
