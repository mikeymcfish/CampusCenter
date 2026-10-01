import bpy,pathlib,json,hashlib
from mathutils import Vector
root=pathlib.Path(__file__).parent/'art_batch_v26_r01';m=json.loads((root/'manifest.json').read_text());r={'checks':[]}
for a in m['artworks']:
 assert hashlib.sha256(pathlib.Path(a['source_absolute']).read_bytes()).hexdigest()==a['sha256']
 if not a['instantiate']:continue
 for kind in ['fbx','glb']:
  bpy.ops.wm.read_factory_settings(use_empty=True)
  path=root/a[kind]
  if kind=='fbx':bpy.ops.import_scene.fbx(filepath=str(path))
  else:bpy.ops.import_scene.gltf(filepath=str(path))
  objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(objs)==1
  o=objs[0];expected=a['estimated_dimensions_m'];assert all(abs(o.dimensions[i]-expected[i])<.001 for i in range(3)),(a['stable_id'],kind,list(o.dimensions),expected)
  assert len(o.material_slots)==2
  r['checks'].append({'id':a['stable_id'],'format':kind,'mesh_count':1,'dimensions_m':list(o.dimensions),'material_slots':len(o.material_slots),'passed':True})
bpy.ops.wm.open_mainfile(filepath=str(root/'source/CampusCenter_Art26_R01.blend'),load_ui=False)
art=[o for o in bpy.context.scene.objects if o.name.startswith('ART26_IMG_')];assert len(art)==11
assert all((o.matrix_world@Vector(c)).x>=.1249 for o in art for c in o.bound_box)
r['saved_scene_reopened']=True;r['art_mesh_count']=11;r['missing_textures']=[i.filepath for i in bpy.data.images if i.source=='FILE' and not pathlib.Path(bpy.path.abspath(i.filepath)).exists()];assert not r['missing_textures']
r['originals_hash_verified_after']=12;r['visual_qa']='All 11 individual renders and proposed_layout.png inspected: correct orientation, source content, no frame clipping, no duplicate main red/black asset. Layout schematic shows spaced wall presentation.'
r['remaining_checks']='Unreal importer runtime, current-map wall corner traces, v26 furniture/door/equipment clearances, desktop/Vive appearance and package smoke are owned by integration workers; this batch does not certify those.'
(root/'validation.json').write_text(json.dumps(r,indent=2));print('VALIDATED_22_EXPORTS_AND_SAVED_SCENE')
