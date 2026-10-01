import bpy,pathlib,json,hashlib,numpy as np
R=pathlib.Path(__file__).parent
P=pathlib.Path(r'C:\Users\mikef\Documents\Codex\2026-09-30\task\CampusCenter-new-plans\downstream\furniture_art_v26_r01')
src=pathlib.Path(bpy.data.filepath);expected='3013db5f7f8171b403bd5fac8561c84e24591875aa049683f950c3ee4e19e56e'
assert hashlib.sha256(src.read_bytes()).hexdigest()==expected
recommend=json.loads((P/'count-reconciliation-and-print-recommendation.json').read_text());manifest=json.loads((P/'batch4-manifest.json').read_text());items={i['marker_id']:i for i in manifest['items']}
bpy.context.scene.frame_set(1);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();rows=[];tris=[];owners=[]
for group in sum(recommend['groups'].values(),[]):
 item=items[group];reason='omit thin wall racks at display scale' if group in ['PH02_Fitness218_044','PH02_Fitness218_045','PH10_Fitness218_057'] else ('omit trophy contents/cases at display scale' if 'TrophyCase' in group else None)
 record={'id':group,'provenance':'actual geometry reuse' if group in recommend['groups']['actual_geometry_reuse'] else 'generic estimated geometry','decision':'omit' if reason else 'supported silhouette','reason':reason,'source_item':item,'objects':[]}
 index=len(rows);rows.append(record)
 if reason:continue
 for name in item['parts']:
  o=bpy.data.objects.get(name)
  if o is None or o.type!='MESH' or o.hide_render:continue
  ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();v=np.array([list(ev.matrix_world@x.co) for x in me.vertices],np.float32);f=np.array([t.vertices for t in me.loop_triangles],np.int32)
  if len(f):tris.append(v[f]);owners.append(np.full(len(f),index,np.int32));record['objects'].append(name)
  ev.to_mesh_clear()
 assert record['objects'],group
release=P/'releases/fitness_support_v26_r02';correction=json.loads((release/'source-manifest.json').read_text());proof=json.loads((release/'source-support-validation.json').read_text());assert correction['source_sha256']==expected
assert len([x for x in proof['support_tests'] if x.get('both_supports_intersect_shaft')])==5
assert len([x for x in proof['support_tests'] if x.get('loaded_bar_removed')])==2
assert proof['unchanged_mesh_objects']==6589 and proof['iLab_unchanged']
index=len(rows);bounds=[];objects=[];view_bounds={}
for name in correction['complete_group_membership']:
 o=bpy.data.objects[name];assert o.type=='MESH' and not o.hide_render,name;ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();v=np.array([list(ev.matrix_world@x.co) for x in me.vertices],np.float32);f=np.array([t.vertices for t in me.loop_triangles],np.int32);tris.append(v[f]);owners.append(np.full(len(f),index,np.int32));bounds.append(v);objects.append(name);view_bounds[name]=[v.min(0).tolist(),v.max(0).tolist()];ev.to_mesh_clear()
v=np.concatenate(bounds);rows.append({'id':'OriginalFitness_U218_Corrected','provenance':'corrected existing source geometry, schematic support','decision':'supported silhouette','reason':None,'source_item':{'bounds_m':[v.min(0).tolist(),v.max(0).tolist()]},'objects':objects})
np.savez_compressed(R/'furniture_surfaces.npz',triangles=np.concatenate(tris),owners=np.concatenate(owners))
(R/'furniture_source.json').write_text(json.dumps({'source':str(src),'sha256':expected,'blender':bpy.app.version_string,'recommendation':recommend,'groups':rows,'art_presentations_omitted':11,'fitness_release':str(release),'fitness_correction':correction,'fitness_correction_proof':proof,'enhancement_groups_carried':63,'corrected_existing_mesh_objects':len(objects),'fitness_view_bounds':view_bounds},indent=2))
print('EXTRACTED_FURNITURE',len(rows),sum(bool(x['objects']) for x in rows),sum(len(t) for t in tris),flush=True)
