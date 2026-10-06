from pathlib import Path
import json,math,time,collections
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).parent;D=R/'madmapper_ripple_R02/test01'
FPS=20;SECONDS=30;DX=.5;DT=.0125;C=25.;DAMPING=.8
assert C*DT/DX < 1/math.sqrt(2)

class Basin:
    def __init__(self,domain,origin,pitch=DX):
        self.domain=domain;self.origin=origin;self.dx=pitch
        self.h=np.zeros(domain.shape,np.float32);self.v=np.zeros_like(self.h)
        self.ex=domain[:,:-1]&domain[:,1:];self.ey=domain[:-1,:]&domain[1:,:]
    def lap(self,h):
        out=np.zeros_like(h);fx=(h[:,1:]-h[:,:-1])*self.ex;fy=(h[1:,:]-h[:-1,:])*self.ey
        out[:,:-1]+=fx;out[:,1:]-=fx;out[:-1,:]+=fy;out[1:,:]-=fy
        return out/self.dx**2
    def step(self,dt=DT,c=C,damping=DAMPING):
        self.v += c*c*dt*self.lap(self.h)
        self.v *= math.exp(-damping*dt)
        self.h += dt*self.v
        self.h[~self.domain]=0;self.v[~self.domain]=0
    def impulse(self,point,width=3.,strength=8.):
        yy,xx=np.mgrid[:self.h.shape[0],:self.h.shape[1]]
        xy=self.origin+np.stack([xx+.5,yy+.5],axis=2)*self.dx
        r2=np.sum((xy-point)**2,axis=2)
        gaussian=np.exp(-r2/(2*width*width)).astype(np.float32)
        local=self.domain&(r2<=(4*width)**2)
        cell=np.floor((point-self.origin)/self.dx).astype(int)
        reached=np.zeros_like(self.domain);queue=collections.deque([tuple(cell)])
        while queue:
            x,y=queue.popleft()
            if x<0 or y<0 or x>=local.shape[1] or y>=local.shape[0] or reached[y,x] or not local[y,x]:continue
            reached[y,x]=True
            queue.extend([(x-1,y),(x+1,y),(x,y-1),(x,y+1)])
        gaussian[~reached]=0
        pulse=-self.lap(gaussian);pulse*=strength/max(float(pulse.max()),1e-20)
        self.v+=pulse
    def energy(self,c=C):
        return float(.5*np.sum(self.v.astype(np.float64)**2)+.5*c*c/self.dx**2*(np.sum(((self.h[:,1:]-self.h[:,:-1])*self.ex).astype(np.float64)**2)+np.sum(((self.h[1:,:]-self.h[:-1,:])*self.ey).astype(np.float64)**2)))

def choose_source(domain,origin):
    # Prefer a cell with at least 5mm distance from basin barriers and furniture.
    inside=domain.copy()
    for _ in range(10):inside&=np.roll(inside,1,0)&np.roll(inside,-1,0)&np.roll(inside,1,1)&np.roll(inside,-1,1)
    yy,xx=np.where(inside if inside.any() else domain)
    xy=origin+np.column_stack([xx+.5,yy+.5])*DX
    target=origin+np.array(domain.shape[::-1])*DX*[.43,.53]
    return xy[int(np.argmin(np.sum((xy-target)**2,axis=1)))]

