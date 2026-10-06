from geometry_utils import *
from PIL import Image,ImageDraw
from production_navigation import square_coverage,components_by_runs
import time

ROOT=R/'madmapper_ripple_R02';WHOLE='--whole-model' in sys.argv;T=ROOT/('whole_model' if WHOLE else 'test01');T.mkdir(parents=True,exist_ok=True)
PITCH=.5;BASE=4.2;LOW=4.25;HIGH=5.2
actors=json.loads((R/'print_revision02/native_selected_actors.json').read_text())
cache=json.loads((R/'print_revision02/actor_mesh_manifest.json').read_text())
contract=json.loads((R/'print_revision02/deliverables/projection/Projection_Coordinate_Contract.json').read_text())
canvas=np.array(contract['canvas_mm']);center=np.array(contract['center_mm'])
boxes=[]
for q in contract['rooms_reference']:
    x0,y0,x1,y1=q['mask_bounds_px']
    b=np.array([[center[0]-canvas[0]/2+x0/2048*canvas[0],center[1]+canvas[1]/2-y1/1572*canvas[1]],
                [center[0]-canvas[0]/2+x1/2048*canvas[0],center[1]+canvas[1]/2-y0/1572*canvas[1]]])
    boxes.append((q['number'],b,float(np.prod(b[1]-b[0]))))
boxes.sort(key=lambda q:q[2])
walls={q['segment']:np.array(q['native_blender_bounds_cm']) for q in json.loads((R/'print_revision02/Gym_Perimeter_and_Hanging_QA.json').read_text())['gym_perimeter_segments']}
gym=(np.array([[walls['West north'][1,0],walls['South west'][1,1]],[walls['East'][0,0],walls['North'][0,1]]])+[4700,230])*.1
print('Verified gym interior',gym.tolist(),flush=True)
# Physical footprint has no tabletop holes: use the closed printed base's slice.
v,u,n,parts=__import__('uvprep_common').parse_obj(R/'madmapper_p02/deliverables/assembly_1_100/CampusCenter_P02_Assembly_1_100_UV01.obj')
op=trimesh.Trimesh(v,parts['Opaque']['f'],process=False);op.remove_unreferenced_vertices()
gl=trimesh.Trimesh(v,parts['Glazing']['f'],process=False);gl.remove_unreferenced_vertices()
s=mf.Manifold(mf.Mesh64(op.vertices,op.faces.astype(np.uint64)))+mf.Manifold(mf.Mesh64(gl.vertices,gl.faces.astype(np.uint64)))
polys=s.slice(.1).to_polygons()
orig=np.floor((v.min(0)[:2]-1)/PITCH)*PITCH
shape=np.ceil((v.max(0)[:2]+1-orig)/PITCH).astype(int)
W,H=shape; img=Image.new('L',(W,H));dr=ImageDraw.Draw(img)
for p in polys:
    p=np.array(p);area=np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1))
    dr.polygon([tuple(x) for x in (p-orig)/PITCH-.5],fill=255 if area>0 else 0)
footprint=np.asarray(img)>0
yy,xx=np.mgrid[:H,:W];wx=orig[0]+(xx+.5)*PITCH;wy=orig[1]+(yy+.5)*PITCH
rid=np.zeros((H,W),np.int16)
for name,b,_ in reversed(boxes):
    if name.isdigit():rid[(wx>=b[0,0])&(wx<=b[1,0])&(wy>=b[0,1])&(wy<=b[1,1])]=int(name)
rid[(wx>=gym[0,0])&(wx<=gym[1,0])&(wy>=gym[0,1])&(wy<=gym[1,1])]=999
requested={999:('GYM','Simple verified gym basin'),102:('Commons','Irregular Commons basin with restored fireplace'),108:('Innovation','Furnished Innovation basin; water around native legs')}
if WHOLE:requested={-1:('Whole_Model','Entire physical base footprint; native near-floor barriers')}

def clip(poly,z,greater):
    out=[]
    for a,b in zip(poly,np.roll(poly,-1,axis=0)):
        aa=a[2]>=z if greater else a[2]<=z;bb=b[2]>=z if greater else b[2]<=z
        if aa:out.append(a)
        if aa!=bb:out.append(a+(z-a[2])/(b[2]-a[2])*(b-a))
    return np.array(out)

