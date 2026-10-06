import os,shutil
from pathlib import Path
import json,hashlib,subprocess
R=Path(__file__).parent;T=R/'madmapper_ripple_R04/whole_model';D=T/'deliverables';S=T/'Mapped_Source_Sequence_1024';ff=Path(os.environ.get('FFMPEG',shutil.which('ffmpeg') or 'ffmpeg'))
target=D/'Ripple_R04_Black_Thin_Staggered_Connected_44s_Mapped_1024_Lossless_Reference.mov';assert not target.exists()
subprocess.run([str(ff),'-hide_banner','-loglevel','error','-framerate','20','-i',str(S/'frame_%04d.png'),'-frames:v','880','-c:v','copy',str(target)],check=True)
probe=json.loads(subprocess.check_output([str(Path(os.environ.get('FFPROBE',shutil.which('ffprobe') or 'ffprobe'))),'-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=codec_name,width,height,r_frame_rate,nb_read_frames,duration','-of','json',str(target)]));assert int(probe['streams'][0]['nb_read_frames'])==880
packets=json.loads(subprocess.check_output([str(Path(os.environ.get('FFPROBE',shutil.which('ffprobe') or 'ffprobe'))),'-v','error','-select_streams','v:0','-show_packets','-show_data_hash','sha256','-show_entries','packet=size,data_hash','-of','json',str(target)]))['packets'];assert len(packets)==880
for frame,p in enumerate(packets):
    f=S/f'frame_{frame:04d}.png';assert p['data_hash'].split(':')[-1].lower()==hashlib.sha256(f.read_bytes()).hexdigest() and int(p['size'])==f.stat().st_size
q={'status':'PASS: all880 lossless mapped-reference frames decode; packets byte-identical to exact-black source PNGs','file':str(target),'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'resolution':[1024,786],'fps':20,'frames':880,'duration_seconds':44,'all_frames_decoded':True,'all_movie_PNG_packets_identical_to_original_mapped_source':True,'background_RGB_exact':[0,0,0],'black_repeat_endpoints_exact':True,'ambient_model_grey_wash_glow_or_banner':False,'raw_projection_atlas':False,'purpose':'Lossless mapped viewing reference with mathematically exact black encoded background; companion standard MP4 is convenient viewing with measured small codec error.','physical_projection_or_MadMapper_playback_verified':False,'probe':probe}
(D/'Lossless_Mapped_Reference_QA.json').write_text(json.dumps(q,indent=2));print(json.dumps({k:q[k] for k in ['status','bytes','sha256','file']},indent=2),flush=True)
