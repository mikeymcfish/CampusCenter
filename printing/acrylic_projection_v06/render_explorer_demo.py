from pathlib import Path
from collections import deque
import sys,json,math,subprocess,hashlib
R=Path(__file__).parent;sys.path.insert(0,str(R.parent/'projection_enclosed_v05/tool_packages'))
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
P=R/'projection';A=P/'assets';O=P/'examples';m=json.loads((P/'map.json').read_text());d=np.load(A/'navigation.npz');walk=d['walkable'];ids=d['room_ids'];valid=np.array(Image.open(A/'receiver.png'))>0;H,W=walk.shape;rooms=m['rooms'];start=tuple(m['start']);base=np.array(Image.open(A/'Explorer_Base.png'));font=ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf',12);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',9)
def bfs(start,goal):
 prev={start:None};q=deque([start])
 while q:
  p=q.popleft()
  if p==goal:break
  for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
   t=(p[0]+dx,p[1]+dy)
   if 0<=t[0]<W and 0<=t[1]<H and walk[t[1],t[0]] and t not in prev:prev[t]=p;q.append(t)
 assert goal in prev;route=[goal]
 while route[-1]!=start:route.append(prev[route[-1]])
 return route[::-1]
targets=[next(r for r in rooms if r['number']==n)['visit_xy'] for n in ['108','102','100']];route=[start]
for target in targets:
 part=bfs(route[-1],tuple(target));route.extend(part[1:]);route.extend([route[-1]]*35)
route.extend(bfs(route[-1],start)[1:]);assert all(walk[y,x] for x,y in route)
cache={}
def card(i):
 if i in cache:return cache[i].copy()
 r=rooms[i];arr=base.copy();mk=(ids==i)&valid;arr[mk]=np.uint8(arr[mk]*.55+np.array([37,209,177])*.45);im=Image.fromarray(arr);dr=ImageDraw.Draw(im);x,y,w,h=m['gym_panel'];dr.rectangle((x,y,x+w,y+h),fill=(9,24,32),outline=(91,213,189));dr.text((x+12,y+8),'KING SCHOOL / DISCOVER THE CAMPUS',font=small,fill=(145,216,202));dr.text((x+12,y+24),r['number']+' '+r['name'],font=font,fill='white');ri=Image.open(P/r['image']).convert('RGB');ri.thumbnail((w-16,h-66));im.paste(ri,(x+(w-ri.width)//2,y+46+(h-66-ri.height)//2));dr.text((x+12,y+h-17),r['image_caption'],font=small,fill=(145,171,186));cache[i]=im;return im.copy()
ff=imageio_ffmpeg.get_ffmpeg_exe();fps=24;N=math.ceil(len(route)/m['speed_px_per_second']*fps);out=O/'Explorer_Demo_1024x786_RGB.mp4';enc=subprocess.Popen([ff,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(fps),'-i','pipe:0','-an','-c:v','libx264rgb','-crf','0','-preset','fast','-pix_fmt','rgb24','-movflags','+faststart',str(out)],stdin=subprocess.PIPE);hashes=[];room=30;shot=False
for f in range(N):
 x,y=route[round(f/(N-1)*(len(route)-1))];i=int(ids[y,x]);room=i if i>=0 else room;im=card(room);dr=ImageDraw.Draw(im);dr.ellipse((x-4,y-3,x+4,y+3),fill=(118,229,204));dr.ellipse((x-2,y-2,x+2,y+2),fill=(241,248,242));arr=np.array(im);arr[~valid]=0;enc.stdin.write(arr.tobytes());hashes.append(hashlib.sha256(arr.tobytes()).hexdigest())
 if rooms[room]['number']=='108' and not shot:Image.fromarray(arr).save(O/'Explorer_Preview.png');shot=True
enc.stdin.close();assert enc.wait()==0
dec=subprocess.Popen([ff,'-v','error','-i',str(out),'-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE);count=0;first=last=None
while True:
 raw=dec.stdout.read(W*H*3)
 if not raw:break
 assert hashlib.sha256(raw).hexdigest()==hashes[count];assert not np.frombuffer(raw,np.uint8).reshape(H,W,3)[~valid].any()
 if first is None:first=raw
 last=raw;count+=1
assert dec.wait()==0 and count==N and first==last
(O/'explorer_validation.json').write_text(json.dumps({'frames':N,'fps':fps,'seconds':N/fps,'route_points':len(route),'all_route_points_walkable':True,'all_frames_blackout':True,'decoded_exact_rgb':True,'first_last_identical':True,'note':'Recorded procedural demonstration of the same navigation grid and room-display behavior; interactive player remains keyboard controlled.'},indent=2));print('EXPLORER_VERIFIED',N,N/fps,flush=True)

