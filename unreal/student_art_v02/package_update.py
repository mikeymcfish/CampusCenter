"""Validate local assets and build the complete eight-decal PC update ZIP."""
import ast
import hashlib
import json
import struct
import zipfile
from pathlib import Path

root=Path(__file__).resolve().parent
manifest=json.loads((root/'manifest.json').read_text())
checks=[]
for path in root.glob('*.py'):
    ast.parse(path.read_text())
    checks.append('Python syntax: '+path.name)
artworks=manifest['artworks']
assert len(artworks)==8
assert len({a['id'] for a in artworks})==8
assert len(manifest['hallway_x_cm'])==len(artworks)
# Exercise the actual standalone sizing function without importing Unreal.
tree=ast.parse((root/'apply_student_art.py').read_text())
function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='canvas_size')
namespace={'CONFIG':manifest}
exec(compile(ast.Module(body=[function],type_ignores=[]),'<canvas_size>','exec'),namespace)
boxes=[]
for art in artworks:
    data=(root/art['texture']).read_bytes()
    assert data[:8]==b'\x89PNG\r\n\x1a\n'
    width,height=struct.unpack('>II',data[16:24])
    assert [width,height]==art['size_px']
    assert hashlib.sha256(data).hexdigest()==art['sha256']
    for x0,y0,x1,y1 in [art['art_rect_px'],art['label_rect_px']]:
        assert 0<x0<x1<width and 0<y0<y1<height
    assert art['art_rect_px'][3]<art['label_rect_px'][1]
    box_w,box_h=namespace['canvas_size'](art)
    assert box_w<=140.000001 and box_h<=110.000001
    assert abs(box_w/box_h-width/height)<1e-9
    boxes.append((box_w,box_h))
    checks.append('PNG dimensions/hash, mask bounds/gap, undistorted bounded sizing: '+art['id'])
for i in range(len(artworks)-1):
    gap=abs(manifest['hallway_x_cm'][i+1]-manifest['hallway_x_cm'][i])-(boxes[i][0]+boxes[i+1][0])/2
    assert gap>=10-1e-6
checks.append('Eight unique artworks and positions; all adjacent projection boxes separated by at least 10 cm')
report={'status':'local_checks_passed_engine_not_run','artwork_count':8,'checks':checks,
        'visual_review':'New masked artworks and exact name labels inspected in browser; original four textures retained byte-for-byte.',
        'unreal_validation':'NOT RUN — Unreal is not installed on this Mac.'}
(root/'local_validation.json').write_text(json.dumps(report,indent=2)+'\n')
archive=root.parent/'Student_Art_Update_v02.zip'
repo=root.parent.parent
files=sorted(p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='apply_report.json')
files.extend(root.parent/name for name in ['Apply_Student_Art_v02.cmd','Walk_Student_Art_v02.cmd'])
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files:z.write(p,p.relative_to(repo).as_posix())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert len([n for n in z.namelist() if '/textures/' in n])==8
print(json.dumps({'status':report['status'],'artworks':len(artworks),'archive':str(archive),'bytes':archive.stat().st_size,'files':len(files)},indent=2))
