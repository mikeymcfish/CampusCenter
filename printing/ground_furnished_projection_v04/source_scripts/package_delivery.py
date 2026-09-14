from pathlib import Path
import json,hashlib,shutil,zipfile
R=Path(__file__).parent
DEST=Path('P:/_code/CampusCenter/printing/ground_furnished_projection_v04')
validated=json.loads((R/'delivery_validation.json').read_text());assert validated['status']=='passed'
hs=json.loads((R/'information/render_hashes.json').read_text());assert hs['master'][0]==hs['master'][-1] and hs['native'][0]==hs['native'][-1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
core=['README.md','Campus_Center_Ground_Furnished_1_87p5.stl','Campus_Center_Ground_Furnished_1_87p5.step','Campus_Center_Furnished_Assembly.3mf','Campus_Center_Furnished_Print.blend','Campus_Center_Projection_Receiver.blend','Campus_Center_Information_Preview.blend','Furnished_Print_Preview.png','Furnished_Print_Top.png','Furnished_Detail_Preview.png','Information_On_Model_01.png','Information_On_Model_03.png','Assembly_Map.png','floor_mask.png','furniture_mask.png','receiver_mask.png','print_validation.json','cad_validation.json','delivery_validation.json','receiver_contract.json','furniture_source.json','print_height_data.npz','cad_mesh.npz','build_information.py','serve_player.py','browser_validation.json']
files=[(R/n,Path(n)) for n in core]
files += [(p,Path('print_tiles')/p.name) for p in sorted((R/'print_tiles').iterdir()) if p.suffix in ['.stl','.3mf']]
files += [(p,Path('information')/p.name) for p in sorted((R/'information').iterdir()) if p.suffix in ['.png','.mp4','.json','.html']]
for name in ['extract_furniture.py','build_print.py','retile.py','export_cad.py','render_print.py','render_presentation.py','validate_delivery.py','create_assembly_map.py','package_delivery.py']:
    files.append((R/name,Path('source_scripts')/name))
assert all(p.is_file() for p,_ in files)
DEST.mkdir(parents=True,exist_ok=True);entries=[]
for source,relative in files:
    target=DEST/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);a=digest(source);assert digest(target)==a
    entries.append({'file':relative.as_posix(),'bytes':target.stat().st_size,'sha256':a,'source':str(source)})
printreadme=(R/'README.md').read_text().split('## Informational mapping')[0]
printreadme=printreadme.replace('unzip `Campus_Center_Furnished_Print_Package.zip`, then load','load')
printreadme=printreadme.split('## Start here')[0]+'''## Start here

Print the six individual STL or 3MF files in `print_tiles/` at 100% scale in millimetres, flat underside down. The two formats contain equivalent geometry. The assembled 3MF is an alignment reference; the STEP contains the complete furnished floor as a single CAD solid.

'''+'## Physical model'+printreadme.split('## Physical model',1)[1]
printreadme+='\n## Digital checks\n\nAll seven STL files and seven 3MF files were independently reopened. Every individual tile is watertight, connected and consistently wound, with no elevated downward-facing surface. The STEP reopened as one valid CAD solid. Physical printing remains to be tested. See the included JSON reports.\n'
(DEST/'README_Print.md').write_text(printreadme,encoding='utf-8')
zipnames=['README_Print.md','Assembly_Map.png','Furnished_Print_Preview.png','Furnished_Detail_Preview.png','Campus_Center_Ground_Furnished_1_87p5.stl','Campus_Center_Ground_Furnished_1_87p5.step','Campus_Center_Furnished_Assembly.3mf','print_validation.json','cad_validation.json']+[str(r).replace('\\','/') for _,r in files if r.parts[0]=='print_tiles']
archive=DEST/'Campus_Center_Furnished_Print_Package.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for n in zipnames:z.write(DEST/n,n)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for n in zipnames:assert hashlib.sha256(z.read(n)).hexdigest()==digest(DEST/n)
for n in ['README_Print.md',archive.name]:
    p=DEST/n;entries.append({'file':n,'bytes':p.stat().st_size,'sha256':digest(p),'source':'Generated delivery package'})
manifest={'status':'verified','created':'2026-09-14','files':entries,'print_zip_entries':len(zipnames),'source_files_preserved':True,'scope':'Ground-floor furnished print, informational projection and matched masks'}
(DEST/'PACKAGE_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
shutil.copy2(archive,R/archive.name)
# Keep the existing repository index and point its current projection link here.
index=DEST.parents[1]/'README.md';text=index.read_text(encoding='utf-8')
text=text.replace('Current floor-only projection: [v03','Previous floor-only projection: [v03')
section='''
## Furnished ground-floor print and informational mapping

Current ground-floor projection model: [v04 — furniture integrated into the support-free print](printing/ground_furnished_projection_v04/README.md). Six STL/3MF tiles, a complete furnished STEP, unchanged 1:87.5 footprint, and no extra ground plane. [Print package](printing/ground_furnished_projection_v04/Campus_Center_Furnished_Print_Package.zip).

The matching [42-second informational tour](printing/ground_furnished_projection_v04/information/Campus_Center_Information_Preview.mp4) highlights commons/cafe, iLab, learning/gallery and athletics, with room captions and checked circulation routes. [Player and alignment modes](printing/ground_furnished_projection_v04/information/index.html). Wall tops and exterior pixels remain black in the RGB masters. Digital geometry and decoded-frame checks passed; physical printing and projector calibration remain to be done.
'''
if '## Furnished ground-floor print and informational mapping' not in text:text+='\n'+section
index.write_text(text,encoding='utf-8')
assert 'ground_furnished_projection_v04/README.md' in index.read_text(encoding='utf-8')
(R/'package_verification.json').write_text(json.dumps({'destination':str(DEST),'verified_files':len(entries),'zip_entries':len(zipnames),'zip_bytes':archive.stat().st_size,'package_manifest_sha256':digest(DEST/'PACKAGE_MANIFEST.json'),'status':'passed'},indent=2))
print('PACKAGE_VERIFIED',len(entries),archive.stat().st_size,str(DEST),flush=True)
