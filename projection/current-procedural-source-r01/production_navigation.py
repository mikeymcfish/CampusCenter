from production_common import *
import heapq,collections

NAVROOT=PROD/'navigation';NAVROOT.mkdir(exist_ok=True)
PITCH=.25;CHAR_RADIUS=2.;HALO=.20;CLEARANCE=.60

def square_coverage(px,shape):
 lo=np.maximum(np.floor(px.min(0)).astype(int)-1,0);hi=np.minimum(np.ceil(px.max(0)).astype(int)+1,np.array(shape)-1)
 x0,y0=lo;x1,y1=hi
 if x1<x0 or y1<y0:return None
 yy,xx=np.mgrid[y0:y1+1,x0:x1+1];covered=np.ones(xx.shape,bool)
 for axis in [[1.,0.],[0.,1.]]+[[-(px[(i+1)%3,1]-px[i,1]),px[(i+1)%3,0]-px[i,0]] for i in range(3)]:
  axis=np.asarray(axis);proj=px@axis;p=xx*axis[0]+yy*axis[1];a=p+min(0,axis[0])+min(0,axis[1]);b=p+max(0,axis[0])+max(0,axis[1]);eps=1e-8*max(1,np.linalg.norm(axis));covered&=(b>=proj.min()-eps)&(a<=proj.max()+eps)
 return (int(x0),int(y0),int(x1),int(y1)),covered

def inflate(blocked,radius):
 cells=math.ceil(radius/PITCH);padded=np.pad(blocked,cells,constant_values=True);H,W=blocked.shape;out=blocked.copy()
 for dy in range(-cells,cells+1):
  for dx in range(-cells,cells+1):
   if dx*dx+dy*dy<=(radius/PITCH)**2+1e-9:out|=padded[cells+dy:cells+dy+H,cells+dx:cells+dx+W]
 return out

def components_by_runs(nav):
 H,W=nav.shape;parent=[];runs=[];last=[]
 def find(x):
  while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
  return x
 for y,row in enumerate(nav):
  diff=np.diff(np.pad(row.astype(np.int8),(1,1)));starts=np.flatnonzero(diff==1);ends=np.flatnonzero(diff==-1);current=[];j=0
  for x0,x1 in zip(starts,ends):
   idx=len(parent);parent.append(idx);record=(int(x0),int(x1),idx);current.append(record);runs.append((y,int(x0),int(x1),idx))
   while j<len(last) and last[j][1]<=x0:j+=1
   k=j
   while k<len(last) and last[k][0]<x1:
    ra,rb=find(idx),find(last[k][2]);parent[ra]=rb;k+=1
  last=current
 roots=collections.Counter()
 for y,x0,x1,i in runs:roots[find(i)]+=x1-x0
 order={r:i+1 for i,(r,n) in enumerate(roots.most_common())};labels=np.zeros(nav.shape,np.uint16)
 for y,x0,x1,i in runs:labels[y,x0:x1]=order[find(i)]
 return labels,[{'component':order[r],'safe_center_cells':n,'safe_center_area_mm2':n*(2*PITCH)**2} for r,n in roots.most_common()]

def build_navigation():
 cfg=config();v,u,n,parts=parse_obj(cfg['obj']);origin=np.floor(v[:,:2].min(0))-3;hi=np.ceil(v[:,:2].max(0))+3;WH=np.ceil((hi-origin)/PITCH).astype(int);W,H=map(int,WH);W+=W%2;H+=H%2
 floor=np.zeros((H,W),bool);obstacle=np.zeros((H,W),bool);counts={};triangle_count=0
 for name,p in parts.items():
  if name=='HangingLoops':continue
  tris=v[p['f']];_,norm,area=geom(v,p['f']);fc=oc=0
  for i,(t,nn) in enumerate(zip(tris,norm)):
   px=(t[:,:2]-origin)/PITCH
   is_floor=name=='Opaque' and nn[2]>.5 and t[:,2].max()<=5.0 and t[:,2].min()>=4.19
   is_obstacle=t[:,2].max()>5.0
   if is_floor:
    patch=barypatch(px,np.array([W,H]))
    if patch is not None:
     (x0,y0,x1,y1),a,b,c,ok=patch;floor[y0:y1+1,x0:x1+1]|=ok;fc+=1
   if is_obstacle:
    patch=square_coverage(px,[W,H])
    if patch is not None:
     (x0,y0,x1,y1),ok=patch;obstacle[y0:y1+1,x0:x1+1]|=ok;oc+=1
   if i%20000==0:print('NAV footprint extraction',name,i,'/',len(tris),flush=True)
  counts[name]={'floor_triangles':fc,'obstacle_projected_triangles':oc};triangle_count+=len(tris)
 # The geometry is never edited to connect a closed door or wall.
 blocked=obstacle|~floor;inflation=CHAR_RADIUS+HALO+CLEARANCE+math.sqrt(2)*PITCH+.02
 safe=~inflate(blocked,inflation)
 coarse=safe.reshape(H//2,2,W//2,2).all((1,3));labels,comps=components_by_runs(coarse)
 for k,arr in [('floor',floor),('obstacles',obstacle),('blocked',blocked),('safe_fine',safe),('safe_coarse',coarse),('components',labels)]:np.save(NAVROOT/(k+'.npy'),arr)
 np.save(NAVROOT/'origin.npy',origin)
 meaningful=[c for c in comps if c['safe_center_area_mm2']>=30]
 qa={'status':'Real frozen mesh footprints extracted; components inspected','source_OBJ':str(cfg['obj']),'source_OBJ_sha256':sha(cfg['obj']),
     'floor_rule':'Union of actual Opaque upward floor triangles at model Z4.19..5.0mm; gym/corridor raised floor included',
     'obstacle_rule':'Union of every opaque and glazing triangle projected in XY with maximum Z>5.0mm, including full tabletop overhangs, furniture, walls, columns and closed glazed door panes',
     'floor_center_pitch_mm':PITCH,'obstacle_conservative_pixel_square_intersection':True,'navigation_coarse_pitch_mm':PITCH*2,
     'character_visible_body_radius_mm':CHAR_RADIUS,'halo_radius_extra_mm':HALO,'clearance_mm':CLEARANCE,'total_erosion_including_grid_and_UV_error_mm':inflation,
     'triangle_counts':counts,'all_connected_components':comps,'meaningful_connected_components':meaningful,
     'physically_disconnected_regions':len(meaningful)>1,'doors_or_walls_removed_to_force_routes':False,
     'origin_mm':origin.tolist(),'grid_dimensions':[W,H],'source_geometry_and_UV_changes':[]}
 (NAVROOT/'Navigation_Contract.json').write_text(json.dumps(qa,indent=2))
 rgb=np.zeros((H,W,3),np.uint8);rgb[floor]=[35,53,65];rgb[obstacle]=[195,84,88];rgb[safe]=[43,173,139];Image.fromarray(rgb[::-1]).save(NAVROOT/'Floor_Obstacles_And_Clearance_Diagnostic.png')
 small=np.zeros((*labels.shape,3),np.uint8)
 for c in meaningful:
  i=c['component'];small[labels==i]=np.uint8([65+(i*67)%170,65+(i*97)%170,65+(i*47)%170])
 Image.fromarray(small[::-1]).save(NAVROOT/'Connected_Component_Diagnostic.png')
 print('NAVIGATION COMPONENTS',len(meaningful),'meaningful /',len(comps),'all',flush=True)
 print(json.dumps(meaningful,indent=2),flush=True)
 return qa

if __name__=='__main__':build_navigation()
