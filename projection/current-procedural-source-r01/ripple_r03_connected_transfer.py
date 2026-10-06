import os,shutil
from production_common import cache_arrays,sha
from pathlib import Path
import numpy as np,json,subprocess
from PIL import Image
R=Path(__file__).parent;T=R/'madmapper_ripple_R03/whole_model';D=T/'deliverables';D.mkdir(exist_ok=True)
RES=4096;FPS=20;FRAMES=800
qa=json.loads((T/'Connected_Wave_Physics_QA.json').read_text());assert qa['status'].startswith('PASS')
arr=cache_arrays(100,RES);valid=arr['valid']>0;floor=valid&(arr['up']>0)&(arr['z']<=5.4*64)
flat=np.flatnonzero(floor);wx=np.asarray(arr['x'][floor],np.float32)/64;wy=np.asarray(arr['y'][floor],np.float32)/64
base=np.zeros((RES,RES,3),np.uint8);base[floor]=[5,12,22];raised=valid&~floor
base[raised]=np.uint8(np.array([73,100,116])*np.asarray(arr['light'][raised],np.float32)[:,None]/255)
hybrid=R/'madmapper_hybrid_UV02/deliverables';patch=np.asarray(Image.open(hybrid/'Fireplace_Only_Patch_8192.png').resize((RES,RES),Image.Resampling.NEAREST));pmask=np.asarray(Image.open(hybrid/'Fireplace_New_Chart_Mask_8192.png').resize((RES,RES),Image.Resampling.NEAREST))>0;base[pmask]=patch[pmask]
manifest=json.loads((T/'Simulation_Domain_Manifest.json').read_text());components=[];coverage=np.zeros(len(flat),bool)
for q in manifest['rooms']:
    data=np.load(T/(q['name']+'_Simulation_Domain.npz'));dom=data['domain'];origin=data['origin'];pitch=float(data['pitch']);hh,ww=dom.shape
    gx=(wx-origin[0])/pitch-.5;gy=(wy-origin[1])/pitch-.5;cx=np.floor((wx-origin[0])/pitch).astype(int);cy=np.floor((wy-origin[1])/pitch).astype(int)
    ix=np.flatnonzero((cx>=0)&(cy>=0)&(cx<ww)&(cy<hh));ix=ix[dom[cy[ix],cx[ix]]];assert not coverage[ix].any();coverage[ix]=True
    x0=np.clip(np.floor(gx[ix]).astype(int),0,ww-1);y0=np.clip(np.floor(gy[ix]).astype(int),0,hh-1);x1=np.minimum(x0+1,ww-1);y1=np.minimum(y0+1,hh-1);tx=np.clip(gx[ix]-x0,0,1);ty=np.clip(gy[ix]-y0,0,1)
    components.append({'name':q['name'],'indices':flat[ix],'x0':x0,'y0':y0,'x1':x1,'y1':y1,'tx':tx,'ty':ty,'fields':np.load(T/(q['name']+'_Height_Sequence.npy'),mmap_mode='r')})
    base.reshape(-1,3)[flat[ix]]=[12,72,100]
    print('CONNECTED WAVE UV SAMPLER',q['name'],len(ix),'floor texels',flush=True)

def render(frame):
    atlas=base.copy();rgb=atlas.reshape(-1,3);peak_channel=0
    for q in components:
        if not len(q['indices']):continue
        h=q['fields'][frame];x0,y0,x1,y1,tx,ty=[q[k] for k in ['x0','y0','x1','y1','tx','ty']]
        value=(1-ty)*((1-tx)*h[y0,x0]+tx*h[y0,x1])+ty*((1-tx)*h[y1,x0]+tx*h[y1,x1])
        dx=(h[y0,x1]-h[y0,x0])/.5;dy=(h[y1,x0]-h[y0,x0])/.5
        # Bounded exposure: brighter teal calm water and cyan crests, with a
        # smooth quadratic response that preserves small rings and quantises
        # naturally quiet residuals to the same still-water display.
        crest=-np.expm1(-(np.maximum(value,0)*1200.)**2)
        trough=-np.expm1(-(np.maximum(-value,0)*1000.)**2)
        slope=(dx-dy)*400.;normal=np.sign(slope)*np.tanh(abs(slope)**1.5)
        color=np.array([12,72,100])+crest[:,None]*[42,155,138]+trough[:,None]*[16,-23,-10]+normal[:,None]*[12,16,10]
        assert np.isfinite(color).all() and np.min(color)>=0 and np.max(color)<255
        rgb[q['indices']]=np.uint8(np.rint(color));peak_channel=max(peak_channel,int(np.max(color)) if len(color) else 0)
    return atlas,peak_channel
