import json,pathlib,hashlib,struct,csv
O=pathlib.Path(__file__).parent;R=pathlib.Path('C:/Users/mikef/Documents/Codex/2026-09-30/task/CampusCenter-new-plans');m=json.loads((O/'replacement_manifest.json').read_text());v=json.loads((O/'validation.json').read_text());before=json.loads((O/'source_integrity_before.json').read_text(encoding='utf-8-sig'))
proof=[]
for row in before:
 p=pathlib.Path(row['Path']);h=hashlib.sha256(p.read_bytes()).hexdigest();proof.append({'path':str(p),'before':row['Hash'].lower(),'after':h,'unchanged':row['Hash'].lower()==h})
assert all(r['unchanged'] for r in proof)
(O/'source_integrity_after.json').write_text(json.dumps(proof,indent=2))
native=json.loads((R/'downstream/furniture_art_v26_r01/fitness_support_patch_r01/native-patch-manifest.json').read_text());slots={r['slot']:r['path'] for r in native['materials']}
names={'Dark metal':'Dark_metal','V8 plain rubber':'V8_plain_rubber','V8 plain sage upholstery':'V8_plain_sage_upholstery','Brushed stainless hardware':'Brushed_stainless_hardware','V8 plain dark screen':'V8_plain_dark_screen','Blockout equipment - untextured':'Blockout_equipment_-_untextured'}
compat=[]
for p in sorted((O/'exports').glob('*.glb')):
 raw=p.read_bytes();length,typ=struct.unpack_from('<II',raw,12);g=json.loads(raw[20:20+length]);mats=[{'gltf_material_index':i,'gltf_name':mat['name'],'native_material':slots.get(names.get(mat['name'],''))} for i,mat in enumerate(g.get('materials',[]))]
 compat.append({'export':p.name,'material_bindings':mats,'all_materials_resolved':all(x['native_material'] for x in mats),'texture_dependencies':len(g.get('images',[])),'use_named_material_mapping':'Import/assign by material name; existing actor slot indices may differ from new mesh indices; preserve visual mapping, not raw index order'})
assert all(c['all_materials_resolved'] and c['texture_dependencies']==0 for c in compat)
(O/'material_compatibility.json').write_text(json.dumps(compat,indent=2))
def bbox(obs):
 return [[min(o['bounds'][0][axis] for o in obs) for axis in range(3)],[max(o['bounds'][1][axis] for o in obs) for axis in range(3)]]
# Whole assembly checks are conservative original bound-box checks recorded by builder.
summary={'replacement_assemblies':len(m['replacements']),'export_files':len(v['exports']),'all_export_roundtrips_pass':all(e['roundtrip_pass'] for e in v['exports']),'max_export_bound_error_m':max(e['max_bound_error_m'] or 0 for e in v['exports']),'all_approved_footprints_pass':all(r['xy_envelope_pass'] for r in m['replacements']),'all_floor_support_pass':all(r['floor_support_pass'] for r in m['replacements']),'all_component_meshes_closed':all(t['nonmanifold_edges']==0 for r in m['replacements'] for t in r['topology']),'all_corrected_bench_world_geometry_preserved':all(d['world_geometry_equal_B05'] for d in v['donor_checks']),'five_supported_shafts':all(s['both_ledges_contact_shaft'] for s in v['rack_support_checks']),'two_standalone_benches_no_loadedbars':all(s['no_loaded_bar_geometry'] for s in v['standalone_checks']),'frozen_sources_unchanged':all(r['unchanged'] for r in proof),'unreal_runtime_checks':'Pending isolated integration; no maps were modified','geometry_dimensions':'Representative estimates except traced footprint/position; no manufacturer certification'}
(O/'DELIVERY_CHECKS.json').write_text(json.dumps(summary,indent=2))
summary['treadmill_and_machine_support_checks_pass']=all(all(value for key,value in row.items() if key!='assembly') for row in v['mechanical_support_checks'])
contract=json.loads((O/'preview_contract.json').read_text());png=[]
for name in contract['outputs']:
 p=O/'previews'/name;raw=p.read_bytes();width,height,depth,color=struct.unpack_from('>IIBB',raw,16);assert raw[:8]==b'\x89PNG\r\n\x1a\n' and (width,height,depth,color)==(1200,900,8,6);png.append({'file':name,'width':width,'height':height,'bit_depth':depth,'color_type':color,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
summary['six_cpu_previews_complete']=len(png)==6
summary['visual_review']='All six final preview types inspected; supports, recognizable mechanics, normals/materials and framing checked. Representative geometry remains estimated.'
(O/'preview_validation.json').write_text(json.dumps(png,indent=2))
(O/'DELIVERY_CHECKS.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
