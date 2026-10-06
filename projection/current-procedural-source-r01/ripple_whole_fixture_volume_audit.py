from geometry_utils import *
from PIL import Image, ImageDraw
from production_navigation import components_by_runs, square_coverage
import time

CONNECTED = '--connected' in sys.argv
ROOT = R / ('madmapper_ripple_R03' if CONNECTED else 'madmapper_ripple_R02')
CANDIDATE = R / 'madmapper_ripple_R02/whole_model'
OUT = ROOT / ('whole_model' if CONNECTED else 'whole_model_v02')
OUT.mkdir(parents=True,exist_ok=True)
assert not (OUT / 'Solid_Fixture_Volume_QA.json').exists(), 'Preserve completed audit'
data = np.load(CANDIDATE / 'Whole_Native_Obstacle_And_Ownership_Grid.npz')
grid = {k: np.array(data[k]) for k in data.files}
if CONNECTED: grid['furniture_legs'][:]=False
origin = grid['origin']; pitch = float(grid['pitch']); shape = grid['footprint'].shape
LOW, HIGH, BASE = 4.25, 5.2, 4.2
arch_extra = np.zeros(shape, bool); fixture_extra = np.zeros(shape, bool)
actors = json.loads((R / 'print_revision02/native_selected_actors.json').read_text())
cache = json.loads((R / 'print_revision02/actor_mesh_manifest.json').read_text())
audit = []; warnings = []; floor_exclusions = []; shell_checks = 0

def clip(poly,z,greater):
    out=[]
    for a,b in zip(poly,np.roll(poly,-1,axis=0)):
        aa=a[2]>=z if greater else a[2]<=z;bb=b[2]>=z if greater else b[2]<=z
        if aa:out.append(a)
        if aa!=bb:out.append(a+(z-a[2])/(b[2]-a[2])*(b-a))
    return np.array(out)

def raster_slab(triangles,dest):
    h,w=dest.shape
    for t in triangles:
        p=clip(t,LOW,True)
        if len(p)<3:continue
        p=clip(p,HIGH,False)
        if len(p)<3:continue
        for j in range(1,len(p)-1):
            result=square_coverage((p[[0,j,j+1],:2]-origin)/pitch,[w,h])
            if result is not None:
                (x0,y0,x1,y1),ok=result;dest[y0:y1+1,x0:x1+1]|=ok

def source_cut_contours(v,faces,z):
    """Use only closed, directed loops of actual plane/triangle intersections."""
    tri=v[faces];use=(tri[:,:,2].min(1)<z)&(tri[:,:,2].max(1)>z)
    tris=tri[use];segments={};points={}
    for t in tris:
        found=[]
        for a,b in zip(t,np.roll(t,-1,axis=0)):
            if (a[2]<z)<=(b[2]<z) and (a[2]<z)==(b[2]<z):continue
            if (a[2]<z)!=(b[2]<z):found.append((a+(z-a[2])/(b[2]-a[2])*(b-a))[:2])
        if len(found)!=2:continue
        a,b=found
        normal=np.cross(t[1]-t[0],t[2]-t[0]);tangent=np.array([-normal[1],normal[0]])
        if (b-a)@tangent<0:a,b=b,a
        ka=tuple(np.rint(a/1e-5).astype(np.int64));kb=tuple(np.rint(b/1e-5).astype(np.int64))
        if ka==kb:continue
        points[ka]=a;points[kb]=b;segments[(ka,kb)]=True
    outgoing=collections.defaultdict(list);incoming=collections.defaultdict(list)
    for a,b in segments:outgoing[a].append(b);incoming[b].append(a)
    available=set(segments);loops=[];unclosed=0
    while available:
        start,nextp=next(iter(available));path=[start];used=[];current=start;closed=False
        while len(outgoing[current])==1 and len(incoming[current])==1:
            following=outgoing[current][0];edge=(current,following)
            if edge not in available:break
            available.remove(edge);used.append(edge);current=following
            if current==start:closed=True;break
            path.append(current)
        if closed and len(path)>=3:loops.append(np.array([points[k] for k in path]))
        else:
            unclosed+=len(used)
            if not used:available.remove((start,nextp));unclosed+=1
    section=mf.CrossSection(loops,mf.FillRule.Positive) if loops else mf.CrossSection()
    return section.to_polygons(),{'actual_intersection_segments':len(segments),'closed_directed_source_loops':len(loops),'unclosed_or_branch_intersection_segments':unclosed}

def fill_slice(polygons):
    # Fill each actor independently, retaining its holes before union with other actors.
    if not len(polygons): return np.zeros(shape, bool)
    polys = [np.asarray(p) for p in polygons if len(p) >= 3]
    im = Image.new('L', shape[::-1]); draw = ImageDraw.Draw(im)
    def area(p): return np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1))/2
    for p in sorted(polys, key=lambda p: -abs(area(p))):
        draw.polygon([tuple(q) for q in (p-origin)/pitch-.5], fill=255 if area(p)>0 else 0)
    return np.asarray(im)>0

