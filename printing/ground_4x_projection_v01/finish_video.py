from pathlib import Path
import json,subprocess,hashlib
import numpy as np
from PIL import Image
R=Path(__file__).parent;O=R/'projection';cfg=json.loads((R/'projector_config.json').read_text());done=json.loads((O/'render_complete.json').read_text());N=cfg['fps']*cfg['loop_seconds'];assert done['frames']==N
mask=np.array(Image.open(O/'receiver_mask.png').convert('RGBA'))[:,:,3].astype(float)/255
frames=O/'masked_frames';frames.mkdir(exist_ok=True);metrics=[];steps=[];previous=None
for i in range(1,N+1):
 p=O/'frames'/f'{i:04}.png';im=Image.open(p).convert('RGBA');assert im.size==(cfg['width'],cfg['height']);a=np.array(im).astype(float);rgb=np.uint8(np.clip(a[:,:,:3]*(a[:,:,3:4]/255)*mask[:,:,None],0,255));Image.fromarray(rgb).save(frames/f'{i:04}.png')
 assert not np.any(rgb[mask==0]);metrics.append(float(rgb.mean()))
 if previous is not None:steps.append(float(np.abs(rgb.astype(float)-previous).mean()))
 previous=rgb.astype(float)
for name in ['receiver_mask','calibration_25mm']:
 im=Image.open(O/(name+'.png')).convert('RGBA');a=np.array(im).astype(float);rgb=np.uint8(a[:,:,:3]*a[:,:,3:4]/255);Image.fromarray(rgb).save(O/(name+'_black.png'))
ff='T:/AI/ffmpeg/bin/ffmpeg.exe';video=O/'Campus_Center_Ground_Loop_1024x786.mp4'
subprocess.run([ff,'-y','-framerate',str(cfg['fps']),'-i',str(frames/'%04d.png'),'-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
probe=json.loads(subprocess.check_output(['T:/AI/ffmpeg/bin/ffprobe.exe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]));v=probe['streams'][0];assert (v['width'],v['height'])==(cfg['width'],cfg['height']) and int(v['nb_read_frames'])==N and abs(float(probe['format']['duration'])-cfg['loop_seconds'])<.01
first=np.array(Image.open(frames/'0001.png')).astype(float);last=np.array(Image.open(frames/f'{N:04}.png')).astype(float);mid=np.array(Image.open(frames/f'{N//2:04}.png')).astype(float)
report={'status':'passed','video':video.name,'frame_count':N,'duration_seconds':cfg['loop_seconds'],'dimensions':[cfg['width'],cfg['height']],'first_last_mean_difference':float(abs(first-last).mean()),'first_middle_mean_difference':float(abs(first-mid).mean()),'outside_mask_black':True,'sha256':hashlib.sha256(video.read_bytes()).hexdigest()}
assert report['first_middle_mean_difference']>.02
report['median_adjacent_frame_difference']=float(np.median(steps));report['maximum_adjacent_frame_difference']=float(max(steps));report['loop_seam_within_normal_frame_variation']=report['first_last_mean_difference']<=max(steps)*1.5
assert report['loop_seam_within_normal_frame_variation']
(O/'video_validation.json').write_text(json.dumps(report,indent=2));Image.open(frames/'0001.png').save(O/'Projection_Preview.jpg',quality=95);print(report)
