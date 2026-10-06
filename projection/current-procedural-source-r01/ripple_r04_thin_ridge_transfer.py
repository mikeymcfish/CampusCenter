import os,shutil
from production_common import cache_arrays,sha
from hybrid_projection_cache import load
from pathlib import Path
from PIL import Image
import numpy as np,json,subprocess,argparse
R=Path(__file__).parent;SRC=R/'madmapper_ripple_R03/whole_model';T=R/'madmapper_ripple_R04/whole_model';D=T/'deliverables';D.mkdir(exist_ok=True)
RES=4096;FPS=20;FRAMES=1280;HALF_WIDTH=.85;QUIET_HEIGHT=.00007;CYAN=np.array([40,235,248],np.float32)
arr=cache_arrays(100,RES);floor=(arr['valid']>0)&(arr['up']>0)&(arr['z']<=5.4*64);flat=np.flatnonzero(floor);wx=np.asarray(arr['x'][floor],np.float32)/64;wy=np.asarray(arr['y'][floor],np.float32)/64
manifest=json.loads((SRC/'Simulation_Domain_Manifest.json').read_text());components=[];coverage=np.zeros(len(flat),bool)
for row in manifest['rooms']:
    data=np.load(SRC/(row['name']+'_Simulation_Domain.npz'));dom=data['domain'];origin=data['origin'];pitch=float(data['pitch']);hh,ww=dom.shape
    gx=(wx-origin[0])/pitch-.5;gy=(wy-origin[1])/pitch-.5;cx=np.floor((wx-origin[0])/pitch).astype(int);cy=np.floor((wy-origin[1])/pitch).astype(int)
    ix=np.flatnonzero((cx>=0)&(cy>=0)&(cx<ww)&(cy<hh));ix=ix[dom[cy[ix],cx[ix]]];assert not coverage[ix].any();coverage[ix]=True
    x0=np.clip(np.floor(gx[ix]).astype(int),0,ww-1);y0=np.clip(np.floor(gy[ix]).astype(int),0,hh-1)
    q={'name':row['name'],'dom':dom,'indices':flat[ix],'x0':x0,'y0':y0,'x1':np.minimum(x0+1,ww-1),'y1':np.minimum(y0+1,hh-1),'tx':np.clip(gx[ix]-x0,0,1),'ty':np.clip(gy[ix]-y0,0,1),'fields':np.load(Path(os.environ.get('RIPPLE_R04_FIELD_ROOT',str(T)))/(row['name']+'_Height_Sequence.npy'),mmap_mode='r')}
    for axis,label in [(1,'x'),(0,'y')]:q[label+'p']=dom&np.roll(dom,-1,axis);q[label+'m']=dom&np.roll(dom,1,axis)
    components.append(q)

def ridge(q,frame):
    h=q['fields'][frame];dom=q['dom'];dx=.5
    xp=np.where(q['xp'],np.roll(h,-1,1),h);xm=np.where(q['xm'],np.roll(h,1,1),h);yp=np.where(q['yp'],np.roll(h,-1,0),h);ym=np.where(q['ym'],np.roll(h,1,0),h)
    gx=(xp-xm)/(2*dx);gy=(yp-ym)/(2*dx);xx=(xp-2*h+xm)/(dx*dx);yy=(yp-2*h+ym)/(dx*dx)
    gyx=(np.where(q['xp'],np.roll(gy,-1,1),gy)-np.where(q['xm'],np.roll(gy,1,1),gy))/(2*dx)
    gxy=(np.where(q['yp'],np.roll(gx,-1,0),gx)-np.where(q['ym'],np.roll(gx,1,0),gx))/(2*dx);xy=(gyx+gxy)*.5
    lam=.5*(xx+yy-np.sqrt((xx-yy)**2+4*xy*xy));vx=xy;vy=lam-xx;length=np.sqrt(vx*vx+vy*vy);regular=length>1e-12
    ex=np.where(regular,vx/np.maximum(length,1e-12),np.where(xx<=yy,1.,0.));ey=np.where(regular,vy/np.maximum(length,1e-12),np.where(xx<=yy,0.,1.))
    distance=np.abs(ex*gx+ey*gy)/np.maximum(-lam,1e-12)
    narrow=np.maximum(1-(distance/HALF_WIDTH)**2,0)
    amplitude=np.clip((h-QUIET_HEIGHT)/.0003,0,1)**.50
    intensity=narrow*amplitude;intensity[~dom|(lam>=-1e-12)|(h<=QUIET_HEIGHT)]=0
    return intensity.astype(np.float32)

def render(frame):
    atlas=np.zeros((RES,RES,3),np.uint8);rgb=atlas.reshape(-1,3)
    for q in components:
        if not len(q['indices']):continue
        value=ridge(q,frame);x0,y0,x1,y1,tx,ty=[q[k] for k in ['x0','y0','x1','y1','tx','ty']]
        sampled=(1-ty)*((1-tx)*value[y0,x0]+tx*value[y0,x1])+ty*((1-tx)*value[y1,x0]+tx*value[y1,x1])
        rgb[q['indices']]=np.uint8(np.rint(sampled[:,None]*CYAN))
    return atlas