def manifolds_for(v, faces):
    global shell_checks
    result = mf.Manifold(mf.Mesh64(np.asarray(v,np.float64), np.asarray(faces,np.uint64)))
    if result.status() == mf.Error.NoError and result.volume()>1e-12:
        return [result], 0, 'whole actor closed mesh'
    m = trimesh.Trimesh(v, faces, process=False)
    solids = []; opened = 0
    for indices in shells(m):
        shell_checks += 1
        p = m.submesh([indices], append=True, repair=False)
        s = mf.Manifold(mf.Mesh64(np.asarray(p.vertices,np.float64),np.asarray(p.faces,np.uint64)))
        if s.status()==mf.Error.NoError and s.volume()>1e-12:
            solids.append(s)
        else:
            opened += len(p.faces)
    return solids, opened, 'closed source shells; unclosed surfaces retain original surface-only barriers'

# Analytic regression: a closed box spanning both cut planes must block its interior,
# and a hollow closed tube must preserve its central opening.
box_test = mf.Manifold.cube((8,8,3)).translate(tuple([*origin,3.8]))
test_mask = fill_slice(box_test.slice(LOW+1e-5).to_polygons())
test_xy = np.floor((origin+[4,4]-origin)/pitch).astype(int)
assert test_mask[test_xy[1],test_xy[0]], 'Closed fixture interior is incorrectly water'
tube = box_test - mf.Manifold.cube((4,4,5)).translate(tuple([*(origin+[2,2]),3.]))
tube_mask = fill_slice(tube.slice(LOW+1e-5).to_polygons())
assert not tube_mask[test_xy[1],test_xy[0]], 'Real hollow opening incorrectly filled'

for i,(a,c) in enumerate(zip(actors,cache)):
    label=a['label']; text=(label+' '+a['mesh']+' '+a.get('folder','')).lower()
    architecture=any(s in (label+' '+str(a.get('tags',[]))) for s in ['Architecture','Doors','Stair','commons_architecture','architectural_glazing'])
    if label=='Architect_Finishes_v02': continue
    if not architecture and any(s in text for s in ('bleacher','grass','shrub','tree','foliage','schoolapron','schoolfoundation','earth','exteriorsidewalk','site_','roller','diffuser','housing','led','ceiling','floorfinish','trophy_illumination','sky','balloon','water','ember')): continue
    ub=np.array(c['triangle_bounds_cm'])
    bounds=np.array([[ub[0,0],-ub[1,1],ub[0,2]],[ub[1,0],-ub[0,1],ub[1,2]]])
    bounds=(bounds+[4700,230,0])*.1; bounds[:,2]+=BASE
    if bounds[0,2]>HIGH or bounds[1,2]<LOW: continue
    if np.any(bounds[1,:2]<origin) or np.any(bounds[0,:2]>origin+np.array(shape[::-1])*pitch): continue
    if CONNECTED and bounds[1,2]<=BASE+.3 and any(token in str(a.get('materials',[])) for token in ('M_ContinuousCorridorOak','M_FloorTransitionBronze','M_CRI_PerimeterTile')):
        floor_exclusions.append({'actor':a['actor'],'label':label,'actual_override_materials':a.get('materials',[]),'native_height_above_ground_cm':[float((bounds[0,2]-BASE)*10),float((bounds[1,2]-BASE)*10)],'classification':'Confirmed thin floor finish or floor transition; basin substrate, not reflecting obstacle','source_sha256':hashlib.sha256(Path(c['file']).read_bytes()).hexdigest()})
        continue
    raw=np.load(c['file']); v=(raw['vertices']+[4700,230,0])*.1; v[:,2]+=BASE
    faces=raw['faces']; slots=a.get('slots',[])
    finish_ids=[k for k,q in enumerate(slots) if 'floor' in q.get('name','').lower()]
    if finish_ids:
        keep=~np.isin(raw['materials'],finish_ids)
        if (~keep).any():
            floor_exclusions.append({'actor':a['actor'],'label':label,'excluded_floor_finish_triangles':int((~keep).sum()),'material_names':[slots[k]['name'] for k in finish_ids]})
        faces=faces[keep]
    if not len(faces): continue
    tri=v[faces];slab_faces=(tri[:,:,2].max(1)>=LOW)&(tri[:,:,2].min(1)<=HIGH)
    if CONNECTED and not architecture:raster_slab(tri[slab_faces],grid['furniture_legs'])
    solids, opened, method = manifolds_for(v,faces)
    cap=np.zeros(shape,bool); used_solids=0
    for s in solids:
        b=np.asarray(s.bounding_box()).reshape(2,3)
        if b[0,2]>HIGH or b[1,2]<LOW: continue
        used_solids+=1
        for z in (LOW+1e-5,HIGH-1e-5):
            cap |= fill_slice(s.slice(z).to_polygons())
    contour_records=[]
    if CONNECTED and opened:
        for z in (LOW+1e-5,HIGH-1e-5):
            contours,cr=source_cut_contours(v,faces,z);cap|=fill_slice(contours);contour_records.append({'cut_Z_model_mm':z,**cr})
    dest = arch_extra if architecture else fixture_extra
    new_before = int((cap & grid['footprint'] & ~grid['architecture'] & ~grid['furniture_legs'] & ~arch_extra & ~fixture_extra).sum())
    dest |= cap
    record={'actor':a['actor'],'label':label,'category':'native wall/glazing/door' if architecture else 'native near-floor furniture/fixture','source_file':c['file'],'source_sha256':hashlib.sha256(Path(c['file']).read_bytes()).hexdigest(),'closed_solids_at_water_slab':used_solids,'unclosed_source_triangles_after_floor_exclusions':opened,'cap_cells':int(cap.sum()),'previously_false_water_cells_blocked':new_before,'method':method,'actual_source_plane_contour_audit':contour_records}
    audit.append(record)
    if opened and (not CONNECTED or any(q['unclosed_or_branch_intersection_segments'] for q in contour_records)): warnings.append(record)
    if len(audit)%30==0: print('CLOSED FIXTURE CAP AUDIT',len(audit),'source index',i,'new interior cells',int(((arch_extra|fixture_extra)&grid['footprint']&~grid['architecture']&~grid['furniture_legs']).sum()),flush=True)

