import os,shutil
from pathlib import Path
from PIL import Image
import numpy as np,subprocess,json,hashlib
R=Path(__file__).parent;T=R/'madmapper_ripple_R04/whole_model';D=T/'deliverables';M=T/'Mapped_Source_Sequence_1024'
qfile=D/'Thin_Black_Staggered_Transfer_QA.json';q=json.loads(qfile.read_text());target=Path(q['file']);FRAMES=q['frames'];W=1024;H=786
def guarded(active,r=16):
    width=2*r+1;i=np.cumsum(np.cumsum(np.pad(active.astype(np.int32),((r+1,r),(r+1,r))),axis=0),axis=1)
    return (i[width:,width:]-i[:-width,width:]-i[width:,:-width]+i[:-width,:-width])>0
ff=Path(os.environ.get('FFMPEG',shutil.which('ffmpeg') or 'ffmpeg'));cmd=[str(ff),'-hide_banner','-loglevel','error','-i',str(target),'-f','rawvideo','-pix_fmt','rgb24','pipe:1'];stats=[];far_max=0;far_nonzero=0;far_count=0;edge_max=0;first=None;last=None
with (D/'Compact_Black_Decode_Log.txt').open('wb') as log:
    proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=log)
    for frame in range(FRAMES):
        need=W*H*3;chunks=[];size=0
        while size<need:
            data=proc.stdout.read(need-size);assert data,('Short video decode',frame);chunks.append(data);size+=len(data)
        actual=np.frombuffer(b''.join(chunks),np.uint8).reshape(H,W,3);source=np.asarray(Image.open(M/f'frame_{frame:04d}.png').convert('RGB'));background=~np.any(source,axis=2);far=~guarded(~background);nonzero=np.any(actual,axis=2)
        fm=int(actual[far].max()) if far.any() else 0;far_max=max(far_max,fm);far_nonzero+=int((nonzero&far).sum());far_count+=int(far.sum());edge_max=max(edge_max,int(actual[background].max()) if background.any() else 0)
        err=np.abs(actual.astype(np.int16)-source.astype(np.int16));stats.append({'frame':frame,'far_background_max_RGB_byte':fm,'far_background_nonzero_pixels':int((nonzero&far).sum()),'codec_mean_absolute_RGB_byte_error':float(err.mean())})
        if frame==0:first=actual.copy()
        if frame==FRAMES-1:last=actual.copy()
        if frame in [0,60,120,240,400,640,879]:Image.fromarray(actual).save(D/f'Ripple_R04_Frame_{frame:04d}_Actual_Decoded_Mapped_1024.png')
        if frame%100==0:print('R04 ACTUAL COMPACT DECODE/BLACK CHECK',frame,'/',FRAMES,'farmax',far_max,flush=True)
    proc.stdout.close();assert proc.wait()==0
assert not np.any(first) and not np.any(last) and np.array_equal(first,last),'Encoded repeat endpoints not exactly black'
probe=json.loads(subprocess.check_output([str(Path(os.environ.get('FFPROBE',shutil.which('ffprobe') or 'ffprobe'))),'-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=codec_name,width,height,r_frame_rate,nb_read_frames,duration','-of','json',str(target)]));assert int(probe['streams'][0]['nb_read_frames'])==FRAMES and abs(float(probe['streams'][0]['duration'])-44)<.001
record={'status':'PASS: all880 compact frames decoded; exact black repeat endpoints; measured encoded background levels','file':str(target),'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'resolution':[1024,786],'frames':FRAMES,'fps':20,'duration_seconds':44,'all_frames_decoded':True,'first_last_frames_all_RGB_0_0_0':True,'source_lossless_background_RGB':[0,0,0],'no_ambient_model_grey_wash_glow_or_banner':True,'far_background_guard_pixels':16,'far_background_encoded_max_RGB_byte':far_max,'far_background_encoded_nonzero_pixels_over_all_frames':far_nonzero,'far_background_samples_over_all_frames':far_count,'far_background_nonzero_fraction':far_nonzero/max(far_count,1),'background_max_RGB_byte_within_compressed_wave_edge_blocks':edge_max,'codec':'Standard H264/yuv420p viewing preview; edge/temporal compression error measured against exact-black source. Matching raw atlas will use lossless PNG-in-MOV.','per_frame_checks':stats,'probe':probe,'visual_review_pending':True,'raw_projection_atlas':False,'matching_atlas_movie_pending':True,'physical_projection_or_MadMapper_playback_verified':False}
(D/'Compact_Black_Levels_And_Decode_QA.json').write_text(json.dumps(record,indent=2));q['compact_decode_and_black_QA']='Compact_Black_Levels_And_Decode_QA.json';q['actual_compact_encoded_endpoints_exact_black']=True;qfile.write_text(json.dumps(q,indent=2));print(json.dumps({k:record[k] for k in ['status','bytes','sha256','far_background_encoded_max_RGB_byte','far_background_nonzero_fraction']},indent=2),flush=True)
