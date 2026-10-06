from infinity_rooms_common import *
from production_navigation import components_by_runs

a=np.load(R/'madmapper_ripple_R03/whole_model/Whole_Native_Obstacle_And_Ownership_Grid.npz',allow_pickle=False)
origin=a['origin'];pitch=float(a['pitch']);owner=a['room_reference_owner'].copy();gh,gw=owner.shape
yy,xx=np.mgrid[:gh,:gw];wx=origin[0]+(xx+.5)*pitch;wy=origin[1]+(yy+.5)*pitch
physical=np.zeros((gh,gw),bool)
for p in sorted((R/'madmapper_ripple_R03/whole_model').glob('*_Simulation_Domain.npz')):
    b=np.load(p,allow_pickle=False);x0,y0=np.rint((b['origin']-origin)/pitch).astype(int);hh,ww=b['domain'].shape
    physical[y0:y0+hh,x0:x0+ww]|=b['domain']
assert physical.sum()==841555
nav=R/'madmapper_production_P01/navigation';nm=json.loads((nav/'Navigation_Contract.json').read_text());assert nm['source_OBJ_sha256']=='5fb3d64faebe846255f84b4e4f2be832070fec649ea99a1005d69f0c802db45f'
fine=np.load(nav/'obstacles.npy',mmap_mode='r');no=np.load(nav/'origin.npy');x0,y0=np.rint((origin-no)/.25).astype(int)
full=fine[y0:y0+gh*2,x0:x0+gw*2].reshape(gh,2,gw,2).any((1,3))
# Append the actual UV02 fireplace's complete XY footprint, which UV01 lacks.
v,uv,n,parts=parse_obj(OBJ);fire=v[parts['Opaque_Fireplace_P03_B3']['f']]
from production_navigation import square_coverage
for tri in fire:
    result=square_coverage((tri[:,:2]-origin)/pitch,[gw,gh])
    if result is not None:
        (x0,y0,x1,y1),ok=result;full[y0:y1+1,x0:x1+1]|=ok
protected=np.array(Image.fromarray(full.astype(np.uint8)*255).filter(ImageFilter.MaxFilter(5)))>0
# Use the accepted H03/H04 world polygons for the 13 named tour spaces.
wm=json.loads((R/'madmapper_highlight_H03/world_clipped/deliverables/World_Clipped_Mask_Manifest.json').read_text())
original_owner=owner.copy();special={int(x) for row in wm['masks'] for x in row['approved_room_codes'] if x.isdigit()};special.add(999)
owner[np.isin(owner,list(special))]=0
for row in reversed(wm['masks']):
    selected=np.zeros_like(physical)
    for lo,hi in row['exact_rectilinear_partition_rectangles_model_mm']:
        selected|=(wx>=lo[0])&(wx<=hi[0])&(wy>=lo[1])&(wy<=hi[1])
    codes=[int(x) if x.isdigit() else 999 for x in row['approved_room_codes']]
    if len(codes)==1:owner[selected]=codes[0]
    elif codes==[100,103]:owner[selected]=np.where(wx[selected]>635,100,103)
    else:
        prior=original_owner[selected];owner[selected]=np.where(np.isin(prior,codes),prior,codes[0])
available=physical&~protected
labels,comps=components_by_runs(available)
owner[(owner==0)&available]=1000+labels[(owner==0)&available]
# One-millimetre stationary lip at each room boundary and support island.
boundary=np.zeros_like(available)
for dy,dx in [(-1,0),(1,0),(0,-1),(0,1)]:boundary|=(owner!=np.roll(owner,(dy,dx),(0,1)))|~np.roll(available,(dy,dx),(0,1))
edge=np.array(Image.fromarray(boundary.astype(np.uint8)*255).filter(ImageFilter.MaxFilter(3)))>0
aperture=available&~edge
labels,comps=components_by_runs(aperture)
small={r['component'] for r in comps if r['safe_center_cells']*pitch*pitch<8}
aperture&=~np.isin(labels,list(small))
owner[~aperture]=0
# Manhattan distance gives a stable thin lip without optional SciPy dependencies.
boundary=np.zeros_like(aperture)
for dy,dx in [(-1,0),(1,0),(0,-1),(0,1)]:boundary|=owner!=np.roll(owner,(dy,dx),(0,1))
dist=np.where(boundary|~aperture,0,1e6).astype(np.float32);idx=np.arange(gw,dtype=np.float32)
for y in range(1,gh):
    dist[y]=np.minimum(dist[y],dist[y-1]+1)
    dist[y]=np.minimum.accumulate(dist[y]-idx)+idx
    dist[y]=np.minimum.accumulate((dist[y]+idx)[::-1])[::-1]-idx
for y in range(gh-2,-1,-1):
    dist[y]=np.minimum(dist[y],dist[y+1]+1)
    dist[y]=np.minimum.accumulate(dist[y]-idx)+idx
    dist[y]=np.minimum.accumulate((dist[y]+idx)[::-1])[::-1]-idx