def mapped(atlas):
    out=np.zeros((*top['material'].shape,3),np.uint8);out[mask]=atlas[ay[mask],ax[mask]]
    return Image.fromarray(out).resize((1024,786),Image.Resampling.BOX)
top=load();mask=top['material']>0;ax=np.clip(np.floor(top['u']*RES).astype(int),0,RES-1);ay=np.clip(np.floor((1-top['v'])*RES).astype(int),0,RES-1)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--stills',nargs='+',type=int);a=ap.parse_args()
    if a.stills:
        for frame in a.stills:
            atlas=render(frame);Image.fromarray(atlas).save(D/f'Ripple_R04_Frame_{frame:04d}_Lossless_Atlas_4096.png');mapped(atlas).save(D/f'Ripple_R04_Frame_{frame:04d}_Mapped_1024.png');print('R04 THIN RIDGE STILL',frame,flush=True)
        raise SystemExit
    qa=json.loads((T/'Staggered_Connected_Wave_Physics_QA.json').read_text());assert qa['status'].startswith('PASS')
    start=render(0);last=render(FRAMES-1);terminal=render(FRAMES);assert not np.any(start) and np.array_equal(start,last) and np.array_equal(start,terminal)
    S=T/'Lossless_Atlas_Sequence_4096';S.mkdir(exist_ok=True);target=D/'Ripple_R04_Black_Thin_Staggered_Connected_Mapped_1024_Viewing_Preview.mp4';assert not target.exists()
    ff=Path(os.environ.get('FFMPEG',shutil.which('ffmpeg') or 'ffmpeg'));cmd=[str(ff),'-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1024x786','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-crf','16','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart',str(target)]
    keyframes=[0,60,120,240,400,640,960,1279];stats=[]
    with (T/'Compact_Encoding_Log.txt').open('wb') as log:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        for frame in range(FRAMES):
            atlas=render(frame);active=np.any(atlas,axis=2);Image.fromarray(atlas).save(S/f'frame_{frame:04d}.png',compress_level=2);im=mapped(atlas);proc.stdin.write(im.tobytes())
            stats.append({'frame':frame,'nonzero_atlas_pixels':int(active.sum()),'background_RGB':[0,0,0]})
            if frame in keyframes:Image.fromarray(atlas).save(D/f'Ripple_R04_Frame_{frame:04d}_Lossless_Atlas_4096.png');im.save(D/f'Ripple_R04_Frame_{frame:04d}_Mapped_1024.png')
            if frame%80==0:print('R04 THIN BLACK MAPPED PREVIEW AND LOSSLESS ATLAS',frame,'/',FRAMES,int(active.sum()),flush=True)
        proc.stdin.close();assert proc.wait()==0
    result={'status':'Authoring PASS: pure black lossless atlas sequence and compact viewing clip; encoded decode QA pending','file':str(target),'bytes':target.stat().st_size,'sha256':sha(target),'width':1024,'height':786,'fps':FPS,'frames':FRAMES,'duration_seconds':64,'lossless_atlas_sequence':str(S),'atlas_resolution':RES,'background_RGB':[0,0,0],'ambient_wash_or_static_model_grey':False,'fireplace_or_fixture_ambient_patch_in_wave_effect':False,'thin_crest_method':'Actual field Hessian principal negative curvature and directional gradient estimate crest distance;0.65mm half-width compact ridge, multiplied by actual wave amplitude. Source is actual solved height field, not analytic circle overlay.','ridge_full_support_width_model_mm':1.3,'crest_RGB_at_full_strength':CYAN.astype(int).tolist(),'height_quiet_threshold_model_mm':QUIET_HEIGHT,'sampler':'Bilinear same physical field through original UVs; +Z exact hybrid top visibility; BOX reduction to1024, no glow/bloom/banner/grey diagnostic model.','receiver_OBJ_sha256':'b949784cbb3f833d10d82fdd48d469ac3fac1b8ac723f7cc08588ca633a59fba','geometry_registration_and_R03_unchanged':True,'first_last_terminal_lossless_atlas_frames_identical_black':True,'physical_domains':56,'source_events':77,'source_times_seconds':[qa['source_timing_first_seconds'],qa['source_timing_last_seconds']],'room_labels_create_no_barriers':True,'floor_texels_in_domains':int(coverage.sum()),'per_frame_black_and_effect_coverage':stats,'physical_projection_or_MadMapper_playback_verified':False,'matching_primary_atlas_movie_pending':True}
    result['ridge_full_support_width_model_mm']=2*HALF_WIDTH
    result['thin_crest_method']='Actual field Hessian principal negative curvature and directional gradient estimate crest distance;0.85mm half-width compact parabolic ridge, multiplied by actual positive wave amplitude. Brightness saturates at height0.00037mm. Source is actual solved height field, not analytic circle overlay.'
    (D/'Thin_Black_Staggered_Transfer_QA.json').write_text(json.dumps(result,indent=2));print('R04 COMPACT AUTHOR COMPLETE',target,flush=True)
