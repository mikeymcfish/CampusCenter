from pathlib import Path
import json,hashlib
R=Path(__file__).parent;B=R.parent/'CampusCenter-print-r25-r01';d=json.loads((R/'changed_piece_manifest.json').read_text())
for family in d['families']:
 folder=family['family'];validation=json.loads((R/folder/'validation.json').read_text());old=json.loads((B/folder/'validation.json').read_text());byname={x['name']:x for x in validation['tiles']};oldname={x['name']:x for x in old['tiles']}
 for region in family['regions']:
  region['pieces']=[]
  for file in region['variant_files']:
   stem=Path(file).stem;v=byname[stem];p=R/folder/'print_tiles'/file
   region['pieces'].append({'file':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'dimensions_mm':v['dimensions_mm'],'assembly_offset_mm':v['assembly_offset_mm'],'volume_mm3':v['volume_mm3'],'region_has_furniture_geometry_change':region['changed_geometry'],'baseline_region_candidates':[{'file':str(Path(folder)/'print_tiles'/f),'sha256':hashlib.sha256((B/folder/'print_tiles'/f).read_bytes()).hexdigest(),'assembly_offset_mm':oldname[Path(f).stem]['assembly_offset_mm']} for f in region['baseline_files']]})
d['unchanged_accessories']='Original v25 optional partitions, acrylic coupon/cut schedule/reference panes copied byte-identically under original_accessories.'
d['regeneration_dependencies']='Generators read sibling CampusCenter-print-r25-r01 baseline and its isolated python_packages; that verified package must be available for regeneration. Editable Blender/STL/3MF/STEP can be used independently.'
(R/'changed_piece_manifest.json').write_text(json.dumps(d,indent=2));print('EXACT_PIECES_RECORDED')
