from ripple_r02_solver import Basin,choose_source,behaviour_tests,DX,DT,C,DAMPING
from pathlib import Path
import json,numpy as np,collections,hashlib
R=Path(__file__).parent;SRC=R/'madmapper_ripple_R03/whole_model';D=R/'madmapper_ripple_R04/whole_model';D.mkdir(parents=True,exist_ok=True)
FPS=20;SECONDS=64;FRAMES=FPS*SECONDS+1
manifest=json.loads((SRC/'Simulation_Domain_Manifest.json').read_text());assert manifest['geometry_connected_solver_domains'] and not manifest['invisible_open_door_boundaries_are_artistic']
old=json.loads((SRC/'Connected_Wave_Physics_QA.json').read_text());assert old['status'].startswith('PASS')
transmission=old['Commons_Cafe_transmission_QA'];assert transmission['actual_free_Commons_Cafe_neighbor_edges']==137 and not transmission['labels_used_in_laplacian_or_flux']

class ConnectedBasin(Basin):
    def __init__(self,domain,origin,pitch=DX):
        super().__init__(domain,origin,pitch);self.h=np.zeros(domain.shape,np.float64);self.v=np.zeros_like(self.h)
    def impulse(self,point,width=3.,strength=8.):
        yy,xx=np.mgrid[:self.h.shape[0],:self.h.shape[1]];xy=self.origin+np.stack([xx+.5,yy+.5],axis=2)*self.dx;r2=np.sum((xy-point)**2,axis=2)
        gaussian=np.exp(-r2/(2*width*width));local=self.domain&(r2<=(4*width)**2);cell=np.floor((point-self.origin)/self.dx).astype(int);reached=np.zeros_like(self.domain);queue=collections.deque([tuple(cell)])
        while queue:
            x,y=queue.popleft()
            if x<0 or y<0 or x>=local.shape[1] or y>=local.shape[0] or reached[y,x] or not local[y,x]:continue
            reached[y,x]=True;queue.extend([(x-1,y),(x+1,y),(x,y-1),(x,y+1)])
        gaussian[~reached]=0;pulse=-self.lap(gaussian);pulse*=strength/max(float(pulse.max()),1e-20);pulse[cell[1],cell[0]]-=np.sum(pulse,dtype=np.float64);self.v+=pulse

representatives={}
for row in old['components']:
    for e in row['source_events']:
        code=e['reference_owner']
        if code is not None and code not in representatives:representatives[code]=np.array(e['point_model_mm'])
remaining=set(representatives);order=[999] if 999 in remaining else [min(remaining)];remaining.remove(order[0])
while remaining:
    last=representatives[order[-1]];n=max(remaining,key=lambda x:(float(np.sum((representatives[x]-last)**2)),-x));order.append(n);remaining.remove(n)
owner_time={n:.75+.60*i for i,n in enumerate(order)};seen=collections.Counter();components=[];source_hashes=[]
for row in old['components']:
    path=SRC/(row['name']+'_Simulation_Domain.npz');data=np.load(path);b=ConnectedBasin(data['domain'],data['origin']);events=[]
    source_hashes.append({'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    for e in row['source_events']:
        code=e['reference_owner'];index=seen[code];seen[code]+=1
        at=(owner_time[code] if code is not None else .75+.60*(len(components)%len(order)))+.0375*(index%7)
        at=round(at/DT)*DT;events.append({'reference_owner':code,'point':np.array(e['point_model_mm']),'time':at,'applied':False})
    field=D/(row['name']+'_Height_Sequence.npy');assert not field.exists();components.append({'name':row['name'],'b':b,'source_events':events,'impulse_energy':0.,'peak':0.,'field_file':field})
fields={q['name']:np.lib.format.open_memmap(q['field_file'],mode='w+',dtype=np.float32,shape=(FRAMES,*q['b'].domain.shape)) for q in components};series=[]
for frame in range(FRAMES):
    if frame:
        for sub in range(4):
            t=(frame-1)/FPS+sub*DT
            for q in components:
                b=q['b']
                for e in q['source_events']:
                    if not e['applied'] and t<=e['time']<t+DT:b.impulse(e['point']);e['applied']=True;q['impulse_energy']=max(q['impulse_energy'],b.energy())
                b.step()
    summary={'time_seconds':frame/FPS,'max_abs_height_mm':0.,'total_energy':0.}
    for q in components:
        b=q['b'];assert np.isfinite(b.h).all() and not np.any(b.h[~b.domain]);fields[q['name']][frame]=b.h;peak=float(np.max(abs(b.h)));q['peak']=max(q['peak'],peak);summary['max_abs_height_mm']=max(summary['max_abs_height_mm'],peak);summary['total_energy']+=b.energy()
    if frame%20==0:series.append(summary)
    if frame%100==0:print('R04 STAGGERED GEOMETRY-CONNECTED SOLVE',frame,'/',FRAMES,summary,flush=True)
for f in fields.values():f.flush()
rows=[]
for q in components:
    b=q['b'];final=float(np.max(abs(b.h)));ratio=b.energy()/max(q['impulse_energy'],1e-20);assert all(e['applied'] for e in q['source_events']) and final<.00007 and ratio<.001,(q['name'],final,ratio)
    rows.append({'name':q['name'],'source_events':[{'reference_owner':e['reference_owner'],'point_model_mm':e['point'].tolist(),'time_seconds':e['time']} for e in q['source_events']],'peak_height_mm':q['peak'],'final_max_abs_height_mm':final,'final_energy_fraction':ratio,'room_labels_do_not_partition_solver':True,'natural_decay_to_quiet_passed':True})
events=[e for q in rows for e in q['source_events']];assert max(e['time_seconds'] for e in events)-min(e['time_seconds'] for e in events)>18
qa={'status':'PASS: deterministic spatially staggered sources, unchanged physical connectivity, natural quiet repeat boundary','revision':'R04; R03 unchanged','fps':FPS,'duration_seconds':SECONDS,'stored_states':FRAMES,'grid_pitch_model_mm':DX,'solver_DT_seconds':DT,'substeps_per_frame':4,'wave_speed_model_mm_per_second':C,'damping_per_second':DAMPING,'numeric_precision':'float64 flux/forcing, float32 stored states','source_events':len(events),'source_timing_first_seconds':min(e['time_seconds'] for e in events),'source_timing_last_seconds':max(e['time_seconds'] for e in events),'spatial_order_reference_codes_metadata_only':order,'timing_rule':'Gym first, then deterministically choose the farthest remaining reference location from the previous one;0.60s between reference zones,0.0375s offset for additional disconnected pockets. Labels locate sources only; no label flux barriers.','connected_components':len(rows),'components':rows,'energy_timeseries':series,'accepted_R03_transmission_evidence':transmission,'synthetic_reflection_and_isolation_tests':behaviour_tests(),'domain_source_hashes':source_hashes,'accepted_actual_geometry_domains_reused_unchanged':True,'source_geometry_UVs_registration_or_R03_media_changed':False,'no_fade':True,'render_transfer_pending':True,'full_hydraulic_liquid_simulation':False,'physical_projection_or_MadMapper_playback_verified':False}
(D/'Staggered_Connected_Wave_Physics_QA.json').write_text(json.dumps(qa,indent=2));print('R04 STAGGERED PHYSICS COMPLETE',len(rows),len(events),flush=True)