old_water=grid['footprint']&~grid['architecture']&~grid['furniture_legs']
grid['architecture'] |= arch_extra; grid['furniture_legs'] |= fixture_extra
water=grid['footprint']&~grid['architecture']&~grid['furniture_legs']
np.savez_compressed(OUT/'Whole_Native_Obstacle_And_Ownership_Grid.npz',**grid)
owner=grid['room_reference_owner']; coverage=np.zeros(shape,bool); rows=[]; labels_manifest=[]
boundary=((np.roll(owner,1,0)!=owner)|(np.roll(owner,-1,0)!=owner)|(np.roll(owner,1,1)!=owner)|(np.roll(owner,-1,1)!=owner))
for number in ([-1] if CONNECTED else sorted(np.unique(owner[water]))):
    labels,components=components_by_runs(water if CONNECTED else water&(owner==number))
    for comp in components:
        domain=labels==comp['component']
        if domain.sum()<8: continue
        ys,xs=np.where(domain); xa=max(int(xs.min())-1,0); xb=min(int(xs.max())+2,shape[1]); ya=max(int(ys.min())-1,0); yb=min(int(ys.max())+2,shape[0]); sl=np.s_[ya:yb,xa:xb]
        name=('Connected' if CONNECTED else 'GYM' if number==999 else 'Neutral' if number==0 else 'R'+str(number))+f"_B{comp['component']:03d}"
        selection=grid['footprint'][sl] if CONNECTED else grid['footprint'][sl]&(owner[sl]==number); dom=domain[sl]
        arch=grid['architecture'][sl]; fixtures=grid['furniture_legs'][sl]; tops=grid['tabletop_projection'][sl]
        closure=np.zeros_like(dom) if CONNECTED else boundary[sl]&selection&~arch
        local_origin=origin+np.array([xa,ya])*pitch
        np.savez_compressed(OUT/(name+'_Simulation_Domain.npz'),domain=dom,selection=selection,architecture=arch,furniture_legs=fixtures,tabletop_projection=tops,artistic_reference_boundary=closure,origin=local_origin,pitch=pitch,global_grid_slice_xy=[xa,ya,xb,yb])
        coverage|=domain
        rows.append({'name':name,'number':int(number),'title':'Geometry-connected water component '+name if CONNECTED else 'Independent basin '+name,'origin_mm':local_origin.tolist(),'grid_shape_HW':list(dom.shape),'global_grid_slice_xy':[xa,ya,xb,yb],'active_area_mm2':float(dom.sum()*pitch**2),'native_wall_cells':int((arch&selection).sum()),'native_near_floor_furniture_cells':int((fixtures&selection).sum()),'native_tabletop_cells_with_water_passage_underneath':int((tops&dom).sum()),'artistic_selection_boundary_cells_without_native_wall':int(closure.sum()),'room_reference_owners_present':sorted(int(x) for x in np.unique(owner[sl][dom]))})
        labels_manifest.append({'name':name,'reference_owner':int(number),'active_cells':int(dom.sum())})
