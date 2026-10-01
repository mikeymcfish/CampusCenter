"""Rebuild supported print heightfields from pinned accepted mesh surfaces.
Run with project Python 3.10; original artifacts are only read.
"""
from pathlib import Path
import sys,json,ast,zipfile,hashlib,time
R=Path(__file__).parent;OLD=R/'workflow_inputs'
sys.path[:0]=[str(R/'python_packages'),str(OLD)]
import numpy as np,trimesh,manifold3d as mf
from scipy.ndimage import maximum_filter,binary_closing,label
from shapely.geometry import Polygon,MultiPoint
from shapely.ops import unary_union
from shapely import contains_xy
from print_heightfield_utils import write_stl
tree=ast.parse((OLD/'projection_furnished_v04/build_print.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='three_mf'],type_ignores=[]),'3mf','exec'))
I=json.loads((R/'source_inventory.json').read_text());rows=I['objects'];data=np.load(R/'approved_surfaces.npz');tris=data['triangles'];owners=data['owners'];P=.5;S=.0875;T=4.8
origin=np.array([-47.,-2.3]);nx=1660;ny=1280
def man(m):return mf.Manifold(mf.Mesh(np.asarray(m.vertices,np.float32),np.asarray(m.faces,np.uint32)))
def mesh(m):
 a=m.to_mesh();return trimesh.Trimesh(np.asarray(a.vert_properties)[:,:3],np.asarray(a.tri_verts),process=True)
def box(lo,hi):return mf.Manifold.cube(tuple(np.array(hi)-lo)).translate(tuple(lo))
def union(xs):return mf.Manifold.batch_boolean(xs,mf.OpType.Add)
def raster_tri(tt,h,zbase,constant=None):
 for v in tt:
  v=v.astype(float);v[:,:2]=(v[:,:2]-origin)/S;v[:,2]=T+(v[:,2]-zbase)/S
  lo=np.ceil(v[:,:2].min(0)/P-.5).astype(int);hi=np.floor(v[:,:2].max(0)/P-.5).astype(int)
  x0,y0=np.maximum(lo,0);x1,y1=np.minimum(hi,[nx-1,ny-1])
  if x1<x0 or y1<y0:continue
  ax,ay=v[0,:2];bx,by=v[1,:2];cx,cy=v[2,:2];den=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
  if abs(den)<=1e-9:continue # maximum envelope; vertical filling is intentional
  yy,xx=np.mgrid[y0:y1+1,x0:x1+1];px=(xx+.5)*P;py=(yy+.5)*P
  a=((by-cy)*(px-cx)+(cx-bx)*(py-cy))/den;b=((cy-ay)*(px-cx)+(ax-cx)*(py-cy))/den;c=1-a-b
  z=np.full(a.shape,constant) if constant is not None else a*v[0,2]+b*v[1,2]+c*v[2,2]
  ok=(a>=-1e-6)&(b>=-1e-6)&(c>=-1e-6);view=h[y0:y1+1,x0:x1+1];view[ok]=np.maximum(view[ok],z[ok])
def raster_poly(q,h,z):
 x0,y0,x1,y1=q.bounds;x0=max(0,int(x0/P)-1);y0=max(0,int(y0/P)-1);x1=min(nx,int(x1/P)+2);y1=min(ny,int(y1/P)+2)
 yy,xx=np.mgrid[y0:y1,x0:x1];ok=contains_xy(q,(xx+.5)*P,(yy+.5)*P);h[y0:y1,x0:x1][ok]=np.maximum(h[y0:y1,x0:x1][ok],z)
def category(o):
 n=o['name'].lower();cols=';'.join(o['collections']).lower()
 if o['hidden']:return 'hidden'
 if n.startswith('ph') or any(x in cols for x in ['footprint','reference planes','needs geometry','placeholder']):return 'qa_or_missing_detail'
 if any(x in n for x in ['folding_partition','foldingpartition']):return 'removable_partition'
 if n.startswith('patio_') and ('step_' in n or 'lower_landing' in n):return 'floor'
 if any(x in n for x in ['header','lintel','door','openleaf','openeastleaf']):return 'door_or_overhead_omitted'
 if o['name'] in ['A101_ground_slab','Gym_slab','A102_upper_slab','Terrace_walking_slab','REV22_TrophyHall_FloorInfill'] or ('patio' in n and ('slab' in n or 'platform' in n)):return 'floor'
 if any(x in cols for x in ['student','planting','site','roof','ceiling','light','graphics','artwork','door_hardware','architectural_details','av -']):return 'visual_detail_omitted'
 if 'bleacher' in n:return 'bleachers_omitted_r08'
 if any(x in cols for x in ['furniture','equipment','fixture','plumbing','locker','technology','reuse','fireplace']):
  if any(t in n for t in ['frame ','tape ','poster','flame','glass','glazing','partition_header','exhaust','vent louver','fittings','accessories','keyboard','mouse','nozzle','spool','filament','gantry','z screw','touchscreen','ui readout','ink label','label','loading slide','platen','control button','net cord','hoop','backboard','stanchion']):return 'fragile_furniture_detail_omitted'
  return 'supported_furniture'
 if cols in ['ground','upper','gym','stair'] or ('architecture' in cols) or o['name'].startswith('REV'):return 'structure'
 return 'unclassified_omitted'
cats=[category(o) for o in rows];objtri={int(i):tris[owners==i] for i in np.unique(owners) if cats[int(i)] in ['floor','structure','supported_furniture','door_or_overhead_omitted']}
(R/'print_disposition.json').write_text(json.dumps([dict(name=o['name'],category=c,source_bounds_m=o['bounds_m'],properties=o['properties']) for o,c in zip(rows,cats)],indent=2))
def make_level(level):
 zbase=0 if level=='ground' else 4.2672;floor=np.zeros((ny,nx),np.float32);struct=floor.copy();furn=floor.copy();accepted=[]
 for i,tt in objtri.items():
  o=rows[i];lo,hi=np.array(o['bounds_m']);cat=cats[i]
  if cat=='door_or_overhead_omitted':
   if level=='upper' and 'lintel' in o['name'].lower() and lo[2]<zbase and hi[2]>zbase+.1:cat='structure'
   else:continue
  if cat=='floor':
   if abs(hi[2]-zbase)<.06 or (level=='ground' and o['name'].startswith('Patio_')):raster_tri(tt,floor,zbase,T);accepted.append({'name':o['name'],'kind':cat})
  elif (lo[2]>=zbase-.35 or (level=='upper' and cat=='structure' and hi[2]>zbase+.1)) and lo[2]<zbase+3.2 and hi[2]>zbase+.05:
   if level=='ground' and lo[2]>3.2:continue
   if cat=='supported_furniture' and hi[2]>zbase+3.2:continue
   raster_tri(tt,struct if cat=='structure' else furn,zbase);accepted.append({'name':o['name'],'kind':cat})
 # Close construction seams under 1.5mm, retaining actual footprint and atrium voids.
 if level=='upper':struct=maximum_filter(struct,size=3)
 support=binary_closing((floor>0)|((struct>T) if level=='upper' else False),structure=np.ones((3,3)));floor[support]=T
 # Broadening mirrors established 0.5mm sampling/reinforcement convention.
 if level!='upper':struct=maximum_filter(struct,size=3)
 struct[~support]=0;struct=np.minimum(struct,T+4.2672/S)
 furn=maximum_filter(furn,size=3);furn[~support]=0;furn=np.ceil(np.minimum(furn,T+3.2/S)/.2)*.2
 h=np.maximum.reduce([floor,struct,furn]);h[~support]=0
 # Remove diagonal-only floor contacts before creating a manifold heightfield.
 for _ in range(15):
  a=h>0;d1=a[:-1,:-1]&a[1:,1:]&~a[:-1,1:]&~a[1:,:-1];d2=a[:-1,1:]&a[1:,:-1]&~a[:-1,:-1]&~a[1:,1:]
  if not(d1.any() or d2.any()):break
  yy,xx=np.where(d1);h[yy,xx+1]=T;yy,xx=np.where(d2);h[yy,xx]=T
 D=R/(level+'_furnished');D.mkdir(exist_ok=True);np.savez_compressed(D/'editable_heightfield.npz',height=h,floor=floor,structure=struct,furniture=furn,pitch_mm=P)
 (D/'source_membership.json').write_text(json.dumps(accepted,indent=2));print('RASTER',level,len(accepted),flush=True)
 write_stl(h,P,D/'raw_heightfield.stl');raw=trimesh.load_mesh(D/'raw_heightfield.stl',process=True);solid=man(raw).simplify(.003);assert solid.status()==mf.Error.NoError
 # Preserve the standalone solid exterior substitution from v05; patio free edges stay open.
 if level=='ground':
  polys=[]
  for name in ['A101_ground_slab','Gym_slab']:
   ix=next(i for i,o in enumerate(rows) if o['name']==name);tt=objtri[ix];top=tt[np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0])[:,2]>1e-9]
   polys.extend(Polygon((v[:,:2]-origin)/S) for v in top)
  footprint=unary_union(polys).buffer(1.5,join_style=2).buffer(-1.5,join_style=2);ring=footprint.difference(footprint.buffer(-3.5,join_style=2));per=np.zeros_like(h);raster_poly(ring,per,48.768);write_stl(per,P,D/'enclosure_intermediate.stl');enclosed=(solid+man(trimesh.load_mesh(D/'enclosure_intermediate.stl',process=True))).simplify(.003)
  export_set(enclosed,R/'ground_enclosed','Ground_Enclosed')
 export_set(solid,D,level.title()+'_Furnished')
 return solid
