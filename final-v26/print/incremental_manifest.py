from pathlib import Path
import json,hashlib
R=Path(__file__).parent;P=R.parent/'CampusCenter-print-furniture-v26-r01';d=json.loads((R/'changed_piece_manifest.json').read_text());changes=[]
for family in d['families']:
 folder=family['family'];old={x['name']:x for x in json.loads((P/folder/'validation.json').read_text())['tiles']};new=json.loads((R/folder/'validation.json').read_text())['tiles']
 for piece in new:
  name=piece['name'];p=R/folder/'print_tiles'/(name+'.stl');before=P/folder/'print_tiles'/p.name;sha=hashlib.sha256(p.read_bytes()).hexdigest();prev=hashlib.sha256(before.read_bytes()).hexdigest() if before.exists() else None
  changes.append({'file':str(p.relative_to(R)),'sha256_R02':sha,'sha256_R01':prev,'byte_changed_from_R01':sha!=prev,'volume_delta_mm3':piece['volume_mm3']-old[name]['volume_mm3'] if name in old else None,'assembly_offset_mm':piece['assembly_offset_mm'],'dimensions_mm':piece['dimensions_mm'],'note':'Byte changes can include triangulation. Component suffixes use volume ordering; compare assembly offsets for identity.'})
d['incremental_R01_comparison']={'previous_version':str(P),'pieces':changes,'unchanged_ground_STL_STEP_proof':'reused_ground_step_proof.json','corrected_source':'B05','enhancement_groups_carried':63,'corrected_existing_mesh_objects':37,'intentional_omissions':{'thin_wall_racks':3,'trophy_cases':2,'photo_presentations':11},'fitness_replacement_region':json.loads((R/'fitness_replacement_region.json').read_text())}
(R/'changed_piece_manifest.json').write_text(json.dumps(d,indent=2));print('R02_INCREMENTAL_MANIFEST_READY')