np.save(OUT/'Animated_Meaningful_Basin_Coverage.npy',coverage)
rgb=np.full((*shape,3),[8,15,23],np.uint8);rgb[grid['footprint']]=[42,94,112];rgb[water]=[66,170,174];rgb[grid['architecture']&grid['footprint']]=[204,207,211];rgb[grid['furniture_legs']&grid['footprint']]=[244,172,67];rgb[old_water&~water]=[255,75,75]
if not CONNECTED:rgb[boundary&water]=[175,70,164]
Image.fromarray(rgb[::-1]).save(OUT/'Whole_Model_Fixture_Volume_And_Domain_Review.png')
scope=('Only actual native near-floor walls, glazing, doors and fixtures plus the physical floor edge define reflecting boundaries. Geometry-connected open areas share the same solver state, including unobstructed doors and Commons/Cafe label boundaries. Frozen coarse room-reference masks identify impulse locations only; they never remove neighbour flux. No invisible room boundary walls.' if CONNECTED else 'Grouping remains frozen coarse A101 reference masks, with verified native gym inner bounds. Masks crossing open doors/floor are explicit artistic invisible closures. Neutral/unassigned physical floor is included. This is not a new R29 semantic room-boundary audit.')
preflight={'status':'PASS: closed native solid cut-plane interiors added before whole-model basin partition; solver/render still pending','physical_floor_cells':int(grid['footprint'].sum()),'previous_candidate_water_free_cells':int(old_water.sum()),'native_water_free_cells':int(water.sum()),'false_closed_solid_interior_water_cells_removed':int((old_water&~water).sum()),'meaningful_basin_cells':int(coverage.sum()),'unexcited_smaller_than_2mm2_cells':int((water&~coverage).sum()),'meaningful_basins':len(rows),'reference_selections_with_meaningful_basins':sorted(int(x) for x in np.unique(owner[coverage])),'basins':labels_manifest,'scope_limit':scope,'prior_files_changed':False,'artificial_room_boundary_cells':0 if CONNECTED else None,'all_open_room_label_edges_have_solver_flux_connections':CONNECTED}
(OUT/'Whole_Model_Coverage_Preflight.json').write_text(json.dumps(preflight,indent=2))
manifest={'status':'Fixture occupancy audit complete; solver and rendered behaviour validation pending','whole_model_scope':True,'source':'Read-only R29 native actor caches with unchanged physical footprint and restored fireplace','grid_pitch_model_mm':pitch,'water_obstacle_slab_model_Z_mm':[LOW,HIGH],'closed_solid_interior_cap_fill':True,'fixture_volume_QA':str(OUT/'Solid_Fixture_Volume_QA.json'),'floor_substrate_finish_exclusions':floor_exclusions,'tabletops_do_not_block_water':True,'native_legs_do_block_water':True,'print_supported_relief_not_used_as_water_physics':True,'boundary_authority':scope,'invisible_open_door_boundaries_are_artistic':not CONNECTED,'rooms':rows,'actor_sources_recorded_once_in_fixture_QA':True,'no_global_wave_post_clipped_to_rooms':True,'old_receiver_media_print_and_sources_changed':False,'geometry_connected_solver_domains':CONNECTED,'room_labels_are_source_locations_only':CONNECTED}
(OUT/'Simulation_Domain_Manifest.json').write_text(json.dumps(manifest,indent=2))
qa={'status':'PASS: closed fixture interiors block water, hollow openings preserved; exact source surfaces retained for unclosed native meshes','analytic_closed_spanning_box_interior_blocked':True,'analytic_hollow_tube_opening_preserved':True,'native_actors_audited':len(audit),'closed_solids_at_water_slab':sum(q['closed_solids_at_water_slab'] for q in audit),'source_shells_checked':shell_checks,'false_interior_water_cells_removed':int((old_water&~water).sum()),'unclosed_native_actor_surface_only_barrier_warnings':warnings,'warnings_count':len(warnings),'all_native_solid_fixtures_watertight_claimed':False,'cut_planes_model_Z_mm':[LOW+1e-5,HIGH-1e-5],'method':'Union original water-slab source triangle footprints with filled cut-plane contours of actual closed native actors/source shells, before domain partition and solving. Per-solid hole winding is preserved. No proxy fixture boxes or invented caps are used on unclosed native geometry.','floor_finish_substrates_excluded':floor_exclusions,'actor_audit':audit,'coverage':preflight,'physical_print_or_projection_receiver_or_prior_test_media_changed':False}
(OUT/'Solid_Fixture_Volume_QA.json').write_text(json.dumps(qa,indent=2))
print(json.dumps({k:v for k,v in qa.items() if k not in ['actor_audit','unclosed_native_actor_surface_only_barrier_warnings','floor_finish_substrates_excluded','coverage']},indent=2),flush=True)
print(json.dumps({k:v for k,v in preflight.items() if k!='basins'},indent=2),flush=True)
