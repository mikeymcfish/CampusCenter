import pathlib,json,hashlib,io
ROOT=pathlib.Path(__file__).parent
OUT=ROOT/'art_batch_v26_r01';OUT.mkdir(exist_ok=True)
for n in ['textures','exports','renders','source']: (OUT/n).mkdir(exist_ok=True)
SRC=pathlib.Path(r'C:\Users\mikef\Documents\Codex\2026-09-30\task\CampusCenter-new-plans')
inv=json.loads((SRC/'downstream/next_phase_plan/art-implementation-inventory.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
for item in inv['items']:
 p=SRC/'references/art/future_unreal_20260930'/item['source'];assert sha(p)==item['sha256']
 meta=json.loads((OUT/'normalization.json').read_text())[item['source']]
 dst=OUT/'textures'/f"{item['stable_id']}.png"
 records.append(dict(item,source_absolute=str(p),normalization=meta,texture='textures/'+dst.name,texture_sha256=sha(dst),texture_size=meta['output_size'],representation='source photograph in shallow frame; photographed surroundings retained; no unseen geometry reconstructed',reconstruction_status='estimated/incomplete reconstruction' if item['source'] in ['IMG_1758.jpeg','IMG_2813.jpeg','IMG_3037.jpeg','IMG_4122.jpeg','IMG_6988.jpeg'] else 'photo-backed presentation; estimated frame dimensions',instantiate=item['source']!='IMG_1795.jpeg'))
old=[]
for version in ['v01','v02']:
 path=pathlib.Path(r'C:\Users\mikef\Documents\Codex\2026-09-30\task-3\CampusCenter-vive\unreal')/('student_art_'+version)
 m=json.loads((path/'manifest.json').read_text());entries=[]
 for a in m['artworks']:
  p=path/a['texture'];entries.append({'id':a['id'],'path':str(p),'sha256':sha(p),'matches_manifest':sha(p)==a['sha256'],'adaptation':a.get('adaptation')})
 old.append({'version':version,'source_map':m['source_map'],'entries':entries,'reuse_policy':'Reuse v02 existing assets by reference only when primary worker retains them; v01 IDs are already contained in v02. No verified identity match to the new photos; no duplicate exports or script execution.'})
manifest={'version':'ART26_R01','host':'Tank','unit':'metres','unreal_position_mapping':'[100*x,-100*y,100*z] centimetres','originals_preserved':True,'authorship_or_licensing':'Not established by sources; no inferred attribution','source_inventory':str(SRC/'downstream/next_phase_plan/art-implementation-inventory.json'),'artworks':records,'existing_packages':old,'render_contract':{'engine':'BLENDER_EEVEE','device':'default raster device','samples':32,'resolution':[640,640],'format':'PNG RGBA 8-bit','view_transform':'Standard','outputs':'11 individual photo-frame renders plus 1 proposed-layout render','purpose':'asset and reversible layout QA; not final room approval'},'integration_limits':['No print implementation','Do not run old updater scripts','Placement is proposed; primary worker must validate v26 furniture clearances and trace current wall corners before enabling actors','No edits to frozen baselines or Vive/primary copies'],'layout_basis':'Photo frames on Gallery-facing surface of Lab_east_wall0; all geometry kept east of x=0.125m, outside protected iLab. Two rows of six/ five small reversible photo panels. No new freestanding display floor footprint.'}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(OUT)
