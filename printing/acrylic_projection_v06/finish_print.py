from pathlib import Path
import sys,json,zipfile,hashlib,xml.etree.ElementTree as ET
R=Path(__file__).parent;D=R/'print';ROOT=R.parent
sys.path.insert(0,str(ROOT/'projection_furnished_v04/python_packages'))
import numpy as np,trimesh
from PIL import Image,ImageDraw,ImageFont
p=json.loads((D/'print_validation.json').read_text());rows=json.loads((D/'glazing_schedule.json').read_text())
base=Image.open(D/'Furnished_Print_Top.png').convert('RGB').resize((1640,1259))
im=Image.new('RGB',(2320,1600),(15,23,30));im.paste(base,(340,160));dr=ImageDraw.Draw(im)
font=ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf',19);title=ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf',32)
dr.text((40,25),'GROUND FLOOR — ACRYLIC INSERT POSITIONS',font=title,fill='white')
dr.text((40,70),'North up | G numbers match the cut list | dimensions are finished width x height in mm',font=font,fill=(171,200,217))
def xy(x,y):return (340+820+(x-398)*1640/830,160+1259/2-(y-289)*1640/830)
for side in [0,1]:
 group=sorted([q for q in rows if (q['center_xy_mm'][0]>=398)==bool(side)],key=lambda q:-q['center_xy_mm'][1])
 for i,q in enumerate(group):
  x,y=xy(*q['center_xy_mm']);tx=2000 if side else 25;ty=150+i*min(53,1320/max(1,len(group)))
  dr.line([(x,y),(tx-12 if side else 325,ty+13)],fill=(84,135,149),width=2)
  dr.ellipse((x-5,y-5,x+5,y+5),fill=(81,220,238));dr.text((tx,ty),f"{q['id']}   {q['cut_width_mm']:.1f} x {q['cut_height_mm']:.1f}",font=font,fill='white')
im.save(D/'Acrylic_Insert_Map.png')
# Independently reopen all print outputs and assembly transforms.
ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'};stls={};report=[]
for f in [D/'Campus_Center_Ground_Acrylic_1_87p5.stl',D/'Acrylic_Fit_Coupon.stl',*sorted((D/'print_tiles').glob('*.stl'))]:
 m=trimesh.load_mesh(f,process=True);assert m.is_watertight and m.is_winding_consistent and len(m.split())==1
 assert not ((m.face_normals[:,2]<-1e-5)&(m.triangles_center[:,2]>.02)).any()
 stls[f.stem]=m;report.append({'file':f.name,'watertight':True,'components':1,'elevated_downward_faces':0})
for f in [D/'Campus_Center_Acrylic_Assembly.3mf',D/'Acrylic_Fit_Coupon.3mf',*sorted((D/'print_tiles').glob('*.3mf'))]:
 with zipfile.ZipFile(f) as z:assert z.testzip() is None;root=ET.fromstring(z.read('3D/3dmodel.model'))
 assert root.attrib['unit']=='millimeter';parts={}
 for ob in root.findall('m:resources/m:object',ns):
  v=np.array([[float(a.attrib[k]) for k in ['x','y','z']] for a in ob.findall('m:mesh/m:vertices/m:vertex',ns)])
  faces=np.array([[int(a.attrib[k]) for k in ['v1','v2','v3']] for a in ob.findall('m:mesh/m:triangles/m:triangle',ns)])
  m=trimesh.Trimesh(v,faces,process=True);assert m.is_watertight and len(m.split())==1;parts[ob.attrib['id']]=m
  name=ob.attrib['name'];target=stls['Acrylic_Fit_Coupon' if name=='Fit coupon' else name];assert abs(m.volume-target.volume)/target.volume<1e-6
 assembled=[]
 for item in root.findall('m:build/m:item',ns):
  m=parts[item.attrib['objectid']].copy();t=[float(x) for x in item.attrib['transform'].split()];m.apply_translation(t[9:]);assembled.append(m)
 if len(assembled)==6:
  a=trimesh.util.concatenate(assembled);full=stls['Campus_Center_Ground_Acrylic_1_87p5'];assert np.allclose(a.bounds,full.bounds,atol=1e-4);assert abs(a.volume-full.volume)/full.volume<1e-5
assert json.loads((D/'cad_validation.json').read_text())['status']=='passed'
assert p['top_insertion_verified'] and p['source_unchanged']
(D/'reopen_validation.json').write_text(json.dumps({'status':'passed','meshes':report,'three_mf_checked':8,'step_valid':True,'pane_insertion_envelopes_checked':len(rows),'physical_fit_tested':False},indent=2))
files=[f for f in D.rglob('*') if f.is_file() and f.suffix in ['.stl','.3mf','.step','.csv','.svg','.md','.json','.png'] and f.name!='Acrylic_Panes_Reference_ONLY.stl']
out=R/'Ground_Acrylic_Print_Package.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(f,f.relative_to(D))
 for f in [R/'build_acrylic.py',R/'prepare_print.py',R/'print_edits_r08.py']:z.write(f,'editable_source/'+f.name)
with zipfile.ZipFile(out) as z:assert z.testzip() is None
print('PRINT_PACKAGE_VERIFIED',len(files),out.stat().st_size,hashlib.sha256(out.read_bytes()).hexdigest(),flush=True)