roi=[]
for number,(name,title) in requested.items():
    selected=footprint if number==-1 else (rid==number)&footprint
    y,x=np.where(selected);x0=max(int(x.min())-2,0);x1=min(int(x.max())+3,W);y0=max(int(y.min())-2,0);y1=min(int(y.max())+3,H)
    roi.append({'number':number,'name':name,'title':title,'slice':(x0,y0,x1,y1),
       'origin':orig+[x0,y0]*np.array(PITCH),'selection':selected[y0:y1,x0:x1],
       'native_architecture':np.zeros((y1-y0,x1-x0),bool),'native_furniture_legs':np.zeros((y1-y0,x1-x0),bool),
       'native_tabletop_projection':np.zeros((y1-y0,x1-x0),bool),'actor_audit':[]})

def raster(triangles,origin,dest):
    h,w=dest.shape
    for t in triangles:
        p=clip(t,LOW,True)
        if len(p)<3:continue
        p=clip(p,HIGH,False)
        if len(p)<3:continue
        for j in range(1,len(p)-1):
            result=square_coverage((p[[0,j,j+1],:2]-origin)/PITCH,[w,h])
            if result is not None:
                (x0,y0,x1,y1),ok=result;dest[y0:y1+1,x0:x1+1]|=ok

included=0;floor_finish_exclusions=[]
for i,(a,c) in enumerate(zip(actors,cache)):
    label=a['label'];text=(label+' '+a['mesh']+' '+a.get('folder','')).lower()
    architecture=any(x in (label+' '+str(a.get('tags',[]))) for x in ['Architecture','Doors','Stair','commons_architecture','architectural_glazing'])
    if label=='Architect_Finishes_v02':continue
    if not architecture and any(s in text for s in ('bleacher','grass','shrub','tree','foliage','schoolapron','schoolfoundation','earth','exteriorsidewalk','site_','roller','diffuser','housing','led','ceiling','floorfinish','trophy_illumination','sky','balloon','water','ember')):continue
    # Manifest bounds describe Unreal's pre-reflection frame. Cached vertices
    # already use right-handed reflected Y. Reflect/swap their AABB first.
    ub=np.array(c['triangle_bounds_cm'])
    b=np.array([[ub[0,0],-ub[1,1],ub[0,2]],[ub[1,0],-ub[0,1],ub[1,2]]])
    b=(b+[4700,230,0])*.1;b[:,2]+=BASE
    is_table=not architecture and any(s in text for s in ('table','desk'))
    near_water=bool(b[0,2]<=HIGH and b[1,2]>=LOW)
    tabletop_test=bool(is_table and b[0,2]<18 and b[1,2]>HIGH)
    if not (near_water or tabletop_test):continue
    targets=[]
    for q in roi:
        xy0=q['origin'];xy1=xy0+np.array(q['selection'].shape[::-1])*PITCH
        if np.all(b[1,:2]>=xy0) and np.all(b[0,:2]<=xy1):targets.append(q)
    if not targets:continue
    raw=np.load(c['file']);av=(raw['vertices']+[4700,230,0])*.1;av[:,2]+=BASE;faces=raw['faces'];tri=av[faces]
    selected=(tri[:,:,2].max(1)>=LOW)&(tri[:,:,2].min(1)<=HIGH)
    # Native finish floors are the basin substrate, not a solid wall above it.
    # For example ILab_Designed_Details contains a 1cm epoxy floor slab.
    slots=a.get('slots',[]);finish_ids=[k for k,q in enumerate(slots) if 'floor' in q.get('name','').lower()]
    if finish_ids:
        excluded=np.isin(raw['materials'],finish_ids)&selected
        if excluded.any():floor_finish_exclusions.append({'actor':a['actor'],'label':label,'finish_material_names':[slots[k]['name'] for k in finish_ids],'excluded_floor_substrate_triangles':int(excluded.sum())})
        selected&=~excluded
    for q in targets:
        arr=q['native_architecture'] if architecture else q['native_furniture_legs'];before=int(arr.sum());raster(tri[selected],q['origin'],arr)
        used=int(arr.sum())-before
        if used:q['actor_audit'].append({'actor':a['actor'],'label':label,'category':'native wall/glazing/door' if architecture else 'native near-floor furniture/fixture','source_sha256':hashlib.sha256(Path(c['file']).read_bytes()).hexdigest(),'new_obstacle_cells':used,'retained_slab_triangles':int(selected.sum())})
        if is_table:
            top=(tri[:,:,2].min(1)>HIGH)&(tri[:,:,2].min(1)<18)&(tri[:,:,2].max(1)<18)
            arr=q['native_tabletop_projection'];h,w=arr.shape
            top_before=int(arr.sum())
            for t in tri[top]:
                result=square_coverage((t[:,:2]-q['origin'])/PITCH,[w,h])
                if result is not None:
                    (x0,y0,x1,y1),ok=result;arr[y0:y1+1,x0:x1+1]|=ok
            top_used=int(arr.sum())-top_before
            if top_used:q['actor_audit'].append({'actor':a['actor'],'label':label,'category':'native tabletop/overhang; intentionally not a water obstacle','source_sha256':hashlib.sha256(Path(c['file']).read_bytes()).hexdigest(),'new_obstacle_cells':0,'new_tabletop_reference_cells':top_used})
    included+=1
    if included%20==0:print('Native shallow-water obstacle actors',included,'source index',i,flush=True)

