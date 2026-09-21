from pathlib import Path
import numpy as np,json,subprocess
from PIL import Image,ImageDraw
R=Path(__file__).parent;D=R/'depth/108/moving';a=np.load(R/'depth/108/moving_depth_metres.npy')
mask=np.array(Image.open(R.parent/'projection_acrylic_v06/rooms/108/Room_Mask_1024.png').resize((512,512),Image.Resampling.NEAREST))>127
assert a.shape==(105,512,512) and np.isfinite(a[:,mask]).all()
sheet=Image.new('RGB',(4*256,2*280),(20,20,20))
for i,frame in enumerate(a):
    im=Image.fromarray(np.uint8(np.where(mask,np.clip(1-frame/4.5,0,1),0)*255))
    im.save(D/f'{i:04d}.png')
for k,i in enumerate([0,15,30,45,59,74,89,104]):
    im=Image.open(D/f'{i:04d}.png').convert('RGB').resize((256,256));sheet.paste(im,(k%4*256,k//4*280));ImageDraw.Draw(sheet).text((k%4*256+5,k//4*280+257),str(i),fill='white')
sheet.save(D/'Contact_Sheet.jpg')
subprocess.run(['T:/AI/Wan2GP/ffmpeg_bins/ffmpeg.exe','-hide_banner','-loglevel','error','-framerate','24','-i',str(D/'%04d.png'),'-c:v','libx264','-crf','0','-pix_fmt','yuv420p','-y',str(D/'Blender_Moving_Depth.mp4')],check=True)
print('Actual Blender depth sequence encoded: 105 frames at 24 fps.')
