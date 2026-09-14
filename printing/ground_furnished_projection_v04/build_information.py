from pathlib import Path
import sys,json,math,heapq,subprocess,hashlib
R=Path(__file__).parent;sys.path.insert(0,str(R/'python_packages'))
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_erosion,distance_transform_edt,gaussian_filter
W,H=2048,1572;Q=2;FPS=24
OUT=R/'information';OUT.mkdir(exist_ok=True)
def readmask(name):return np.array(Image.open(R/name).convert('L'))>127
raw=readmask('receiver_mask.png');valid=binary_erosion(raw,iterations=2)
floor=readmask('floor_mask.png')&valid;furn=readmask('furniture_mask.png')&valid
Image.fromarray(np.uint8(valid)*255).save(OUT/'Projection_Validity.png')
def wp(x,y):return (512+(x+13.356249809265137)*1024/69.1622314453125,393-(y-22.987499237060547)*1024/69.1622314453125)
def boxzone(bounds):
    x0,y0,x1,y1=bounds;a=wp(x0,y0);b=wp(x1,y1);im=Image.new('L',(W,H));ImageDraw.Draw(im).rectangle([round(a[0]*Q),round(b[1]*Q),round(b[0]*Q),round(a[1]*Q)],fill=255);return np.array(im)>0
zones={
 'commons':{'bounds':[.15,14.7,16.4,30.9],'label':'COMMONS 102','color':[75,215,240],'preferred':[6,26]},
 'cafe':{'bounds':[12,14.7,16.4,20.3],'label':'CAFE 101','color':[255,193,92],'preferred':[14,17]},
 'ilab':{'bounds':[-11.8,.1,-.2,9.35],'label':'iLAB 108','color':[86,225,189],'preferred':[-6.6,8.5]},
 'learning':{'bounds':[-26.6,6.4,-14.3,13.05],'label':'LEARNING','color':[155,157,255],'preferred':[-23.5,11.5]},
 'gallery':{'bounds':[.1,.1,12.25,8.7],'label':'GALLERY 105','color':[255,151,121],'preferred':[6,4]},
 'athletics':{'bounds':[-45.8,6,-26,40.6],'label':'ATHLETICS','color':[255,199,108],'preferred':[-29,35]},
 'gym':{'bounds':[-25.7,16.38,-.16,47.24],'label':'GYM','color':[255,199,108],'preferred':[-13,20]}}
for z in zones.values():z['mask']=boxzone(z['bounds'])&valid;z['edge']=z['mask']&~binary_erosion(z['mask'],iterations=3)
chapters=[
 {'name':'Welcome','start':0,'duration':6,'title':['A PLACE TO','COME TOGETHER'],'body':['Explore the ground floor','Gather. Learn. Make. Play.'],'zones':['commons','ilab','learning','gallery','athletics','gym'],'color':[75,215,240],'target':[6,26],'narration':'The Campus Center brings shared spaces, learning, innovation and athletics together on one connected ground floor.'},
 {'name':'Commons & cafe','start':6,'duration':7,'title':['MEET &','CONNECT'],'body':['Student commons and cafe','Space to study, share and recharge'],'zones':['commons','cafe'],'color':[75,215,240],'target':[6,26],'narration':'The student commons and cafe form the social heart of the building, with seating for conversation, independent work and group study.'},
 {'name':'Innovation lab','start':13,'duration':8,'title':['DESIGN.','MAKE. TEST.'],'body':['Innovation Lab 108','3D printing and digital fabrication'],'zones':['ilab'],'color':[86,225,189],'target':[-6.6,6],'narration':'In the innovation lab, collaboration tables and workbenches sit alongside 3D printers and digital fabrication equipment.'},
 {'name':'Learning & gallery','start':21,'duration':7,'title':['IDEAS IN','ACTION'],'body':['Collaboration and Aspire classrooms','A gallery for work in progress'],'zones':['learning','gallery'],'color':[155,157,255],'target':[-22.5,14.8],'narration':'Collaboration rooms and the Aspire classroom support learning together. The gallery gives students a place to share their work. The illuminated route stops in the shared corridor outside the learning rooms.'},
 {'name':'Athletics','start':28,'duration':7,'title':['MOVE &','BELONG'],'body':['Gym, team spaces and athletics offices','Locker rooms and changing facilities'],'zones':['athletics','gym'],'color':[255,199,108],'target':[-29,35],'narration':'The gym connects to athletics offices, training spaces and locker rooms through the trophy hall and west-side corridors.'},
 {'name':'Connections','start':35,'duration':7,'title':['ONE CONNECTED','CAMPUS'],'body':['Follow the shared ground-floor route','Return to the entrance to explore again'],'zones':['commons','ilab','learning','gallery','athletics','gym'],'color':[75,215,240],'target':[-29,35],'narration':'Shared corridors link the entrance, commons, innovation lab, learning rooms and athletics spaces.'}]