if WHOLE:
    whole=roi[0];x0,y0,x1,y1=whole['slice'];local_rid=rid[y0:y1,x0:x1];water=whole['selection']&~whole['native_architecture']&~whole['native_furniture_legs']
    np.savez_compressed(T/'Whole_Native_Obstacle_And_Ownership_Grid.npz',footprint=whole['selection'],architecture=whole['native_architecture'],furniture_legs=whole['native_furniture_legs'],tabletop_projection=whole['native_tabletop_projection'],room_reference_owner=local_rid,origin=whole['origin'],pitch=PITCH)
    labels_manifest=[];roi=[];coverage=np.zeros_like(water)
    for number in sorted(np.unique(local_rid[water])):
        labels,comps=components_by_runs(water&(local_rid==number))
        for comp in comps:
            component=comp['component'];domain=labels==component
            if domain.sum()<8:continue
            ys,xs=np.where(domain);xa=max(int(xs.min())-1,0);xb=min(int(xs.max())+2,domain.shape[1]);ya=max(int(ys.min())-1,0);yb=min(int(ys.max())+2,domain.shape[0]);sl=np.s_[ya:yb,xa:xb]
            name=('GYM' if number==999 else ('Neutral' if number==0 else 'R'+str(number)))+f'_B{component:03d}'
            select=whole['selection'][sl]&(local_rid[sl]==number)
            q={'number':int(number),'name':name,'title':f'Independent basin {name}',
               'slice':(x0+xa,y0+ya,x0+xb,y0+yb),'origin':whole['origin']+np.array([xa,ya])*PITCH,
               'selection':select,'native_architecture':whole['native_architecture'][sl],
               'native_furniture_legs':whole['native_furniture_legs'][sl],
               'native_tabletop_projection':whole['native_tabletop_projection'][sl],
               'actor_audit':whole['actor_audit'],'domain_override':domain[sl]}
            roi.append(q);coverage|=domain;labels_manifest.append({'name':name,'reference_owner':int(number),'active_cells':int(domain.sum())})
    np.save(T/'Animated_Meaningful_Basin_Coverage.npy',coverage)
    (T/'Whole_Model_Coverage_Preflight.json').write_text(json.dumps({'status':'Native physics domains expanded across full physical base footprint','physical_floor_cells':int(whole['selection'].sum()),'native_water_free_cells':int(water.sum()),'meaningful_basin_cells':int(coverage.sum()),'unexcited_smaller_than_2mm2_cells':int((water&~coverage).sum()),'meaningful_basins':len(roi),'reference_selections_with_meaningful_basins':sorted(set(q['number'] for q in roi)),'basins':labels_manifest,'old_test01_or_receiver_or_media_changed':False,'scope_limit':'Room grouping remains frozen coarse reference selections with explicit artistic boundaries; actual native near-floor barriers participate in each independent solver. Neutral/unassigned actual floor is also included. This is not a new R29 semantic room-boundary audit.'},indent=2))
    print('WHOLE MODEL INDEPENDENT BASINS',len(roi),'covered cells',int(coverage.sum()),'of water-free',int(water.sum()),flush=True)
