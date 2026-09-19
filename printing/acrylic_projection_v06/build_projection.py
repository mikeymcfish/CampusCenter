from pathlib import Path
import sys,json,math,hashlib,heapq
R=Path(__file__).parent;ROOT=R.parent;sys.path.insert(0,str(ROOT/'projection_furnished_v04/python_packages'))
import numpy as np
import trimesh
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_erosion,binary_dilation,distance_transform_edt,gaussian_filter,label
O=R/'projection';A=O/'assets';A.mkdir(parents=True,exist_ok=True)
previous_map=json.loads((R/'projection/map.json').read_text())
W,H=1024,786;rooms=json.loads((R/'rooms/room_contract.json').read_text());data=json.loads((ROOT/'output_3d_v4/model_geometry.json').read_text())
def wp(x,y):return (W/2+((x+47)/.0875-398)*W/830,H/2-((y+2.3)/.0875-289)*W/830)
def loadmask(n):return np.array(Image.open(R/'print'/n).convert('L')).reshape(H,2,W,2).min(axis=(1,3))>250
valid=loadmask('receiver_mask.png');valid=binary_erosion(valid,iterations=1);floor=loadmask('floor_mask.png')&valid;furn=loadmask('furniture_mask.png')&valid
mesh=trimesh.load(R/'print/Campus_Center_Ground_Acrylic_1_87p5.stl',force='mesh');height=np.full((H,W),-1,np.float32);normal=np.zeros((H,W,3),np.float32)
for tri,n in zip(mesh.triangles,mesh.face_normals):
 if n[2]<=.001:continue
 pts=np.column_stack([W/2+(tri[:,0]-398)*W/830,H/2-(tri[:,1]-289)*W/830]);x0=max(0,int(np.floor(pts[:,0].min())));x1=min(W,int(np.ceil(pts[:,0].max()))+1);y0=max(0,int(np.floor(pts[:,1].min())));y1=min(H,int(np.ceil(pts[:,1].max()))+1)
 if x1<=x0 or y1<=y0:continue
 yy,xx=np.mgrid[y0:y1,x0:x1];xx=xx+.5;yy=yy+.5;(ax,ay),(bx,by),(cx,cy)=pts;den=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
 if abs(den)<1e-8:continue
 u=((by-cy)*(xx-cx)+(cx-bx)*(yy-cy))/den;v=((cy-ay)*(xx-cx)+(ax-cx)*(yy-cy))/den;w=1-u-v;z=u*tri[0,2]+v*tri[1,2]+w*tri[2,2];inside=(u>=-1e-6)&(v>=-1e-6)&(w>=-1e-6)&(z>height[y0:y1,x0:x1]);height[y0:y1,x0:x1][inside]=z[inside];normal[y0:y1,x0:x1][inside]=n
assert (height[valid]>=0).all()
dist=distance_transform_edt(valid);edge=valid&~binary_erosion(valid,iterations=2);fedge=furn&~binary_erosion(furn,iterations=1)
np.savez_compressed(A/'surface_data.npz',height_mm=height,normal=normal,valid=valid,floor=floor,furniture=furn,edge=edge,distance_px=dist)
Image.fromarray(np.uint8(valid)*255).save(A/'receiver.png');Image.fromarray(np.uint8(furn)*255).save(A/'furniture.png');Image.fromarray(np.uint8(np.clip(height/55,0,1)*255)).save(A/'height.png');Image.fromarray(np.uint8((normal*.5+.5)*255)).save(A/'normal.png')
idsfull=np.load(R/'rooms/room_id_map.npz')['room_ids'];ids=idsfull[1::2,1::2];idimg=np.uint8(ids+1);Image.fromarray(idimg).save(A/'room_ids.png')
# Logical navigation uses open architectural doorways, not the closed door-light plinths of the print.
slab=Image.new('L',(W,H));bar=Image.new('L',(W,H));ds=ImageDraw.Draw(slab);db=ImageDraw.Draw(bar)
for p in data['parts']:
 if 'poly' not in p:continue
 pts=[wp(x/1000,y/1000) for x,y in p['poly']]
 if p['name'] in ['A101_ground_slab','Gym_slab']:ds.polygon(pts,fill=255)
 if p.get('group') in ['GROUND','GYM'] and p['kind'] in ['wall','glass'] and p.get('z',0)<1300 and 'leaf' not in p['name']:db.polygon(pts,fill=255)
walk=(np.array(slab)>0)&(np.array(bar)==0)&~binary_dilation(furn,iterations=1);walk=binary_erosion(walk,iterations=1)
def near(point,allowed):
 yy,xx=np.where(allowed);k=np.argmin((xx-point[0])**2+(yy-point[1])**2);return (int(xx[k]),int(yy[k]))
start=near(wp(17.8,12),walk);components,count=label(walk);reachable=components==components[start[1],start[0]]
navreport=[]
for i,r in enumerate(rooms):
 candidates=(ids==i)&walk;reachable_candidates=candidates&reachable
 navreport.append({'room':r['number'],'walkable_pixels':int(candidates.sum()),'reachable_pixels':int(reachable_candidates.sum())})
 if reachable_candidates.any():r['visit_xy']=list(near(wp(r['center_mm'][0]/1000,r['center_mm'][1]/1000),reachable_candidates))
 else:r['visit_xy']=None
 r['index']=i+1;r['image']='../rooms/'+r['number']+'/Room_3D.png'