duration=sum(c['duration'] for c in chapters)
fontpath='C:/Windows/Fonts/segoeui.ttf';boldpath='C:/Windows/Fonts/seguisb.ttf'
def font(size,bold=False):return ImageFont.truetype(boldpath if bold else fontpath,round(size*Q))
def txt(draw,xy,text,size=12,color=(220,235,245),bold=False,anchor='mm'):
    draw.text((xy[0]*Q,xy[1]*Q),text,font=font(size,bold),fill=tuple(color),anchor=anchor)
def rect(draw,bb,fill,outline=None,width=1):draw.rounded_rectangle(tuple(round(x*Q) for x in bb),radius=5*Q,fill=fill,outline=outline,width=round(width*Q))
# Actual navigable floor mask; no route is allowed to cross furniture or walls.
walk=floor.reshape(H//2,2,W//2,2).all(axis=(1,3));walk=binary_erosion(walk,iterations=1)
def nearest(pt):
    x,y=pt;yy,xx=np.where(walk);j=np.argmin((xx-x)**2+(yy-y)**2);return (int(xx[j]),int(yy[j]))
start=nearest(wp(17.7,12))
def astar(goal):
    goal=nearest(wp(*goal));heap=[(0,0,start)];cost={start:0};prev={};found=False
    while heap:
        _,g,p=heapq.heappop(heap)
        if p==goal:found=True;break
        if g!=cost.get(p):continue
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]:
            x,y=p[0]+dx,p[1]+dy
            if not(0<=x<1024 and 0<=y<786 and walk[y,x]):continue
            if dx and dy and not(walk[p[1],x] and walk[y,p[0]]):continue
            ng=g+(1.41421356237 if dx and dy else 1);q=(x,y)
            if ng<cost.get(q,1e99):cost[q]=ng;prev[q]=p;heapq.heappush(heap,(ng+math.hypot(x-goal[0],y-goal[1]),ng,q))
    if not found:return []
    route=[goal]
    while route[-1]!=start:route.append(prev[route[-1]])
    return route[::-1]
routes=[astar(c['target']) for c in chapters]
routes[-1]=routes[-1][::-1]  # The final chapter returns toward the entrance.
print('ROUTE_CHECK',start,[(c['name'],nearest(wp(*c['target'])),len(r)) for c,r in zip(chapters,routes)],flush=True)
assert all(routes),'A chapter route is not connected through the existing openings'
for route in routes:assert all(walk[y,x] for x,y in route)
base=np.zeros((H,W,3),np.uint8);base[floor]=[7,12,20];base[furn]=[40,49,59]
baseedge=valid&~binary_erosion(valid,iterations=2);base[baseedge]=[21,37,52]
def find_label(z):
    p=wp(*z['preferred']);text=z['label'];ff=font(9,True);w=ff.getlength(text)+12;hh=25
    allowed=floor&z['mask'];best=None
    for yy in range(max(15,int(p[1]*2)-90),min(H-15,int(p[1]*2)+90),4):
        for xx in range(max(50,int(p[0]*2)-110),min(W-50,int(p[0]*2)+110),4):
            x0=int(xx-w/2);x1=int(xx+w/2)+1;y0=yy-hh//2;y1=yy+hh//2+1
            if x0<0 or x1>W or not allowed[y0:y1,x0:x1].all():continue
            score=(xx-p[0]*2)**2+(yy-p[1]*2)**2
            if best is None or score<best[0]:best=(score,(xx/2,yy/2))
    return best[1] if best else None