report=[]
for q in roi:
    selection=q['selection'];arch=q['native_architecture'];legs=q['native_furniture_legs'];domain=q.get('domain_override',selection&~arch&~legs)
    assert domain.sum()>=8
    closure=((np.roll(rid,1,0)!=rid)|(np.roll(rid,-1,0)!=rid)|(np.roll(rid,1,1)!=rid)|(np.roll(rid,-1,1)!=rid))
    x0,y0,x1,y1=q['slice'];closure=closure[y0:y1,x0:x1]&selection&~arch
    np.savez_compressed(T/(q['name']+'_Simulation_Domain.npz'),domain=domain,selection=selection,architecture=arch,furniture_legs=legs,tabletop_projection=q['native_tabletop_projection'],artistic_reference_boundary=closure,origin=q['origin'],pitch=PITCH)
    rgb=np.full((*domain.shape,3),[8,15,23],np.uint8);rgb[selection]=[42,94,112];rgb[domain]=[66,170,174];rgb[arch&selection]=[204,207,211];rgb[legs&selection]=[244,172,67];rgb[closure]=[175,70,164]
    Image.fromarray(rgb[::-1]).resize((domain.shape[1]*2,domain.shape[0]*2)).save(T/(q['name']+'_Domain_Review.png'))
    q['actor_audit'].sort(key=lambda r:r['actor'])
    report.append({'name':q['name'],'title':q['title'],'number':q['number'],'origin_mm':q['origin'].tolist(),'grid_shape_HW':list(domain.shape),'active_area_mm2':float(domain.sum()*PITCH**2),'native_wall_cells':int((arch&selection).sum()),'native_near_floor_furniture_cells':int((legs&selection).sum()),'native_tabletop_cells_with_water_passage_underneath':int((q['native_tabletop_projection']&domain).sum()),'artistic_selection_boundary_cells_without_native_wall':int(closure.sum()),'actors':q['actor_audit']})
manifest={'status':'Domain extraction complete; solver and physical behaviour validation pending','whole_model_scope':WHOLE,'source':'R29 read-only transformed native actor caches plus unchanged physical base footprint; restored fireplace native actors included','receiver':'P02plusP03B3 UV02 1:100 copy','grid_pitch_model_mm':PITCH,'water_obstacle_slab_model_Z_mm':[LOW,HIGH],'water_obstacle_slab_height_above_native_floor_cm':[(LOW-BASE)*10,(HIGH-BASE)*10],'floor_substrate_finish_exclusions':floor_finish_exclusions,'tabletops_do_not_block_water':True,'native_legs_do_block_water':True,'print_supported_relief_not_used_as_water_physics':True,'navigation_physics_distinct':'PacMan still avoids tabletop footprints; water travels under tabletops around near-floor legs.','boundary_authority':'GYM rectangle uses verified native wall inner bounds. Other basin grouping uses frozen A101 room reference masks clipped to actual physical footprint and native near-floor barriers. These are documented artistic selection boundaries, not a new R29 architectural room-boundary audit. Open door/reference boundaries reflect independently and do not imply a real wall.','invisible_open_door_boundaries_are_artistic':True,'rooms':report,'no_global_wave_post_clipped_to_rooms':True,'old_receiver_media_print_and_sources_changed':False}
(T/'Simulation_Domain_Manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps([{k:r[k] for k in ['name','active_area_mm2','native_wall_cells','native_near_floor_furniture_cells','native_tabletop_cells_with_water_passage_underneath','artistic_selection_boundary_cells_without_native_wall']} for r in report],indent=2),flush=True)
