from pathlib import Path
import sys,json,heapq
R=Path(__file__).parent;ROOT=R.parent
sys.path.insert(0,str(ROOT/'projection_furnished_v04/python_packages'))
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import distance_transform_edt,binary_erosion,label
data=json.loads((ROOT/'output_3d_v4/model_geometry.json').read_text());W,H=2048,1572
def wp(x,y):return (W/2+((x+47)/.0875-398)*W/830,H/2-((y+2.3)/.0875-289)*W/830)
floor=Image.new('L',(W,H));barrier=Image.new('L',(W,H));df=ImageDraw.Draw(floor);db=ImageDraw.Draw(barrier)
for p in data['parts']:
 if 'poly' not in p:continue
 pts=[wp(x/1000,y/1000) for x,y in p['poly']]
 if p['name'] in ['A101_ground_slab','Gym_slab']:df.polygon(pts,fill=255)
 if p.get('group') not in ['GROUND','GYM']:continue
 if p['kind'] in ['wall','glass'] and (p.get('z',0)<2200) and ('leaf' not in p['name']):db.polygon(pts,fill=255)
# Open social spaces receive explicit program boundaries rather than imaginary walls.
db.line([wp(0,14.628),wp(16.437,14.628)],fill=255,width=2)
db.line([wp(0,14.628),wp(0,16.39)],fill=255,width=2)
db.line([wp(0,8.8),wp(12.25,8.8)],fill=255,width=2)
db.line([wp(12.1,14.63),wp(12.1,20.3),wp(16.44,20.3)],fill=255,width=2)
db.line([wp(11.969,4.787),wp(11.969,9.628),wp(16.56,9.628)],fill=255,width=2)
free=(np.array(floor)>0)&(np.array(barrier)==0)
rooms=[r for r in data['rooms'] if r['floor']=='GROUND']
near=distance_transform_edt(~free,return_distances=False,return_indices=True)
ids=np.full((H,W),-1,np.int16);cost=np.full((H,W),np.inf,np.float32);heap=[]
for i,r in enumerate(rooms):
 x,y=wp(r['center_mm'][0]/1000,r['center_mm'][1]/1000);x=int(x);y=int(y)
 if not free[y,x]:y,x=near[:,y,x]
 cost[y,x]=0;ids[y,x]=i;heapq.heappush(heap,(0,int(y),int(x),i))
while heap:
 dist,y,x,i=heapq.heappop(heap)
 if dist!=cost[y,x] or i!=ids[y,x]:continue
 for dy,dx in [(-1,0),(1,0),(0,-1),(0,1)]:
  yy=y+dy;xx=x+dx
  if 0<=yy<H and 0<=xx<W and free[yy,xx] and dist+1<cost[yy,xx]:
   cost[yy,xx]=dist+1;ids[yy,xx]=i;heapq.heappush(heap,(dist+1,yy,xx,i))
out=R/'rooms';out.mkdir(exist_ok=True);overview=np.zeros((H,W,3),np.uint8);rng=np.random.default_rng(6);contracts=[]
for i,r in enumerate(rooms):
 mask=ids==i;yy,xx=np.where(mask);assert len(xx)>20,r
 bounds=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
 d=out/r['number'];d.mkdir(exist_ok=True);Image.fromarray(np.uint8(mask)*255).save(d/'mask_full_canvas.png');overview[mask]=rng.integers(65,195,3)
 # Square orthographic room image, sharp from edge to edge, no perspective or DOF.
 x0,y0,x1,y1=bounds;side=max(x1-x0,y1-y0)+16;cx=(x0+x1)/2;cy=(y0+y1)/2
 worldcx=((cx-W/2)*830/W+398)*.0875-47;worldcy=((H/2-cy)*830/W+289)*.0875-2.3;span=side*830/W*.0875
 contracts.append(dict(r,mask_bounds_px=bounds,center_world_m=[worldcx,worldcy],ortho_span_m=span,output_resolution=[1024,1024],camera_z_m=3.5,mask_area_m2=float(mask.sum()*(830/W*.0875)**2)))
im=Image.fromarray(overview);draw=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf',17)
for r in rooms:draw.text(wp(r['center_mm'][0]/1000,r['center_mm'][1]/1000),r['number'],font=font,fill='white',stroke_width=1,stroke_fill='black',anchor='mm')
im.save(out/'Room_Mask_Review.png');(out/'room_contract.json').write_text(json.dumps(contracts,indent=2));np.savez_compressed(out/'room_id_map.npz',room_ids=ids,walkable=free)
print('ROOM_MASKS',len(rooms),[(r['number'],round(r['mask_area_m2'],1)) for r in contracts],flush=True)