dist*=pitch
# Exact cell-by-cell 2D DDA: no ray can jump across a thin real wall or island.
cy,cx=np.nonzero(aperture);rid=owner[cy,cx];qx=wx[cy,cx];qy=wy[cy,cx]
dx=(qx-EYE[0])/(EYE[2]-FLOOR_Z);dy=(qy-EYE[1])/(EYE[2]-FLOOR_Z)
sx=np.where(dx>=0,1,-1);sy=np.where(dy>=0,1,-1)
tdx=pitch/np.maximum(abs(dx),1e-12);tdy=pitch/np.maximum(abs(dy),1e-12);tx=tdx*.5;ty=tdy*.5
depth=np.zeros(len(cx),np.float32);axis=np.zeros(len(cx),np.uint8);active=np.arange(len(cx));rx=cx.copy();ry=cy.copy();steps=0
while len(active):
    xa=tx[active]<=ty[active];cross=np.where(xa,tx[active],ty[active]);rx[active]+=sx[active]*xa;ry[active]+=sy[active]*~xa
    tx[active]+=tdx[active]*xa;ty[active]+=tdy[active]*~xa
    inbounds=(rx[active]>=0)&(rx[active]<gw)&(ry[active]>=0)&(ry[active]<gh)
    remain=np.zeros(len(active),bool);ii=np.flatnonzero(inbounds);remain[ii]=owner[ry[active[ii]],rx[active[ii]]]==rid[active[ii]]
    done=~remain;depth[active[done]]=cross[done];axis[active[done]]=np.where(xa[done],1,2)
    active=active[remain];steps+=1
    assert steps<3000
    if steps%100==0:print('ROOM WALL RAYS',steps,'remaining',len(active),flush=True)
wall=np.zeros((gh,gw),np.float32);wall[cy,cx]=depth;wa=np.zeros((gh,gw),np.uint8);wa[cy,cx]=axis
rooms=json.loads((R/'print_revision02/deliverables/projection/Projection_Coordinate_Contract.json').read_text())['rooms_reference'];names={int(q['number']):q['name'] for q in rooms if q['number'].isdigit()};names[999]='GYM'
regions=[]
for i,rid in enumerate(sorted(np.unique(owner[aperture]))):
    chosen=rid==owner;limit=float(np.clip(np.percentile(wall[chosen],92),12,180));spacing=max(2.5,limit/11)
    regions.append({'region_id':int(rid),'name':names.get(int(rid),'Unlabelled physical area'),'animated_area_mm2':float(chosen.sum()*pitch*pitch),'maximum_virtual_depth_mm':limit,'layer_spacing_mm':spacing,'phase_radians':float((i*.38196601125%1)*2*np.pi),'colour_RGB':PALETTE[i%len(PALETTE)].astype(int).tolist()})
np.savez_compressed(C/'Infinity_Room_Apertures_And_Depth.npz',owner=owner,aperture=aperture,wall_depth=wall,wall_axis=wa,edge_distance=dist,protected=protected,full_obstacles=full,physical=physical,origin=origin,pitch=pitch)
q={'status':'PASS: geometry-constrained room apertures and fixed-front virtual wall rays','receiver_SHA256':sha(OBJ),'grid_pitch_mm':pitch,'physical_domain_cells':int(physical.sum()),'protected_full_projected_furniture_walls_and_fireplace_cells':int((protected&physical).sum()),'animated_aperture_cells':int(aperture.sum()),'animated_aperture_area_mm2':float(aperture.sum()*pitch*pitch),'aperture_overlap_full_obstacles':int((aperture&full).sum()),'aperture_overlap_inflated_supports':int((aperture&protected).sum()),'regions':regions,'whole_model_including_non_tour_rooms':True,'outside_named_polygons':'Residual unlabelled areas assigned to actual physical connected components, then clipped by full projected obstacles; no room labels displayed.','room_boundary_authority':'Registered A101 reference footprints, accepted H03/H04 rectilinear polygons and H02 numbered hall extensions; intersected with accepted native physical floor domains and full actual print-mesh obstacle projection. Open Cafe/Commons/Gallery divisions are virtual aperture borders, not new physical walls. No fresh R29 semantic perimeter audit claimed.','physical_furniture_method':'Complete conservative XY projection of all opaque/glazing receiver triangles above5mm, plus actual UV02 fireplace; one-millimetre inflation and stationary lip. No pit texture beneath complete tabletop/bench/cabinet overhangs. Original fixture mesh and its static atlas pixels stay fixed.','virtual_geometry_method':'For each floor point, the fixed viewer ray is extended below the floor; exact cell-by-cell DDA finds first room/support wall. Descending light planes and bottom floor are a colour illusion only.','ray_steps':steps,'eye_mm':EYE.tolist(),'target_mm':TARGET.tolist(),'horizontal_FOV_degrees':HFOV,'view_assumption':'South / negative-Y front, looking north; fixed perspective camera. Projector pose was not supplied or calibrated; one projector assumed. Real mesh occlusion remains.','frame_count':FRAMES,'fps':FPS,'duration_seconds':SECONDS,'depth_is_virtual_not_physical_geometry':True,'no_flash':'One smooth sinusoidal descend/return per24s, deterministic spatial phase offsets, no random flicker, noise, strobe or added bloom.','source_P01_is_reference_only':True,'original_geometry_UV_scale_origin_and_prior_media_changed':False}
assert q['aperture_overlap_full_obstacles']==q['aperture_overlap_inflated_supports']==0
write_json(C/'Infinity_Geometry_And_View_Contract.json',q)
out=np.zeros((gh,gw,3),np.uint8);out[physical]=[15,25,35];out[protected&physical]=[95,70,55]
for row in regions:out[owner==row['region_id']]=np.uint8(np.array(row['colour_RGB'])*.6)
Image.fromarray(out[::-1]).save(D/'Room_Apertures_And_Protected_Furniture_Plan_QA.png')
print('INFINITY GEOMETRY PREFLIGHT PASS',len(regions),'regions',q['animated_aperture_cells'],'cells',flush=True)
front_cache()
