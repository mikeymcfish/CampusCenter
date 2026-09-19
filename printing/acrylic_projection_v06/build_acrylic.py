from pathlib import Path
import sys,json,ast,hashlib,zipfile,csv
R=Path(__file__).parent;ROOT=R.parent;D=R/'print';D.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'projection_furnished_v04/python_packages'))
import numpy as np,trimesh,manifold3d as mf
tree=ast.parse((ROOT/'projection_furnished_v04/build_print.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='three_mf'],type_ignores=[]),'3mf','exec'))
parts=json.loads((ROOT/'output_3d_v4/model_geometry.json').read_text())['parts'];byname={p['name']:p for p in parts}
prior=json.loads((ROOT/'projection_enclosed_v05/ground/print_validation.json').read_text())
SRC=ROOT/'projection_enclosed_v05/ground'/prior['filename'];initial=hashlib.sha256(SRC.read_bytes()).hexdigest()
SLOT=1.85;ACRYLIC=25.4/16;BASE=4.8;FRAME=5.2
def man(m):return mf.Manifold(mf.Mesh(np.asarray(m.vertices,np.float32),np.asarray(m.faces,np.uint32)))
def mesh(m):
 a=m.to_mesh();return trimesh.Trimesh(np.asarray(a.vert_properties)[:,:3],np.asarray(a.tri_verts),process=True)
def box(lo,hi):return mf.Manifold.cube(tuple(np.array(hi)-lo)).translate(tuple(lo))
def bar(axis,a,b,c,w,z0,z1):
 return box([a,c-w/2,z0],[b,c+w/2,z1]) if axis==0 else box([c-w/2,a,z0],[c+w/2,b,z1])
targets=[];seen=set()
for p in parts:
 if p.get('group')!='GROUND' or p.get('kind')!='glass':continue
 name=p['name']
 if 'Patio' in name:continue # Guards are optional accessories, not room windows.
 if 'leaf' in name:
  prefix=name.split('_door')[0];idx=name.split('_door')[1].split('_')[0];q=byname.get(prefix+'_lintel'+idx)
  if not q:raise RuntimeError('No closed glazing datum for '+name)
  if q['name'] in seen:continue
  seen.add(q['name']);bounds=np.asarray(q['poly']);z=p.get('z',0);top=z+p.get('height',0);kind='glazed door light'
 else:
  if 'lintel' in name:continue # Door light handled using its closed doorway datum.
  bounds=np.asarray(p['poly']);z=p['z'];top=z+p['height'];kind='fixed glazing'
 lo=(bounds.min(0)+[47000,2300])/87.5;hi=(bounds.max(0)+[47000,2300])/87.5;axis=int(np.argmax(hi-lo));c=(lo[1-axis]+hi[1-axis])/2
 targets.append({'source':name,'axis':axis,'start':lo[axis],'end':hi[axis],'center':c,'sill':max(BASE+3,BASE+z/87.5),'pane_top':min(48.768,BASE+top/87.5),'kind':kind})
# Split glazing at plate boundaries so inserts stay local to printable pieces.
rows=[]
for t in targets:
 cuts=prior['split_x_mm'] if t['axis']==0 else prior['split_y_mm'];cs=[t['start']]+[x for x in cuts if t['start']+.05<x<t['end']-.05]+[t['end']]
 for a,b in zip(cs,cs[1:]):
  if b-a<.8:raise RuntimeError('Submillimetre glazing fragment')
  q=dict(t,start=a,end=b);q['id']=f'G{len(rows)+1:02d}';rows.append(q)
m=trimesh.load_mesh(SRC,process=True);solid=man(m);cuts=[];adds=[];slots=[];panes=[]
for q in rows:
 ax=q['axis'];a=q['start'];b=q['end'];c=q['center'];sill=q['sill'];L=b-a;jamb=min(1.8,L*.20);engage=jamb*.5;bottom=sill-2.4
 # Remove the solid glazing substitute and any unsupported head above it.
 cuts.append(bar(ax,a,b,c,7.5,sill,90))
 # Solid plinth with open-top jambs. Each added feature extends to the bed.
 adds.extend([bar(ax,a,b,c,FRAME,0,sill),bar(ax,a,a+jamb,c,FRAME,0,48.768),bar(ax,b-jamb,b,c,FRAME,0,48.768)])
 slots.append(bar(ax,a+jamb-engage,b-jamb+engage,c,SLOT,bottom,90))
 pw=L-2*jamb+2*engage-.20;pt=max(sill+1,q['pane_top']);ph=pt-bottom
 pane=bar(ax,a+jamb-engage+.1,b-jamb+engage-.1,c,ACRYLIC,bottom,pt);panes.append(pane)
 q.update(slot_width_mm=SLOT,acrylic_nominal_mm=ACRYLIC,cut_width_mm=pw,cut_height_mm=ph,seat_z_mm=bottom,side_engagement_mm=engage-.1,frame_width_mm=FRAME)
 q['center_xy_mm']=[(a+b)/2,c] if ax==0 else [c,(a+b)/2]
print('GLAZING',len(targets),'SEGMENTS',len(rows),flush=True)
union=lambda xs:mf.Manifold.batch_boolean(xs,mf.OpType.Add)
solid=(((solid-union(cuts))+union(adds))-union(slots)).simplify(.001)
assert solid.status()==mf.Error.NoError
from print_edits_r08 import apply_edits
solid=apply_edits(solid,ROOT,D)
m=mesh(solid)
def check(m,label):
 assert m.is_watertight and m.is_winding_consistent,label
 nc=len(m.split());bad=int(((m.face_normals[:,2]<-1e-5)&(m.triangles_center[:,2]>.02)).sum())
 assert nc==1 and bad==0,(label,nc,bad)
 return {'watertight':True,'components':nc,'elevated_downward_faces':bad,'dimensions_mm':m.extents.tolist(),'volume_mm3':float(m.volume)}
report=check(m,'full');name='Campus_Center_Ground_Acrylic_1_87p5';m.export(D/(name+'.stl'));np.savez_compressed(D/'cad_mesh.npz',vertices=m.vertices,faces=m.faces)
mesh(union(panes)).export(D/'Acrylic_Panes_Reference_ONLY.stl')
# Nominal pane fit and full vertical insertion envelope must be free of structure.
for q,pane in zip(rows,panes):
 assert (solid^pane).volume()<.001,(q['id'],'pane collision')
 env=bar(q['axis'],q['start']+min(1.8,(q['end']-q['start'])*.2)/2+.1,q['end']-min(1.8,(q['end']-q['start'])*.2)/2-.1,q['center'],ACRYLIC,q['seat_z_mm'],85)
 assert (solid^env).volume()<.001,(q['id'],'insertion blocked')
out=D/'print_tiles';out.mkdir(exist_ok=True);assembly=[];tile_rows=[];vol=0
xs=list(prior['split_x_mm']);ys=list(prior['split_y_mm']);xs[0]=min(xs[0],m.bounds[0,0]);xs[-1]=max(xs[-1],m.bounds[1,0]);ys[0]=min(ys[0],m.bounds[0,1]);ys[-1]=max(ys[-1],m.bounds[1,1])
for j in range(2):
 for i in range(3):
  p=mesh(solid^box([xs[i],ys[j],-1],[xs[i+1],ys[j+1],90]));r=check(p,f'{j}{i}');off=p.bounds[0].copy();off[2]=0;p.apply_translation(-off);stem=f'Acrylic_{chr(65+j)}{i+1}'
  p.export(out/(stem+'.stl'));three_mf(out/(stem+'.3mf'),[(stem,p,[0,0,0])]);assembly.append((stem,p,off));vol+=p.volume
  r.update(name=stem,assembly_offset_mm=off.tolist());tile_rows.append(r)
assert abs(vol-m.volume)/m.volume<1e-5
three_mf(D/'Campus_Center_Acrylic_Assembly.3mf',assembly)
# Fit coupon: five open-ended, top-loading slots and a plain 1.5875 mm gauge.
coupon=box([0,0,0],[70,22,8]);widths=[1.65,1.75,1.85,1.95,2.05]
for i,w in enumerate(widths):coupon=coupon-box([7+i*13-w/2,4,2.4],[7+i*13+w/2,22.1,10])
cm=mesh(coupon);check(cm,'coupon');cm.export(D/'Acrylic_Fit_Coupon.stl');three_mf(D/'Acrylic_Fit_Coupon.3mf',[('Fit coupon',cm,[0,0,0])])
with (D/'Acrylic_Cut_List.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=['id','source','kind','cut_width_mm','cut_height_mm','acrylic_nominal_mm','slot_width_mm']);writer.writeheader();writer.writerows([{k:q[k] for k in writer.fieldnames} for q in rows])
(D/'glazing_schedule.json').write_text(json.dumps(rows,indent=2))
report.update(status='passed',scale='1:87.5',source=str(SRC),source_sha256=initial,source_unchanged=hashlib.sha256(SRC.read_bytes()).hexdigest()==initial,glazing_source_count=len(targets),pane_count=len(rows),slot_width_mm=SLOT,nominal_acrylic_mm=ACRYLIC,top_insertion_verified=True,split_x_mm=xs,split_y_mm=ys,tiles=tile_rows,furnished_volume_mm3=float(m.volume),physical_fit_tested=False)
(D/'print_validation.json').write_text(json.dumps(report,indent=2));print('ACRYLIC_BUILD_PASSED',m.extents,len(m.faces),flush=True)