labelpos={k:find_label(v) for k,v in zones.items() if k!='gym'}
cards=[]
for i,c in enumerate(chapters):
    arr=base.copy()
    for key in c['zones']:
        z=zones[key];col=np.array(z['color']);zm=z['mask'];arr[zm&floor]=(col*.22).astype(np.uint8);arr[zm&furn]=(col*.7+35).clip(0,255).astype(np.uint8);arr[z['edge']]=(col*.82).astype(np.uint8)
    im=Image.fromarray(arr);dr=ImageDraw.Draw(im)
    # The clear gym floor acts as the caption area; no extra baseboard is needed.
    rect(dr,[367,94,665,361],(5,12,23))
    txt(dr,(516,116),'KING SCHOOL  /  CAMPUS CENTER',10,(158,189,205),True)
    dr.line([(389*Q,140*Q),(643*Q,140*Q)],fill=tuple(c['color']),width=Q)
    txt(dr,(516,159),f'{i+1:02d} / 06   {c["name"].upper()}',9,c['color'],True)
    for j,line in enumerate(c['title']):txt(dr,(516,201+j*31),line,24,(235,243,248),True)
    for j,line in enumerate(c['body']):txt(dr,(516,288+j*20),line,10.5,(177,199,213))
    for key in c['zones']:
        if key in labelpos and labelpos[key]:txt(dr,labelpos[key],zones[key]['label'],9,zones[key]['color'],True)
    # A small entry marker anchors every chapter to the same physical entrance.
    ex,ey=start;dr.ellipse([(ex-3)*Q,(ey-3)*Q,(ex+3)*Q,(ey+3)*Q],fill=(241,245,247))
    arr=np.array(im);arr[~valid]=0;cards.append(arr)
    Image.fromarray(arr).save(OUT/f'Chapter_{i+1:02d}.png')
    print('CHAPTER',i+1,c['name'],len(routes[i]),flush=True)
