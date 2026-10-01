from pathlib import Path
import sys,json,hashlib,zipfile,xml.etree.ElementTree as ET
R=Path(__file__).parent;B=R.parent/'CampusCenter-print-r25-r01';sys.path.insert(0,str(B/'python_packages'))
import numpy as np,trimesh,manifold3d as mf
reports=[];formats=[]
for family in ['ground_furnished','ground_enclosed','ground_acrylic','upper_enclosed','stacked_1_350']:
 for p in (R/family).rglob('*.stl'):
  if '_raw' in p.name:continue
  m=trimesh.load_mesh(p,process=True);assert m.is_watertight and m.is_winding_consistent and np.isfinite(m.vertices).all();assert (m.area_faces>1e-9).all(),p
  count=len(m.split());bed=p.parent.name=='print_tiles' or family=='stacked_1_350';assert abs(m.bounds[0,2])<.001
  if bed:assert np.all(m.extents<=[290,300,315])
  if p.parent.name=='print_tiles':assert count==1
  down=int(((m.face_normals[:,2]<-1e-5)&(m.triangles_center[:,2]>.02)).sum());assert down==0,(p,down)
  reports.append({'file':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'watertight':True,'normals_consistent':True,'zero_area_faces':0,'components':count,'elevated_down_faces':down,'dimensions_mm':m.extents.tolist(),'bed_fit':bed})
 for p in (R/family).rglob('*.3mf'):
  with zipfile.ZipFile(p) as z:root=ET.fromstring(z.read('3D/3dmodel.model'))
  ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'};assert root.get('unit')=='millimeter';count=0
  for o in root.findall('m:resources/m:object',ns):
   v=np.array([[float(x.get(a)) for a in ['x','y','z']] for x in o.findall('m:mesh/m:vertices/m:vertex',ns)]);f=np.array([[int(x.get(a)) for a in ['v1','v2','v3']] for x in o.findall('m:mesh/m:triangles/m:triangle',ns)]);m=trimesh.Trimesh(v,f,process=True);assert m.is_watertight and m.is_winding_consistent;count+=1
  formats.append({'file':str(p.relative_to(R)),'unit':'millimeter','reopened_meshes':count})
# Existing acrylic panes remain a no-print reference; ensure added furniture does not occupy their insertion envelopes.
furniture=np.load(R/'acrylic_furniture_addition.npz')['height'];schedule=json.loads((B/'ground_acrylic/glazing_schedule.json').read_text());collision=[]
for p in schedule['panes']:
 axis=p['axis'];start=p['start'];end=p['end'];center=p['center'];half=p['acrylic_nominal_mm']/2
 lo=[start,center-half] if axis==0 else [center-half,start];hi=[end,center+half] if axis==0 else [center+half,end]
 x0,y0=np.floor(np.array(lo)/.5).astype(int);x1,y1=np.ceil(np.array(hi)/.5).astype(int);occupied=furniture[y0:y1,x0:x1];maximum=float(occupied.max()) if occupied.size else 0
 if maximum>p['seat_z_mm']+.01:collision.append({'id':p['id'],'addition_height_mm':maximum,'seat_z_mm':p['seat_z_mm']})
assert not collision,collision
source=Path(json.loads((R/'furniture_source.json').read_text())['source']);sha=hashlib.sha256(source.read_bytes()).hexdigest();assert sha==json.loads((R/'furniture_source.json').read_text())['sha256']
baseline=json.loads((B/'delivery_manifest.json').read_text());(R/'baseline_manifest_reference.json').write_text(json.dumps(baseline,indent=2))
(R/'digital_validation.json').write_text(json.dumps({'status':'passed','source_sha256_after':sha,'source_unchanged':True,'stl_files':reports,'three_mf_files':formats,'acrylic_furniture_insertion_collisions':collision,'minimum_feature_assessment':'Constructive supported envelopes: 0.5 mm sampling plus one-cell broadening each side at 1:87.5; 0.25 mm miniature sampling with one-cell broadening. Floor clipping/cut edges can leave smaller local tips. No exhaustive thickness or slicer certification.','physical_or_slicer_tested':False},indent=2));print('VALIDATED',len(reports),'STL',len(formats),'3MF',flush=True)
