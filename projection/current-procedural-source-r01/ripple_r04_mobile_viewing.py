import os,shutil
from pathlib import Path
from PIL import Image
import subprocess,json,hashlib,numpy as np
R=Path(__file__).parent;T=R/'madmapper_ripple_R04';D=T/'mobile_viewing';D.mkdir(exist_ok=True)
MASTER=T/'whole_model/deliverables/Ripple_R04_Black_Thin_Staggered_Connected_44s_Mapped_1024_Lossless_Reference.mov'
S=T/'whole_model/Mapped_Source_Sequence_1024';FF=Path(os.environ.get('FFMPEG',shutil.which('ffmpeg') or 'ffmpeg'))
OUT=D/'Ripple_R04_Black_Thin_Staggered_44s_Mapped_720_Mobile_Viewing_Only.mp4'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for c in iter(lambda:f.read(8*1024*1024),b''):h.update(c)
    return h.hexdigest()
before=sha(MASTER);assert before=='3ba30a882ae941609e21e451998713df9d8c77392e975f71a743bb1e588a7116'
cmd=[str(FF),'-hide_banner','-loglevel','error','-i',str(MASTER),'-vf','scale=720:-2:flags=lanczos','-an','-c:v','libx264','-crf','23','-preset','slow','-maxrate','1400k','-bufsize','2800k','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT)]
if not OUT.exists():
    with (D/'Mobile_Encoding_Log.txt').open('wb') as log:subprocess.run(cmd,stdout=log,stderr=log,check=True)
assert OUT.stat().st_size<10_000_000,OUT.stat().st_size
probe=json.loads(subprocess.check_output([str(Path(os.environ.get('FFPROBE',shutil.which('ffprobe') or 'ffprobe'))),'-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=codec_name,width,height,r_frame_rate,nb_read_frames,duration','-of','json',str(OUT)]));q=probe['streams'][0];W=int(q['width']);H=int(q['height']);assert W==720 and int(q['nb_read_frames'])==880 and abs(float(q['duration'])-44)<.001 and q['r_frame_rate']=='20/1'
def guard(active,r=12):
    width=2*r+1;i=np.cumsum(np.cumsum(np.pad(active.astype(np.int32),((r+1,r),(r+1,r))),axis=0),axis=1)
    return (i[width:,width:]-i[:-width,width:]-i[width:,:-width]+i[:-width,:-width])>0
far_max=0;far_nonzero=0;far_total=0;far_sum=0;source_black_max=0;errors=[];first=None;last=None
with (D/'Mobile_Decode_Log.txt').open('wb') as log:
    proc=subprocess.Popen([str(FF),'-hide_banner','-loglevel','error','-i',str(OUT),'-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE,stderr=log)
    for frame in range(880):
        chunks=[];size=0;need=W*H*3
        while size<need:
            data=proc.stdout.read(need-size);assert data,('Short actual mobile video decode',frame,size);chunks.append(data);size+=len(data)
        actual=np.frombuffer(b''.join(chunks),np.uint8).reshape(H,W,3)
        ref=np.asarray(Image.open(S/f'frame_{frame:04d}.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS))
        black=~np.any(ref,axis=2);far=~guard(~black);nz=np.any(actual,axis=2);maximum=int(actual[far].max()) if far.any() else 0
        far_max=max(far_max,maximum);far_nonzero+=int((nz&far).sum());far_total+=int(far.sum());far_sum+=int(actual[far].sum());source_black_max=max(source_black_max,int(actual[black].max()) if black.any() else 0)
        if frame==0:first=actual.copy()
        if frame==879:last=actual.copy()
        if frame in [0,60,240,400,640,879]:
            path=D/f'R04_Mobile_Frame_{frame:04d}_Actual_Decoded_720.png';Image.fromarray(actual).save(path)
            error=np.abs(actual.astype(np.int16)-ref.astype(np.int16));errors.append({'frame':frame,'actual_decoded_still':path.name,'mean_RGB_byte_error_against_lossless_source_Pillow_Lanczos_reference':float(error.mean()),'maximum_RGB_byte_error':int(error.max()),'far_background_max_RGB_byte':maximum})
        if frame%100==0:print('R04 MOBILE FULL DECODE/BLACK CHECK',frame,'/880','farmax',far_max,flush=True)
    proc.stdout.close();assert proc.wait()==0
endpoint_metrics={name:{'maximum_RGB_byte':int(value.max()),'nonzero_pixels':int(np.any(value,axis=2).sum()),'mean_RGB_byte':float(value.mean())} for name,value in [('first',first),('last',last)]}
assert sha(MASTER)==before
qa={'status':'PASS: mobile viewing MP4 under10MB; all880 frames decode; black compression noise measured; visual review pending','file':str(OUT),'bytes':OUT.stat().st_size,'sha256':sha(OUT),'width':W,'height':H,'fps':20,'frames':880,'duration_seconds':44,'viewing_only':True,'raw_projection_atlas':False,'transcoded_directly_from_lossless_mapped_master':str(MASTER),'master_sha256_unchanged':before,'animation_sources_geometry_timing_or_wave_treatment_changed':False,'codec':'H264/yuv420p,CRF23,720wide,Lanczos,1400kbit/s maxrate,faststart','all_frames_fully_decoded':True,'first_last_decoded_frames_exact_RGB_black':bool(not np.any(first) and not np.any(last)),'encoded_endpoint_black_noise':endpoint_metrics,'MP4_exact_black_background_claimed':False,'encoded_black_noise':{'far_from_effect_guard_pixels':12,'maximum_RGB_byte':far_max,'nonzero_far_background_samples':far_nonzero,'far_background_samples':far_total,'nonzero_far_background_fraction':far_nonzero/max(far_total,1),'mean_RGB_byte_far_background':far_sum/max(far_total*3,1),'max_RGB_byte_on_source_black_pixels_including_wave_edge_blocks':source_black_max,'note':'Lossy viewing MP4 may add edge/chroma/temporal compression noise. Exact-black lossless mapped/atlas masters are unchanged. Pillow and FFmpeg Lanczos resamplers differ slightly; comparison errors include this.'},'decoded_keyframe_checks':errors,'visual_review_pending':True,'physical_projection_or_MadMapper_playback_verified':False,'probe':probe}
(D/'Mobile_Viewing_Decode_And_Black_QA.json').write_text(json.dumps(qa,indent=2));print(json.dumps({k:qa[k] for k in ['status','file','bytes','sha256','width','height','duration_seconds','encoded_black_noise']},indent=2),flush=True)