def check(m):
 assert m.is_watertight and m.is_winding_consistent
 bad=int(((m.face_normals[:,2]<-1e-5)&(m.triangles_center[:,2]>.02)).sum());assert bad==0,bad
 return dict(watertight=True,winding_consistent=True,components=len(m.split()),elevated_down_faces=bad,dimensions_mm=m.extents.tolist(),bounds_mm=m.bounds.tolist(),volume_mm3=float(m.volume),triangles=len(m.faces))
def export_set(solid,D,stem):
 D.mkdir(exist_ok=True);m=mesh(solid);report=check(m);m.export(D/(stem+'.stl'));re=trimesh.load_mesh(D/(stem+'.stl'),process=True);assert np.allclose(re.extents,m.extents,atol=.001);check(re)
 np.savez_compressed(D/'cad_mesh.npz',vertices=m.vertices,faces=m.faces)
 xs=np.linspace(m.bounds[0,0],m.bounds[1,0],4);ys=np.linspace(m.bounds[0,1],m.bounds[1,1],3);tile=D/'print_tiles';tile.mkdir(exist_ok=True);assembly=[];reports=[];vol=0
 for j in range(2):
  for i in range(3):
   piece=mesh(solid^box([xs[i],ys[j],-1],[xs[i+1],ys[j+1],100]));components=piece.split()
   for k,c in enumerate(components):
    name=f'{stem}_{chr(65+j)}{i+1}'+(f'_{k+1}' if len(components)>1 else '');off=c.bounds[0].copy();off[2]=0;c.apply_translation(-off);r=check(c);assert np.all(c.extents<=[290,300,315]);c.export(tile/(name+'.stl'));three_mf(tile/(name+'.3mf'),[(name,c,[0,0,0])]);vol+=c.volume;assembly.append((name,c,off));r.update(name=name,assembly_offset_mm=off.tolist());reports.append(r)
 assert abs(vol-m.volume)/m.volume<1e-5
 three_mf(D/(stem+'_Assembly.3mf'),assembly);report.update(source_sha256=I['source_sha256'],scale='1:87.5',units='mm',split_x_mm=xs.tolist(),split_y_mm=ys.tolist(),tiles=reports,tile_volume_relative_error=abs(vol-m.volume)/m.volume,floor_thickness_mm=T,physical_test=False)
 (D/'validation.json').write_text(json.dumps(report,indent=2));print('EXPORTED',stem,report['dimensions_mm'],len(reports),'tiles',flush=True)
if __name__=='__main__':
 for level in sys.argv[1:] or ['ground','upper']:make_level(level)
