from ripple_r02_solver import Basin,choose_source,behaviour_tests,DX,DT,C,DAMPING
from pathlib import Path
import json, math, numpy as np,collections
R=Path(__file__).parent;D=R/'madmapper_ripple_R03/whole_model';FPS=20;SECONDS=40;FRAMES=FPS*SECONDS+1
manifest=json.loads((D/'Simulation_Domain_Manifest.json').read_text());assert manifest['geometry_connected_solver_domains'] and not manifest['invisible_open_door_boundaries_are_artistic']
grid=np.load(D/'Whole_Native_Obstacle_And_Ownership_Grid.npz');owner=grid['room_reference_owner'];water=grid['footprint']&~grid['architecture']&~grid['furniture_legs'];origin=grid['origin']

class ConnectedBasin(Basin):
    def __init__(self,domain,origin,pitch=DX):
        super().__init__(domain,origin,pitch)
        self.h=np.zeros(domain.shape,np.float64);self.v=np.zeros_like(self.h)
    def impulse(self,point,width=3.,strength=8.):
        yy,xx=np.mgrid[:self.h.shape[0],:self.h.shape[1]]
        xy=self.origin+np.stack([xx+.5,yy+.5],axis=2)*self.dx;r2=np.sum((xy-point)**2,axis=2)
        gaussian=np.exp(-r2/(2*width*width));local=self.domain&(r2<=(4*width)**2)
        cell=np.floor((point-self.origin)/self.dx).astype(int);reached=np.zeros_like(self.domain);queue=collections.deque([tuple(cell)])
        while queue:
            x,y=queue.popleft()
            if x<0 or y<0 or x>=local.shape[1] or y>=local.shape[0] or reached[y,x] or not local[y,x]:continue
            reached[y,x]=True;queue.extend([(x-1,y),(x+1,y),(x,y-1),(x,y+1)])
        gaussian[~reached]=0;pulse=-self.lap(gaussian);pulse*=strength/max(float(pulse.max()),1e-20)
        # Divergence forcing has exactly zero net volume analytically. Correct
        # only its machine-rounding remainder at the source cell, retaining
        # compact support, rather than allowing an undamped constant DC mode.
        pulse[cell[1],cell[0]]-=np.sum(pulse,dtype=np.float64)
        self.v+=pulse

# Actual Commons/Cafe boundary test: remove labels from the operator entirely.
edges=(water[:,:-1]&water[:,1:])&(((owner[:,:-1]==102)&(owner[:,1:]==101))|((owner[:,:-1]==101)&(owner[:,1:]==102)))
edges_y=(water[:-1,:]&water[1:,:])&(((owner[:-1,:]==102)&(owner[1:,:]==101))|((owner[:-1,:]==101)&(owner[1:,:]==102)))
ys,xs=np.where(edges); candidates=[(int(x),int(y),'x') for x,y in zip(xs,ys)]
ys,xs=np.where(edges_y);candidates += [(int(x),int(y),'y') for x,y in zip(xs,ys)]
assert candidates,'No actual open Commons/Cafe label edge was found'
def score(q):
    x,y,axis=q;return int(water[max(y-12,0):y+13,max(x-12,0):x+13].sum())
x,y,axis=max(candidates,key=score);xa=max(x-45,0);xb=min(x+46,water.shape[1]);ya=max(y-45,0);yb=min(y+46,water.shape[0]);local=water[ya:yb,xa:xb];local_owner=owner[ya:yb,xa:xb]
test=ConnectedBasin(local,origin+np.array([xa,ya])*DX);inside=local&(local_owner==102);yy,xx=np.where(inside)
target=np.array([x-xa,y-ya])-np.array([8,0] if axis=='x' else [0,8]);pick=np.argmin(np.sum((np.column_stack([xx,yy])-target)**2,axis=1));source=test.origin+np.array([xx[pick]+.5,yy[pick]+.5])*DX
test.impulse(source,width=1.3,strength=3.);maximum=0.;series=[]
for i in range(160):
    test.step();maximum=max(maximum,float(np.max(abs(test.h[local_owner==101]))));series.append(maximum)
assert maximum>1e-4,('No wave transmission across actual open label boundary',maximum)
label_edges_x=water[:,:-1]&water[:,1:]&(owner[:,:-1]!=owner[:,1:]);label_edges_y=water[:-1,:]&water[1:,:]&(owner[:-1,:]!=owner[1:,:])
transmission={'status':'PASS: actual Commons/Cafe open boundary transmits the solved wave','actual_free_Commons_Cafe_neighbor_edges':len(candidates),'all_open_room_label_neighbor_edges_with_solver_flux_connections':int(label_edges_x.sum()+label_edges_y.sum()),'artificial_label_barrier_edges':0,'test_source_point_model_mm':source.tolist(),'test_edge_model_mm':(origin+[x+.5,y+.5]*np.array(DX)).tolist(),'Cafe_max_abs_height_from_Commons_only_impulse_mm':maximum,'test_duration_seconds':160*DT,'labels_used_in_laplacian_or_flux':False,'geometry_domain_crop_used':True}
(D/'Open_Commons_Cafe_Transmission_QA.json').write_text(json.dumps(transmission,indent=2))
print(json.dumps(transmission,indent=2),flush=True)

