from pathlib import Path
import sys,json,math,subprocess,hashlib
R=Path(__file__).parent;sys.path.insert(0,str(R.parent/'projection_furnished_v04/python_packages'));sys.path.insert(0,str(R.parent/'projection_enclosed_v05/tool_packages'))
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
P=R/'projection';A=P/'assets';O=P/'examples';O.mkdir(exist_ok=True)
d=np.load(A/'surface_data.npz');valid=d['valid'];h=d['height_mm'];normal=d['normal'];edge=d['edge'];dist=d['distance_px'];furn=d['furniture'];H,W=valid.shape;yy,xx=np.indices((H,W));base=np.array(Image.open(A/'Explorer_Base.png')).astype(np.float32);ink=np.array(Image.open(A/'Ink_Map.png')).astype(np.float32)
height=np.maximum(0,h-4.8);shade=.45+.55*np.maximum(0,normal[:,:,2]);radius=np.sqrt(((xx-600)*830/W)**2+((yy-550)*830/W)**2+(height*5)**2)
def frame(mode,phase):
 t=phase*2*math.pi
 if mode=='Depth_Contours':
  contour=np.exp(-((np.mod(height/5-phase*2,1)-.5)/.085)**2)*furn
  edgewave=np.exp(-((np.mod(dist/18-phase*2,1)-.5)/.12)**2)*.28
  a=base*.6; a+=contour[:,:,None]*np.array([40,185,220]);a+=edgewave[:,:,None]*np.array([30,120,100]);a[furn]+=np.array([30,40,70])*shade[furn,None];a[edge]=[60,125,140]
 elif mode=='Surface_Ripples':
  wave=(.5+.5*np.cos(radius*.12-t*3))**10;fine=(.5+.5*np.sin(radius*.031+t))**4
  a=base*.35+wave[:,:,None]*np.array([42,150,205])*shade[:,:,None]+fine[:,:,None]*np.array([43,24,68]);a[edge]+=np.array([20,50,70])
 elif mode=='Architecture_Scan':
  field=xx/W+height/90;band=np.exp(-((np.mod(field-phase*2,1)-.5)/.042)**2);line=(.5+.5*np.cos(dist*.9-t*4))**14
  a=base*.45+band[:,:,None]*np.array([90,215,160])*shade[:,:,None]+(line*band)[:,:,None]*np.array([80,30,20]);a[furn]+=np.array([16,25,37]);a[edge]+=np.array([24,48,40])
 else:
  wave=(.5+.5*np.cos((xx+yy)*.012-t))**18;brightness=.82+.18*wave;a=ink*brightness[:,:,None]
 a=np.uint8(np.clip(a,0,255));a[~valid]=0;return a
ff=imageio_ffmpeg.get_ffmpeg_exe();report=[];FPS=24;N=192
for mode in ['Ink_Map_Loop','Depth_Contours','Surface_Ripples','Architecture_Scan']:
 out=O/(mode+'_1024x786_RGB.mp4');cmd=[ff,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264rgb','-crf','0','-preset','fast','-pix_fmt','rgb24','-movflags','+faststart',str(out)]
 enc=subprocess.Popen(cmd,stdin=subprocess.PIPE);hashes=[]
 for i in range(N):
  a=frame(mode,i/(N-1));assert not a[~valid].any();enc.stdin.write(a.tobytes());hashes.append(hashlib.sha256(a.tobytes()).hexdigest())
  if i==N//3:Image.fromarray(a).save(O/(mode+'_Preview.png'))
 enc.stdin.close();assert enc.wait()==0
 # Decode the actual delivered file; exact RGB + black receiver margins must survive encoding.
 dec=subprocess.Popen([ff,'-v','error','-i',str(out),'-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE);count=0;first=last=None
 while True:
  raw=dec.stdout.read(W*H*3)
  if not raw:break
  assert len(raw)==W*H*3;arr=np.frombuffer(raw,np.uint8).reshape(H,W,3);assert not arr[~valid].any();assert hashlib.sha256(raw).hexdigest()==hashes[count]
  if first is None:first=raw
  last=raw;count+=1
 assert dec.wait()==0 and count==N and first==last
 report.append({'file':out.name,'frames':count,'fps':FPS,'seconds':N/FPS,'decoded_exact_rgb':True,'all_frames_blackout_pass':True,'first_last_identical':True,'resolution':[W,H]});print('EFFECT_VERIFIED',mode,flush=True)
(O/'video_validation.json').write_text(json.dumps(report,indent=2))
