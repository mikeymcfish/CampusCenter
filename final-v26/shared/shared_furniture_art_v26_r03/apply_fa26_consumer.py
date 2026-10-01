import unreal,pathlib,json,hashlib
# Caller supplies explicit consumer context. No desktop map/config defaults.
assert all(k in globals() for k in ['BASE_MAP','TARGET_MAP','RELEASE_ROOT'])
root=pathlib.Path(RELEASE_ROOT);m=json.loads((root/'manifest.json').read_text());E=unreal.EditorAssetLibrary;L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert BASE_MAP!=TARGET_MAP and not E.does_asset_exist(TARGET_MAP)
P=pathlib.Path(unreal.Paths.project_dir()).resolve()
for x in m['dependency_packages']:
 p=P/x['relative_file'];assert p.exists(),('missing dependency',x['package'])
 if x['new_namespace']:assert hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256'],('release package mismatch',x['package'])
 # Existing dependency hashes are inventoried, not silently overwritten. Consumer
 # owner must report any target-specific difference and verify semantic parity.
assert E.duplicate_asset(BASE_MAP,TARGET_MAP);assert L.load_level(TARGET_MAP)
actors=A.get_all_level_actors();retire=[]
for x in m['explicit_retirements']:
 matches=[a for a in actors if a.get_actor_label()==x['label'] and isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_path_name()==x['mesh']]
 assert len(matches)==1,('retirement identity unresolved',x['label'],len(matches));retire.append(matches[0])
assert not any(a.get_actor_label().startswith(('FA26_','ART26_')) for a in actors),'Consumer already contains enhancement; do not duplicate'
created=[]
for x in m['new_actor_recipes']:
 mesh=unreal.load_asset(x['mesh']);materials=[unreal.load_asset(p) for p in x['materials']];assert mesh and all(materials)
 rotation=x['rotation_degrees'];pitch,yaw,roll=rotation['pitch'],rotation['yaw'],rotation['roll'];a=A.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*x['location_cm']),unreal.Rotator(pitch=pitch,yaw=yaw,roll=roll));assert a;c=a.static_mesh_component;c.set_static_mesh(mesh);a.set_actor_scale3d(unreal.Vector(*x['scale']));assert c.get_num_materials()==len(materials)
 for i,mat in enumerate(materials):c.set_material(i,mat)
 a.set_actor_label(x['stable_label']);a.tags=[unreal.Name(t) for t in x['tags']];a.set_folder_path('FurnitureArtV26R01');c.set_collision_profile_name(x['component_collision_profile']);a.set_actor_enable_collision(x['actor_collision']);created.append(a)
for a in retire:
 a.set_editor_property('hidden',True);a.set_actor_enable_collision(False);a.static_mesh_component.set_collision_profile_name('NoCollision')
assert len(created)==277 and len(retire)==213;assert L.save_current_level();assert L.load_level(TARGET_MAP)
out=P/'Saved/FurnitureArtV26R01';out.mkdir(parents=True,exist_ok=True);(out/'consumer-application.json').write_text(json.dumps({'base_map':BASE_MAP,'target_map':TARGET_MAP,'new_actors':277,'retained_hidden_no_collision':213,'release_manifest_sha256':hashlib.sha256((root/'manifest.json').read_bytes()).hexdigest(),'status':'Saved/reopened; target-specific preservation, pixels and walking validation still required.'},indent=2))