def behaviour_tests():
    # A wall partitions one solver field. Exciting its left basin must not cause
    # a single nonzero cell on the right; this tests solver adjacency, not colour masking.
    dom=np.ones((41,121),bool);dom[:,60]=False;b=Basin(dom,np.zeros(2));b.impulse(np.array([18.,10.]),1.,2.)
    max_other=0.;ener=[]
    for i in range(400):b.step(c=20.,damping=.1);max_other=max(max_other,float(np.max(abs(b.h[:,61:]))));ener.append(b.energy(20.))
    assert max_other==0 and not np.any(b.h[~dom])
    # Pulse travels into a closed end; the returning pulse reaches the source-side
    # probe only after round-trip travel. Compare before/after energy at that probe.
    dom=np.ones((9,101),bool);r=Basin(dom,np.zeros(2));x=(np.arange(101)+.5)*DX;g=np.exp(-((x-15.)/1.5)**2).astype(np.float32)
    r.h[:]=g;derivative=np.gradient(g,DX);r.v[:]=-20.*derivative
    series=[]
    for i in range(440):
        r.step(c=20.,damping=.03);series.append(float(r.h[4,30]))
    times=np.arange(440)*DT
    outgoing=float(np.max(np.abs(np.array(series)[(times>.4)&(times<2.)])))
    reflected=float(np.max(np.abs(np.array(series)[(times>3.)&(times<4.2)])))
    assert reflected>.25,(outgoing,reflected)
    return {'inter_basin_transfer_max_abs_height_mm':max_other,'barrier_cells_height_and_velocity_exact_zero':True,'edge_flux_at_walls_exact_zero_by_no_connection':True,'returning_closed_wall_probe_amplitude_mm':reflected,'reflection_probe_passed':True,'CFL_number':C*DT/DX,'2D_stability_limit':1/math.sqrt(2),'solver_method':'Symplectic damped height-field wave equation; symmetric finite-volume neighbour flux. Removed domain neighbour means no flow / reflecting Neumann wall, not a post-render mask.','full_liquid_flow_splashes_or_overtopping_simulated':False}

if __name__=='__main__':
    manifest=json.loads((D/'Simulation_Domain_Manifest.json').read_text());rooms=[]
    for q in manifest['rooms']:
        a=np.load(D/(q['name']+'_Simulation_Domain.npz'));b=Basin(a['domain'],a['origin']);point=choose_source(b.domain,b.origin)
        rooms.append({'name':q['name'],'b':b,'source':point,'source_time':.5+len(rooms)*.8,'initial_energy':0.,'maxheight':0.,'field_file':D/(q['name']+'_Height_Sequence.npy')})
    tests=behaviour_tests();frames=FPS*SECONDS+1
    fields={q['name']:np.lib.format.open_memmap(q['field_file'],mode='w+',dtype=np.float32,shape=(frames,*q['b'].h.shape)) for q in rooms}
    energy=[]
    for frame in range(frames):
        t=frame/FPS
        if frame:
            for sub in range(4):
                st=(frame-1)/FPS+sub*DT
                for q in rooms:
                    if st<=q['source_time']<st+DT:
                        q['b'].impulse(q['source']);q['initial_energy']=q['b'].energy()
                    q['b'].step()
        sample={'time_s':t}
        for q in rooms:
            b=q['b'];assert np.isfinite(b.h).all() and not np.any(b.h[~b.domain]);fields[q['name']][frame]=b.h
            q['maxheight']=max(q['maxheight'],float(np.max(abs(b.h))));sample[q['name']]=b.energy()
        energy.append(sample)
        if frame%100==0:print('ROOM-LOCAL WAVE STATES',frame,'/',frames,[(q['name'],round(float(np.max(abs(q['b'].h))),7)) for q in rooms],flush=True)
    for arr in fields.values():arr.flush()
    roomqa=[]
    for q in rooms:
        b=q['b'];final=float(np.max(abs(b.h)));ratio=b.energy()/max(q['initial_energy'],1e-20)
        assert final<.001 and ratio<.001,(q['name'],final,ratio)
        roomqa.append({'name':q['name'],'source_point_mm':q['source'].tolist(),'source_time_seconds':q['source_time'],'peak_height_mm':q['maxheight'],'final_max_abs_height_mm':final,'final_energy_fraction_of_impulse':ratio,'natural_damping_quiet_threshold_height_mm':.001,'natural_decay_to_quiet_passed':True,'external_fade_applied':False,'separate_independent_basin_state':True})
    result={'status':'PASS: independent room wave solver reflects at barriers and decays naturally to quiet','fps':FPS,'duration_seconds':SECONDS,'stored_states':frames,'grid_pitch_model_mm':DX,'solver_substeps_per_video_frame':4,'solver_time_step_seconds':DT,'artistic_wave_speed_model_mm_per_second':C,'damping_velocity_per_second':DAMPING,'behaviour_tests':tests,'rooms':roomqa,'energy_timeseries':energy,'geometry_and_UV_modified':False,'whole_building_expansion_complete':False,'important_boundary_limit':manifest['boundary_authority'],'next_stage':'UV02 field transfer and fresh native mapped preview; extend room grouping only after basin boundary review.'}
    (D/'Room_Local_Wave_Physics_QA.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:result[k] for k in ['status','behaviour_tests','rooms']},indent=2),flush=True)
