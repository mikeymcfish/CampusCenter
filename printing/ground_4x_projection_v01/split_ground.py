from pathlib import Path
import sys,json,hashlib
R=Path(__file__).parent;sys.path.insert(0,str(R/'python_packages'))
import numpy as np,trimesh
SRC=R.parent/'output_v12_roof_set/Campus_Center_Ground_v12.stl'
O=R/'print_tiles';O.mkdir(exist_ok=True)
m=trimesh.load_mesh(SRC,process=True);assert m.is_watertight and m.volume>0
source_bounds=m.bounds.copy();m.apply_scale(4)
lo,hi=m.bounds;xs=np.linspace(lo[0],hi[0],4);ys=np.linspace(lo[1],hi[1],3)
rows=[];total=0
for j in range(2):
 for i in range(3):
  a=np.array([xs[i],ys[j],-1]);b=np.array([xs[i+1],ys[j+1],hi[2]+1]);cut=trimesh.creation.box(extents=b-a,transform=trimesh.transformations.translation_matrix((a+b)/2))
  chunk=trimesh.boolean.intersection([m,cut],engine='manifold');assert chunk.is_watertight
  # Separate genuine disconnected islands so every STL is a single connected print.
  pieces=sorted(chunk.split(only_watertight=False),key=lambda x:-x.volume)
  for k,p in enumerate(pieces):
   assert p.is_watertight and p.volume>0
   offset=p.bounds[0].copy();offset[2]=0;p.apply_translation(-offset)
   assert np.all(p.extents<=[290,300,315]),p.extents
   name=f'Ground_{chr(65+j)}{i+1}'+(f'_{k+1}' if len(pieces)>1 else '')
   path=O/(name+'.stl');p.export(path);r=trimesh.load_mesh(path,process=True);assert r.is_watertight and r.is_winding_consistent and len(r.split())==1
   total+=r.volume;rows.append({'name':name,'file':path.name,'assembly_offset_mm':offset.tolist(),'dimensions_mm':r.extents.tolist(),'volume_mm3':r.volume,'triangles':len(r.faces),'watertight':True,'single_component':True,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()});print(name,r.extents,flush=True)
assert abs(total-m.volume)/m.volume<1e-5
report={'source':str(SRC),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'source_bounds_mm':source_bounds.tolist(),'scale_multiplier':4,'architectural_scale':'1:87.5','assembly_bounds_mm':m.bounds.tolist(),'assembly_dimensions_mm':m.extents.tolist(),'source_scaled_volume_mm3':m.volume,'tiles_volume_mm3':total,'relative_volume_error':abs(total-m.volume)/m.volume,'tile_maximum_mm':[290,300,315],'split_x_mm':xs.tolist(),'split_y_mm':ys.tolist(),'tiles':rows,'extra_ground_plane':False,'joints':'Exact planar butt joints; align using assembly map, glue only after dry fit.'}
(R/'print_manifest.json').write_text(json.dumps(report,indent=2));print('SPLIT_VALIDATED',len(rows),flush=True)
