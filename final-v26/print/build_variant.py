from pathlib import Path
import sys,json,ast,hashlib,zipfile,time
R=Path(__file__).parent;B=R.parent/'CampusCenter-print-r25-r01';OLD=B/'workflow_inputs'
sys.path[:0]=[str(B/'python_packages'),str(OLD)]
import numpy as np,trimesh,manifold3d as mf
from scipy.ndimage import maximum_filter
from shapely.geometry import MultiPoint
from print_heightfield_utils import write_stl
tree=ast.parse((B/'build_revised.py').read_text());names=['man','mesh','box','check','raster_tri']
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),'helpers','exec'))
tree=ast.parse((OLD/'projection_furnished_v04/build_print.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='three_mf'],type_ignores=[]),'3mf','exec'))
source=json.loads((R/'furniture_source.json').read_text());d=np.load(R/'furniture_surfaces.npz');tris=d['triangles'];owners=d['owners'];P=.5;S=.0875;T=4.8;origin=np.array([-47.,-2.3]);nx=1660;ny=1280
records=[];additions={}
for level in ['ground','upper']:
 base=np.load(B/(level+'_furnished')/'editable_heightfield.npz');support=base['height']>0;f=np.zeros((ny,nx),np.float32);zbase=0 if level=='ground' else 4.2672
 for i,row in enumerate(source['groups']):
  if not row['objects']:continue
  tt=tris[owners==i];bottom=float(tt[:,:,2].min())
  if abs(bottom-zbase)>.4:continue
  a=np.zeros_like(f);raster_tri(tt,a,zbase);a=maximum_filter(a,size=3);a=np.ceil(np.minimum(a,T+3.2/S)/.2)*.2
  before=int((a>T).sum());a[~support]=0;after=int((a>T).sum());assert after>0,row['id'];f=np.maximum(f,a)
  records.append({'id':row['id'],'level':level,'provenance':row['provenance'],'source_objects':row['objects'],'source_bounds_m':row['source_item']['bounds_m'],'supported_raster_cells':after,'clipped_outside_floor_cells':before-after,'simplification':'0.5 mm maximum surface envelope; vertically filled to base; 0.5 mm broadening each side; height cap 3.2 m; thin cavities/rods merged into solid support'})
 additions[level]=f
 np.savez_compressed(R/(level+'_furniture_addition.npz'),height=f,pitch_mm=P)
 print('FURNITURE_RASTER',level,int((f>T).sum()),flush=True)
def export(solid,folder,stem,baseline):
 D=R/folder;D.mkdir(exist_ok=True);m=mesh(solid)
 down=(m.face_normals[:,2]<-1e-5)&(m.triangles_center[:,2]>.02)
 if down.any():
  (D/'downface_diagnostic.json').write_text(json.dumps({'triangles':m.triangles[down].tolist(),'normals':m.face_normals[down].tolist(),'areas':m.area_faces[down].tolist()},indent=2));m.export(D/'debug_candidate.stl')
 report=check(m);old=json.loads((B/folder/'validation.json').read_text());assert np.allclose(m.bounds,old['bounds_mm'],atol=.003),(folder,m.bounds,old['bounds_mm'])
 m.export(D/(stem+'.stl'));np.savez_compressed(D/'cad_mesh.npz',vertices=m.vertices,faces=m.faces)
 xs=np.array(old['split_x_mm']);ys=np.array(old['split_y_mm']);tile=D/'print_tiles';tile.mkdir(exist_ok=True);assembly=[];tiles=[];changed=[];volume=0
 for j in range(2):
  for i in range(3):
   c=mesh(solid^box([xs[i],ys[j],-1],[xs[i+1],ys[j+1],100]));components=sorted(c.split(),key=lambda c:(-c.volume,*c.bounds[0]))
   for k,c in enumerate(components):
    name=f'{stem}_{chr(65+j)}{i+1}'+(f'_{k+1}' if len(components)>1 else '');off=c.bounds[0].copy();off[2]=0;c.apply_translation(-off);receipt=check(c);assert np.all(c.extents<=[290,300,315]);c.export(tile/(name+'.stl'));three_mf(tile/(name+'.3mf'),[(name,c,[0,0,0])]);assembly.append((name,c,off));volume+=c.volume;receipt.update(name=name,assembly_offset_mm=off.tolist());tiles.append(receipt)
   oldpieces=[x for x in old['tiles'] if x['name'].split('_')[-1]==f'{chr(65+j)}{i+1}' or '_'+f'{chr(65+j)}{i+1}'+'_' in x['name']]
   oldvol=sum(x['volume_mm3'] for x in oldpieces);newpieces=tiles[-len(components):];newvol=sum(x['volume_mm3'] for x in newpieces)
   changed.append({'region':f'{chr(65+j)}{i+1}','baseline_files':[x['name']+'.stl' for x in oldpieces],'variant_files':[x['name']+'.stl' for x in newpieces],'volume_delta_mm3':newvol-oldvol,'changed_geometry':abs(newvol-oldvol)>.01,'piece_numbering_note':'Suffixes assigned by descending component volume, then bounds. Use variant assembly offsets; source baseline suffix identity is not assumed.'})
 assert abs(volume-m.volume)/m.volume<1e-5;three_mf(D/(stem+'_Assembly.3mf'),assembly);report.update(scale='1:87.5',units='mm',split_x_mm=xs.tolist(),split_y_mm=ys.tolist(),tiles=tiles,baseline=baseline,geometry_operation='baseline solid union supported furniture envelope; no shell subtraction',physical_or_slicer_tested=False)
 if folder=='upper_enclosed':report['geometry_operation']='Bounded replacement of old Fitness envelope region with accepted floor/structure/glazing inputs, then supported B05/additional furniture unions; retain original upper solid outside replacement bounds.'
 (D/'validation.json').write_text(json.dumps(report,indent=2));return changed
manifest=[]
# Replace the complete corrected Fitness donor group; do not union corrected
# silhouettes over old barbell envelopes, which would retain retired bars.
old_inventory=json.loads((B/'source_inventory.json').read_text())['objects'];inventory_index={o['name']:i for i,o in enumerate(old_inventory)}
raw=np.load(B/'approved_surfaces.npz');oldtri=raw['triangles'];oldowners=raw['owners'];retired=set(source['fitness_correction']['complete_group_membership']);base=np.load(B/'upper_furnished/editable_heightfield.npz');remaining=np.zeros((ny,nx),np.float32)
for item in json.loads((B/'upper_furnished/source_membership.json').read_text()):
 if item['kind']!='supported_furniture' or item['name'] in retired:continue
 ix=inventory_index[item['name']];raster_tri(oldtri[oldowners==ix],remaining,4.2672)
remaining=maximum_filter(remaining,size=3);remaining[base['height']<=0]=0;remaining=np.ceil(np.minimum(remaining,T+3.2/S)/.2)*.2
corrected_height=np.maximum.reduce([base['floor'],base['structure'],remaining])
for _ in range(15):
 a=corrected_height>0;d1=a[:-1,:-1]&a[1:,1:]&~a[:-1,1:]&~a[1:,:-1];d2=a[:-1,1:]&a[1:,:-1]&~a[:-1,:-1]&~a[1:,1:]
 if not(d1.any() or d2.any()):break
 yy,xx=np.where(d1);corrected_height[yy,xx+1]=T;yy,xx=np.where(d2);corrected_height[yy,xx]=T
write_stl(corrected_height,P,R/'corrected_upper_base_raw.stl');corrected_upper_base=man(trimesh.load_mesh(R/'corrected_upper_base_raw.stl',process=True)).simplify(.003);assert corrected_upper_base.status()==mf.Error.NoError
adds=[]
for p in json.loads((OLD/'output_3d_v4/model_geometry.json').read_text())['parts']:
 if p.get('group')!='UPPER' or p.get('kind')!='glass':continue
 o=old_inventory[inventory_index[p['name']]] if p['name'] in inventory_index else None
 if not o or o['hidden'] or 'leaf' in p['name'].lower() or 'lintel' in p['name'].lower():continue
 lo,hi=np.array(o['bounds_m']);xy=(np.array([lo[:2],hi[:2]])-origin)/S;axis=int(np.argmax(xy[1]-xy[0]));c=(xy[0,1-axis]+xy[1,1-axis])/2;guard=p['name'].startswith(('Terrace_guard','Bridge_guard'));width=3 if guard else 3.5;top=16.8 if guard else 49.3;low=[xy[0,0],c-width/2,0] if axis==0 else [c-width/2,xy[0,1],0];high=[xy[1,0],c+width/2,top] if axis==0 else [c+width/2,xy[1,1],top]
 if high[axis]-low[axis]>.1:adds.append(box(low,high))
corrected_upper_base=(corrected_upper_base+mf.Manifold.batch_boolean(adds,mf.OpType.Add)).simplify(.003)
points=[np.array(old_inventory[inventory_index[n]]['bounds_m']) for n in retired if n in inventory_index]+[np.array(source['groups'][-1]['source_item']['bounds_m'])]
lo=np.min([p[0,:2] for p in points],axis=0);hi=np.max([p[1,:2] for p in points],axis=0);lo=np.floor(((lo-origin)/S-2)/P)*P;hi=np.ceil(((hi-origin)/S+2)/P)*P;replacement_region=box([*lo,-1],[*hi,100]);old_upper=man(trimesh.load_mesh(B/'upper_enclosed/Upper_Enclosed.stl',process=True))
corrected_upper_base=(old_upper-replacement_region)+(corrected_upper_base^replacement_region)
(R/'fitness_replacement_region.json').write_text(json.dumps({'xy_bounds_mm':[lo.tolist(),hi.tolist()],'method':'Replace complete old/corrected Fitness envelope bounds plus 2 mm reinforcement margin; retain original upper solid outside this bounded region. Reconstruction retains accepted floor/structure/glazing inputs.'},indent=2))
for folder,stem,level in [('ground_furnished','Ground_Furnished','ground'),('ground_enclosed','Ground_Enclosed','ground'),('ground_acrylic','Ground_Acrylic','ground'),('upper_enclosed','Upper_Enclosed','upper')]:
 h=additions[level].copy()
 if folder=='ground_acrylic':
  for p in json.loads((B/'ground_acrylic/glazing_schedule.json').read_text())['panes']:
   half=p['slot_width_mm']/2+.5;start=p['start']-.8;end=p['end']+.8;center=p['center'];lo=[start,center-half] if p['axis']==0 else [center-half,start];hi=[end,center+half] if p['axis']==0 else [center+half,end];x0,y0=np.floor(np.array(lo)/P).astype(int);x1,y1=np.ceil(np.array(hi)/P).astype(int);h[y0:y1,x0:x1]=0
  np.savez_compressed(R/'acrylic_furniture_addition.npz',height=h,pitch_mm=P)
 temp=R/(folder+'_addition_raw.stl');write_stl(h,P,temp);addition=man(trimesh.load_mesh(temp,process=True)).simplify(.003)
 original=corrected_upper_base if level=='upper' else man(trimesh.load_mesh(B/folder/(stem+'.stl'),process=True));variant=(original+addition).simplify(.003)
 # Remove numerically collinear corners within the existing bounded cleanup convention.
 m=mesh(variant);m.vertices=np.round(m.vertices,3);m.merge_vertices();m.update_faces(m.nondegenerate_faces());candidate=man(m).simplify(.005)
 if candidate.status()==mf.Error.NoError:variant=candidate
 else:variant=variant.simplify(.005)
 assert variant.status()==mf.Error.NoError
 changes=export(variant,folder,stem,str(B/folder/(stem+'.stl')));manifest.append({'family':folder,'regions':changes});print('EXPORTED',folder,flush=True)
# Separate matched miniature assembly: add supported downsampled furniture, leaving roof/interface recipe intact.
D=R/'stacked_1_350';D.mkdir(exist_ok=True);old=np.load(B/'stacked_1_350/editable_assembly_grids.npz');levels={x:old[x].copy() for x in ['ground','upper','roof']};z={'ground':0,'upper':12.192,'roof':23.077714285714286}
for level in ['ground','upper']:
 f=additions[level].reshape(640,2,830,2).max(axis=(1,3))/4;f=maximum_filter(f,size=3);f[levels[level]<=0]=0
 ceiling=z['upper'] if level=='ground' else z['roof']-z['upper'];f=np.minimum(f,ceiling);levels[level]=np.maximum(levels[level],f)
solids={};assembly=[];checks={}
for level,h in levels.items():
 name='Stack_'+level.title();write_stl(h,.25,D/(name+'_raw.stl'));so=man(trimesh.load_mesh(D/(name+'_raw.stl'),process=True)).simplify(.003);m=mesh(so);checks[level]=check(m);assert np.all(m.extents<=[290,300,315]);m.export(D/(name+'.stl'));three_mf(D/(name+'.3mf'),[(name,m,[0,0,0])]);solids[level]=so;assembly.append((name,m,[0,0,z[level]]))
interfaces=[]
for low,up in [('ground','upper'),('upper','roof')]:
 offset=z[up]-z[low];penetration=float((solids[low]^solids[up].translate((0,0,offset))).volume());assert penetration<.002
 contact=(levels[low]>=offset-.003)&(levels[up]>0);hull=MultiPoint(np.column_stack(np.where(contact))[:,::-1]*.25).convex_hull;cent=mesh(solids[up]).center_mass[:2];assert hull.covers(MultiPoint([cent]).convex_hull)
 interfaces.append({'lower':low,'upper':up,'penetration_mm3':penetration,'contact_area_mm2':float(contact.sum()*.25*.25),'centroid_supported':True})
three_mf(D/'Stack_Assembly.3mf',assembly);np.savez_compressed(D/'editable_assembly_grids.npz',**levels,pitch_mm=.25);(D/'validation.json').write_text(json.dumps({'scale':'1:350','assembly_z_mm':z,'interfaces':interfaces,'meshes':checks,'roof_unchanged_grid':bool(np.array_equal(levels['roof'],old['roof'])),'physical_or_slicer_tested':False},indent=2))
(R/'changed_piece_manifest.json').write_text(json.dumps({'source_sha256':source['sha256'],'furniture_groups_carried':records,'omitted_groups':[{'id':x['id'],'reason':x['reason']} for x in source['groups'] if not x['objects']],'art_presentations_omitted':11,'families':manifest,'scale_note':'Estimated donor/product geometry remains estimated; source room envelopes preserved.'},indent=2));print('VARIANT_COMPLETE',len(records),flush=True)
