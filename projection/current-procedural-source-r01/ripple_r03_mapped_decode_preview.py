import os,shutil
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from hybrid_projection_cache import load
from production_common import sha
import numpy as np,json,subprocess
R=Path(__file__).parent;D=R/'madmapper_ripple_R03/whole_model/deliverables';RES=4096;FPS=20;FRAMES=800
src=D/'Ripple_R03_WholeModel_Connected_UV02_1_100_4096_HAP.mov';target=D/'Ripple_R03_WholeModel_Connected_Mapped_1024_Viewing_Preview.mp4';assert not target.exists()
ffmpeg=Path(os.environ.get('FFMPEG',shutil.which('ffmpeg') or 'ffmpeg'));cache=load();mask=cache['material']>0
xx=np.clip(np.floor(cache['u']*RES).astype(int),0,RES-1);yy=np.clip(np.floor((1-cache['v'])*RES).astype(int),0,RES-1)
FONT=r'C:\Windows\Fonts\segoeui.ttf';decoded=0;first=None;last=None;keyframe_errors=[]
dec_cmd=[str(ffmpeg),'-hide_banner','-loglevel','error','-i',str(src),'-f','rawvideo','-pix_fmt','rgb24','pipe:1']
enc_cmd=[str(ffmpeg),'-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1024x846','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-crf','17','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart',str(target)]
with (D/'Decode_And_Preview_Encoding_Log.txt').open('wb') as log:
    decode=subprocess.Popen(dec_cmd,stdout=subprocess.PIPE,stderr=log);encode=subprocess.Popen(enc_cmd,stdin=subprocess.PIPE,stderr=log)
    for frame in range(FRAMES):
        want=RES*RES*3;parts=[];size=0
        while size<want:
            data=decode.stdout.read(want-size);assert data,('Short actual movie decode',frame,size);parts.append(data);size+=len(data)
        atlas=np.frombuffer(b''.join(parts),np.uint8).reshape(RES,RES,3)
        if frame==0:first=atlas.copy()
        if frame==FRAMES-1:last=atlas.copy()
        if frame in [0,60,120,200,400,799]:
            Image.fromarray(atlas).save(D/f'Ripple_R03_Frame_{frame:04d}_Decoded_Atlas_4096.png')
            source=np.asarray(Image.open(D/f'Ripple_R03_Frame_{frame:04d}_Source_Atlas_4096.png').convert('RGB'))
            error=np.abs(atlas.astype(np.int16)-source.astype(np.int16));keyframe_errors.append({'frame':frame,'HAP_lossy_mean_absolute_RGB_byte_error':float(error.mean()),'HAP_lossy_max_RGB_byte_error':int(error.max())})
        mapped=np.zeros((*mask.shape,3),np.uint8);mapped[mask]=atlas[yy[mask],xx[mask]]
        im=Image.fromarray(mapped).resize((1024,786),Image.Resampling.LANCZOS);out=Image.new('RGB',(1024,846),(10,17,25));out.paste(im,(0,60));draw=ImageDraw.Draw(out)
        draw.text((14,7),'Ripple R03 | whole model | connected open areas | brighter water',font=ImageFont.truetype(FONT,20),fill='white')
        draw.text((14,33),'Actual decoded atlas mapped through UV02 | only geometry reflects | projector playback untested',font=ImageFont.truetype(FONT,15),fill=(169,192,205))
        encode.stdin.write(out.tobytes());decoded+=1
        if frame in [0,60,120,200,400,799]:out.save(D/f'Ripple_R03_Frame_{frame:04d}_Mapped_1024_Viewing.png')
        if frame%100==0:print('ACTUAL HAP DECODE / MAPPED VIEWING VIDEO',frame,'/',FRAMES,flush=True)
    decode.stdout.close();encode.stdin.close();assert decode.wait()==0 and encode.wait()==0
assert np.array_equal(first,last),'Encoded quiet movie endpoints differ'
info=json.loads(subprocess.check_output([str(Path(os.environ.get('FFPROBE',shutil.which('ffprobe') or 'ffprobe'))),'-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=codec_name,width,height,r_frame_rate,nb_read_frames,duration','-of','json',str(target)]));assert int(info['streams'][0]['nb_read_frames'])==FRAMES
subprocess.run([str(ffmpeg),'-hide_banner','-loglevel','error','-i',str(target),'-f','null','-'],check=True)
record={'status':'PASS: compact mapped preview created from fully decoded actual HAP atlas; visual native review pending','file':str(target),'bytes':target.stat().st_size,'sha256':sha(target),'width':1024,'height':846,'fps':FPS,'frames':FRAMES,'duration_seconds':FRAMES/FPS,'raw_atlas_playback_file':False,'actual_primary_movie':str(src),'actual_primary_movie_sha256':sha(src),'all_primary_atlas_movie_frames_decoded':decoded,'actual_decoded_primary_first_and_last_frames_equal_after_natural_decay':True,'all_compact_preview_frames_decoded':True,'projection_reference':'Exact receiver triangles and UVs, including restored fireplace visibility; unchanged +Z orthographic view','invisible_room_boundary_reflections':False,'keyframe_lossy_codec_error':keyframe_errors,'physical_projection_or_MadMapper_playback_verified':False,'visual_review_pending':True,'codec_probe':info}
(D/'Compact_Mapped_Preview_QA.json').write_text(json.dumps(record,indent=2))
transfer=json.loads((D/'Connected_Wave_Transfer_And_Video_QA.json').read_text());transfer.update({'status':'PASS: actual encoded raw atlas fully decoded and mapped viewing preview built','all_primary_movie_frames_decoded':decoded,'actual_decoded_first_and_last_quiet_frames_equal':True,'mapped_viewing_preview':str(target),'native_receiver_reapplication_pending':True});(D/'Connected_Wave_Transfer_And_Video_QA.json').write_text(json.dumps(transfer,indent=2))
print(json.dumps(record,indent=2),flush=True)