Image.fromarray(np.uint8(walk)*255).save(A/'walkable.png')
np.savez_compressed(A/'navigation.npz',walkable=walk,reachable=reachable,room_ids=ids)
(O/'navigation_validation.json').write_text(json.dumps({'start':start,'rooms':navreport,'reachable_count':sum(r['reachable_pixels']>0 for r in navreport),'room_count':len(rooms),'door_policy':'Logical open architectural portals; avatar is blacked out over printed door plinths. No teleporting through walls.'},indent=2))
# Geometry-derived ink interpretation: irregular grid, hatched edge bands and furniture contours.
yy,xx=np.indices((H,W));rng=np.random.default_rng(615);paper=np.zeros((H,W,3),np.uint8);noise=gaussian_filter(rng.normal(0,1,(H,W)),.6)
for k,c in enumerate([227,219,194]):paper[:,:,k]=np.clip(c+noise*3,0,255)
paper[~valid]=0
ink=Image.fromarray(paper);dr=ImageDraw.Draw(ink)
for x in range(0,W,19):
 pts=[(x+1.1*math.sin(y*.071+x*.1),y) for y in range(0,H,6)];dr.line(pts,fill=(170,163,143),width=1)
for y in range(0,H,19):
 pts=[(x,y+math.sin(x*.057+y*.2)) for x in range(0,W,6)];dr.line(pts,fill=(170,163,143),width=1)
arr=np.array(ink);arr[edge]=[48,45,40];arr[furn]=np.clip(arr[furn]*.86,0,255);arr[fedge]=[43,41,37]
band=valid&(dist>2)&(dist<7)&(((xx+yy)//3)%2==0);arr[band]=[95,89,76];arr[~valid]=0
ink=Image.fromarray(arr);dr=ImageDraw.Draw(ink);font=ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf',11)
for r in rooms:
 if r['number']=='GYM':continue
 m=ids==r['index']-1
 if m.sum()<60:continue
 p=near(wp(r['center_mm'][0]/1000,r['center_mm'][1]/1000),m&valid if (m&valid).any() else m);dr.text(p,r['number'],font=font,fill=(44,40,35),stroke_width=2,stroke_fill=(227,219,194),anchor='mm')
titlefont=ImageFont.truetype('C:/Windows/Fonts/segoepr.ttf',25);dr.text(wp(-13,35),'Campus Center',font=titlefont,fill=(42,40,35),anchor='mm');dr.text(wp(-13,33),'GROUND FLOOR  /  EXPLORE & DISCOVER',font=font,fill=(62,55,42),anchor='mm')
# North arrow and 25 mm physical scale inside the gym's receiving floor.
gx,gy=wp(-13,26);dr.line([(gx,gy),(gx,gy-35)],fill=(45,41,33),width=2);dr.polygon([(gx,gy-39),(gx-5,gy-28),(gx+5,gy-28)],fill=(45,41,33));dr.text((gx,gy-49),'N',font=font,fill=(45,41,33),anchor='mm')
arr=np.array(ink);arr[~valid]=0;Image.fromarray(arr).save(A/'Ink_Map.png')
base=np.zeros((H,W,3),np.uint8);base[floor]=[10,23,32];base[furn]=[52,81,94];base[edge]=[67,111,128];base[fedge]=[107,156,167];Image.fromarray(base).save(A/'Explorer_Base.png')
# 25 mm grid in physical model coordinates, axis-coloured target with exact receiver blackout.
px=398+(xx+.5-W/2)*830/W;py=289+(H/2-yy-.5)*830/W;checker=(np.floor(px/25)+np.floor(py/25)).astype(int)%2
cal=np.zeros_like(base);cal[floor]=np.where(checker[floor,None]==0,[50,60,74],[95,110,125]);cal[furn]=[238,177,75];grid=(np.mod(px,25)<.9)|(np.mod(py,25)<.9);cal[grid&valid]=[160,220,245];cal[edge]=[100,240,170]
im=Image.fromarray(cal);dr=ImageDraw.Draw(im);marks=[]
for i,pt in enumerate([(-43,38),(-43,8),(-22,44),(-3,44),(-22,19),(-3,19),(3,27),(14,27),(-9,2),(-2,2),(15,3),(18,12)]):
 x,y=near(wp(*pt),floor);dr.line([(x-8,y),(x+8,y)],fill='white',width=1);dr.line([(x,y-8),(x,y+8)],fill='white',width=1);dr.ellipse((x-4,y-4,x+4,y+4),outline=(255,90,140),width=1);dr.text((x+10,y-6),str(i+1),font=font,fill='white');marks.append({'id':i+1,'canvas_xy':[x,y],'model_xy_mm':[398+(x-W/2)*830/W,289+(H/2-y)*830/W]})
dr.text(wp(-13,36),'ALIGNMENT  /  25 mm GRID',font=ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf',19),fill='white',anchor='mm');dr.text(wp(-13,34),'Green edges / amber furniture / black walls',font=font,fill='white',anchor='mm')
arr=np.array(im);arr[~valid]=0;Image.fromarray(arr).save(A/'Alignment_25mm.png')
(O/'calibration_points.json').write_text(json.dumps(marks,indent=2))
contract={'width':W,'height':H,'physical_canvas_mm':[830,637.08984375],'center_mm':[398,289],'start':list(start),'rooms':rooms,'gym_panel':[347,112,315,245],'speed_px_per_second':20,'model_source_sha256':hashlib.sha256((R/'print/Campus_Center_Ground_Acrylic_1_87p5.stl').read_bytes()).hexdigest()}
for r in rooms:
 old=next(q for q in previous_map['rooms'] if q['number']==r['number'])
 for key in ['image','image_caption','image_is_room_specific']:r[key]=old[key]
contract['speed_px_per_second']=previous_map['speed_px_per_second'];contract['revision']='r08 open patio and no gym bleachers'
(O/'map.json').write_text(json.dumps(contract,indent=2));print('PROJECTION_ASSETS',len(rooms),'reachable',sum(r['reachable_pixels']>0 for r in navreport),'height range',float(height[valid].min()),float(height[valid].max()),flush=True)
