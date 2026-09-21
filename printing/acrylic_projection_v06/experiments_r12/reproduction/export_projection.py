"""Preserve generated clips and export exact-black masked projection masters."""
from pathlib import Path
import json, subprocess, sys
import cv2
import numpy as np
from PIL import Image

R=Path(__file__).parent
n=sys.argv[1]; d=R/('retry' if '--retry' in sys.argv else 'final')/n
status=json.loads((d/'status.json').read_text())
assert status['status']=='finished'
source=Path(status['generated_files'][0])
cap=cv2.VideoCapture(str(source))
w=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));h=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT));fps=cap.get(cv2.CAP_PROP_FPS);total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));first=None
mask=np.asarray(Image.open(R.parent/'projection_acrylic_v06/rooms'/n.split('_')[0]/'Room_Mask_1024.png').convert('L').resize((w,h),Image.Resampling.NEAREST))>127
master=d/'Projection_Lossless.mkv'; preview=d/'Projection_Preview.mp4'
ff='T:/AI/Wan2GP/ffmpeg_bins/ffmpeg.exe'
cmd=[ff,'-y','-v','error','-f','rawvideo','-pixel_format','bgr24','-video_size',f'{w}x{h}','-framerate',str(fps),'-i','pipe:0','-an','-c:v','ffv1','-level','3','-pix_fmt','bgr0',str(master)]
p=subprocess.Popen(cmd,stdin=subprocess.PIPE);count=0
while True:
    ok,frame=cap.read()
    if not ok:break
    frame[~mask]=0
    if first is None:first=frame.copy()
    if count>=total-6:
        amount=(count-(total-7))/6
        amount=amount*amount*(3-2*amount)
        frame=np.rint(frame.astype(np.float32)*(1-amount)+first.astype(np.float32)*amount).astype(np.uint8)
    p.stdin.write(frame.tobytes());count+=1
cap.release();p.stdin.close();assert p.wait()==0
subprocess.run([ff,'-y','-v','error','-i',str(master),'-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(preview)],check=True)
check=cv2.VideoCapture(str(master));verified=0;outside_max=0;check_first=None;check_last=None
while True:
    ok,frame=check.read()
    if not ok:break
    if check_first is None:check_first=frame.copy()
    check_last=frame
    outside_max=max(outside_max,int(frame[~mask].max()) if (~mask).any() else 0);verified+=1
check.release();assert verified==count and outside_max==0 and np.array_equal(check_first,check_last)
(d/'projection_export.json').write_text(json.dumps({'source':str(source),'lossless_master':str(master),'preview':str(preview),'frames':count,'fps':fps,'outside_mask_max_lossless':outside_max,'closing_blend_frames':6,'first_last_lossless_identical':True,'mask':'Original Blender room mask, nearest-neighbor resized','limitations':'Final six frames gently blend to the opening encoded frame to close the loop. Masking does not correct generated interior geometry or motion. H264 preview can have slight compression bleed; use FFV1 master when exact black outside the mask matters.'},indent=2))
print(n,count,'frames verified; outside-mask RGB is exactly zero in lossless master')