# 25 mm geometric checker, including furniture tops, plus alignment crosses.
yy,xx=np.indices((H,W));px=(xx+.5)*790.426/W+384.5-790.426/2;py=289+790.426*H/W/2-(yy+.5)*790.426/W
checker=(((np.floor(px/25)+np.floor(py/25)).astype(int)%2)*115+90).astype(np.uint8)
cal=np.repeat(checker[:,:,None],3,axis=2);cal[~valid]=0;Image.fromarray(cal).save(OUT/'Calibration_25mm.png')
Image.fromarray(cards[0]).save(OUT/'Information_Overview.png')
furniturecard=base.copy();furniturecard[furn]=[130,220,244];furniturecard[~valid]=0;Image.fromarray(furniturecard).save(OUT/'Furniture_Only.png')
FF='T:/AI/ffmpeg/bin/ffmpeg.exe';master=OUT/'Campus_Center_Information_Master_RGB.mp4';preview=OUT/'Campus_Center_Information_Preview.mp4';native=OUT/'Campus_Center_Information_1024x786_RGB.mp4'
def encoder(path,w,h,rgb=True):
    return subprocess.Popen([FF,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264rgb' if rgb else 'libx264','-crf','0' if rgb else '18','-preset','fast','-pix_fmt','rgb24' if rgb else 'yuv420p','-movflags','+faststart',str(path)],stdin=subprocess.PIPE)
enc=encoder(master,W,H);smallenc=encoder(native,1024,786);smallmask=valid.reshape(786,2,1024,2).all(axis=(1,3));hashes=[];smallhashes=[]
for f in range(duration*FPS):
    t=f/FPS;i=max(j for j,c in enumerate(chapters) if t>=c['start']);c=chapters[i];local=t-c['start'];fade=min(1,local/.65,(c['duration']-local)/.65);fade=max(0,fade)
    arr=cards[i];im=Image.fromarray(arr.copy());dr=ImageDraw.Draw(im);route=routes[i];col=tuple(c['color'])
    # A restrained moving pulse follows a geometrically checked corridor route.
    progress=min(1,max(0,(local-.65)/max(1,c['duration']-1.3)));k=round(progress*(len(route)-1))
    trail=route[max(0,k-42):k+1]
    if len(trail)>1:dr.line([(x*Q,y*Q) for x,y in trail],fill=col,width=3*Q,joint='curve')
    x,y=route[k];dr.ellipse([(x-2)*Q,(y-2)*Q,(x+2)*Q,(y+2)*Q],fill=(235,246,251))
    # Progress ticks stay on the caption floor, outside architectural surfaces.
    for j in range(6):dr.line([((467+j*18)*Q,341*Q),((477+j*18)*Q,341*Q)],fill=col if j<=i else (33,48,64),width=2*Q)
    arr=np.array(im);arr[~valid]=0
    if f==duration*FPS-1:fade=0  # Identical first/last frames for the loop seam.
    if fade<1:arr=(base.astype(np.float32)*(1-fade)+arr.astype(np.float32)*fade).astype(np.uint8)
    arr[~valid]=0;assert arr[~valid].max()==0
    hashes.append(hashlib.sha256(arr.tobytes()).hexdigest());enc.stdin.write(arr.tobytes())
    small=np.array(Image.fromarray(arr).resize((1024,786),Image.Resampling.LANCZOS));small[~smallmask]=0
    smallhashes.append(hashlib.sha256(small.tobytes()).hexdigest());smallenc.stdin.write(small.tobytes())
    if f%120==0:print('VIDEO_FRAME',f,flush=True)
enc.stdin.close();smallenc.stdin.close();assert enc.wait()==0 and smallenc.wait()==0
subprocess.run([FF,'-hide_banner','-loglevel','error','-y','-i',str(master),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(preview)],check=True)
description={'title':'Campus Center: one connected ground floor','duration_seconds':duration,'fps':FPS,'resolution':[W,H],'native_resolution':[1024,786],'chapters':chapters,'route_start_native_px':start,'routes_native_px':routes,'label_positions_native_px':labelpos,'reference_observations':[{'url':'https://www.youtube.com/watch?v=0vH0pd6N7oc&t=220s','reviewed':'Browser video views around 3:41, 3:51 and 3:56','takeaway':'Dark model, selected bright architectural edges and localized color reveal; the physical miniature carries the form.'},{'url':'https://www.youtube.com/shorts/4ZzGP8LLHxA','reviewed':'Chrome playback','takeaway':'Tightly registered imagery changes the appearance of a real miniature while its surrounding surface remains largely untouched.'}],'creative_application':'Room-by-room highlights, restrained route pulses, readable functional captions, and independent furniture-top masks. No moving sun or crowd footage.','wall_tops_black':True,'extra_caption_board':False,'all_routes_inside_walkable_floor':True,'narration_status':'Text draft only; video is silent','calibration':'Direct overhead assumption; hardware alignment remains required'}
(OUT/'show_plan.json').write_text(json.dumps(description,indent=2));(OUT/'render_hashes.json').write_text(json.dumps({'master':hashes,'native':smallhashes},indent=2));Image.fromarray(np.uint8(smallmask)*255).save(OUT/'Native_Validity.png')
print('INFORMATION_COMPLETE',duration,FPS,duration*FPS,flush=True)