components=[];events=[];owner_ids=sorted(int(n) for n in np.unique(owner[water]))
for q in manifest['rooms']:
    data=np.load(D/(q['name']+'_Simulation_Domain.npz'));b=ConnectedBasin(data['domain'],data['origin']);xa,ya,xb,yb=q['global_grid_slice_xy'];local_owner=owner[ya:yb,xa:xb]
    row={'name':q['name'],'b':b,'source_events':[],'impulse_energy':0.,'peak':0.,'field_file':D/(q['name']+'_Height_Sequence.npy')}
    for number in sorted(int(n) for n in np.unique(local_owner[b.domain])):
        selection=b.domain&(local_owner==number)
        if selection.sum()<8:continue
        point=choose_source(selection,b.origin)
        # Labels locate drops only; every event changes the shared connected field.
        at=.5+2.*owner_ids.index(number)/max(len(owner_ids)-1,1)
        event={'reference_owner':number,'point':point,'time':at,'applied':False}
        row['source_events'].append(event)
    if not row['source_events']:
        row['source_events'].append({'reference_owner':None,'point':choose_source(b.domain,b.origin),'time':1.5,'applied':False})
    components.append(row)
tests=behaviour_tests();fields={q['name']:np.lib.format.open_memmap(q['field_file'],mode='w+',dtype=np.float32,shape=(FRAMES,*q['b'].domain.shape)) for q in components}
energies=[]
for frame in range(FRAMES):
    if frame:
        for sub in range(4):
            t=(frame-1)/FPS+sub*DT
            for q in components:
                b=q['b']
                for e in q['source_events']:
                    if not e['applied'] and t<=e['time']<t+DT:
                        b.impulse(e['point']);e['applied']=True;q['impulse_energy']=max(q['impulse_energy'],b.energy())
                b.step()
    summary={'time_s':frame/FPS,'max_abs_height_mm':0.,'total_energy':0.}
    for q in components:
        b=q['b'];assert np.isfinite(b.h).all() and not np.any(b.h[~b.domain]);fields[q['name']][frame]=b.h
        peak=float(np.max(abs(b.h)));q['peak']=max(q['peak'],peak);summary['max_abs_height_mm']=max(summary['max_abs_height_mm'],peak);summary['total_energy']+=b.energy()
    if frame%20==0:energies.append(summary)
    if frame%100==0:print('CONNECTED ACTUAL-GEOMETRY WAVE STATES',frame,'/',FRAMES,summary,flush=True)
for a in fields.values():a.flush()
rows=[]
for q in components:
    b=q['b'];final=float(np.max(abs(b.h)));ratio=b.energy()/max(q['impulse_energy'],1e-20)
    assert all(e['applied'] for e in q['source_events'])
    assert final<.001 and ratio<.001,(q['name'],final,ratio)
    rows.append({'name':q['name'],'source_events':[{'reference_owner':e['reference_owner'],'point_model_mm':e['point'].tolist(),'time_seconds':e['time']} for e in q['source_events']],'peak_height_mm':q['peak'],'final_max_abs_height_mm':final,'final_energy_fraction_of_impulses':ratio,'independent_only_because_actual_geometry_disconnected':True,'room_labels_do_not_partition_solver':True,'natural_damping_to_quiet_passed':True,'external_fade_applied':False})
result={'status':'PASS: full-model actual geometry-connected waves transmit across open label boundaries, reflect at real obstacles and decay naturally','fps':FPS,'duration_seconds':SECONDS,'stored_states':FRAMES,'grid_pitch_model_mm':DX,'solver_time_step_seconds':DT,'solver_substeps_per_video_frame':4,'solver_numeric_precision':'float64 conservative flux and compact zero-sum forcing; stored output height fields float32','artistic_wave_speed_model_mm_per_second':C,'damping_velocity_per_second':DAMPING,'behaviour_tests':tests,'Commons_Cafe_transmission_QA':transmission,'components':rows,'energy_timeseries':energies,'room_labels_used_for_impulses_only':True,'invisible_room_boundaries_used':False,'whole_model_solve_complete':True,'source_geometry_UV_or_prior_media_changed':False,'boundary_authority':manifest['boundary_authority'],'vertical_wall_water_or_hydraulic_filling_simulated':False,'render_transfer_pending':True}
(D/'Connected_Wave_Physics_QA.json').write_text(json.dumps(result,indent=2));print('WHOLE MODEL CONNECTED PHYSICS COMPLETE',len(rows),'components',sum(len(q['source_events']) for q in rows),'impulses',flush=True)