quiet0,_=render(0);quietlast,_=render(FRAMES-1);quietend,_=render(FRAMES)
assert np.array_equal(quiet0,quietlast) and np.array_equal(quiet0,quietend),'Extend physical simulation or adjust documented transfer until actual display is quiet'
ffmpeg=Path(os.environ.get('FFMPEG',shutil.which('ffmpeg') or 'ffmpeg'));primary=D/'Ripple_R03_WholeModel_Connected_UV02_1_100_4096_HAP.mov';assert not primary.exists()
cmd=[str(ffmpeg),'-hide_banner','-loglevel','error','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{RES}x{RES}','-framerate',str(FPS),'-i','pipe:0','-an','-c:v','hap','-format','hap','-compressor','snappy','-chunks','8','-pix_fmt','rgba',str(primary)]
peaks=[]
with (T/'Encoding_Log.txt').open('wb') as err:
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=err)
    for frame in range(FRAMES):
        atlas,peak=render(frame);peaks.append(peak)
        if frame in [0,60,120,200,400,799]:Image.fromarray(atlas).save(D/f'Ripple_R03_Frame_{frame:04d}_Source_Atlas_4096.png')
        proc.stdin.write(atlas.tobytes())
        if frame%80==0:print('CONNECTED BRIGHT WHOLE-MODEL ATLAS VIDEO',frame,'/',FRAMES,flush=True)
    proc.stdin.close();assert proc.wait()==0
result={'status':'Authoring PASS; encoded movie decode and mapped preview pending','primary_movie':str(primary),'primary_bytes':primary.stat().st_size,'primary_sha256':sha(primary),'resolution':RES,'fps':FPS,'frames':FRAMES,'duration_seconds':FRAMES/FPS,'connected_component_count':len(components),'floor_texels_in_solved_physical_domains':int(coverage.sum()),'wave_transfer_is_world_position_plus_Z_floor_projection':True,'floor_transfer_not_room_label_clipped':True,'actual_walls_glazing_doors_and_near_floor_furniture_define_reflections':True,'invisible_room_boundary_cells':0,'tabletops_overhead_for_physics':True,'static_fixture_height_shading_and_exact_fireplace_patch':True,'same_actual_display_at_initial_last_and_terminal_quiet_states':True,'external_fade_applied':False,'brightness_transfer':{'quiet_water_RGB':[12,72,100],'previous_R02_quiet_water_RGB':[8,38,55],'crest_response':'1-exp(-(max(height,0)*1200)^2)','trough_response':'1-exp(-(max(-height,0)*1000)^2)','bounded_normal_response':'sign(slope)*tanh(abs(slope*400)^1.5)','maximum_dynamic_floor_channel_before_rounding':max(peaks),'white_clipped_wave_pixels':0,'bounded_dynamic_floor_channel_maximum':248},'physical_QA':str(T/'Connected_Wave_Physics_QA.json'),'coverage_QA':str(T/'Whole_Model_Coverage_Preflight.json'),'fixture_QA':str(T/'Solid_Fixture_Volume_QA.json'),'receiver_OBJ':str(hybrid/'CampusCenter_P02plusP03B3_Assembly_1_100_UV02.obj'),'receiver_OBJ_sha256':sha(hybrid/'CampusCenter_P02plusP03B3_Assembly_1_100_UV02.obj'),'geometry_UV_or_prior_files_changed':False,'full_hydraulic_filling_splashes_or_vertical_wall_water_simulated':False,'physical_projection_or_MadMapper_playback_verified':False,'raw_atlas_is_not_camera_view':True}
(D/'Connected_Wave_Transfer_And_Video_QA.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2),flush=True)
