from pathlib import Path
import json,math,csv,collections
R=Path(__file__).resolve().parents[1];O=R/'lego';O.mkdir(parents=True,exist_ok=True)
geo=json.loads((R/'cad/structural_geometry.json').read_text());laser=json.loads((R/'laser/parts_manifest.json').read_text())
W,H=96,64;ox,oy=60,8
walls=set();axis={};glazing=set();doors=set();placements=[]
def xy(x,y):return round(x/1000+ox),round(y/1000+oy)
for p in laser['parts']:
 if p['kind']!='WALL' or p['floor']!='GROUND':continue
 a=p['meta'];hor=a['axis']=='H';lo=round(a['a']/5+(ox if hor else oy));hi=round(a['b']/5+(ox if hor else oy));c=round(a['c']/5+(oy if hor else ox))
 for t in range(lo,hi+1):
  q=(t,c) if hor else (c,t)
  if 0<=q[0]<W and 0<=q[1]<H:walls.add(q);axis[q]='H' if hor else 'V'
for p in geo['parts']:
 if p['kind']!='glass' or 'poly' not in p or p.get('z',5000)>=4000 or '_leaf' in p['name']:continue
 xs=[q[0] for q in p['poly']];ys=[q[1] for q in p['poly']];hor=max(xs)-min(xs)>max(ys)-min(ys)
 for q in walls:
  x=(q[0]-ox)*1000;y=(q[1]-oy)*1000
  if (min(xs)+250<x<max(xs)-250 and abs(y-sum(ys)/len(ys))<600) if hor else (min(ys)+250<y<max(ys)-250 and abs(x-sum(xs)/len(xs))<600):glazing.add(q)
doorinfo=[];reserved_headers=set()
for d in geo['doors']:
 if d.get('floor')!='GROUND':continue
 # This source uses plan opening polygons; use the hardware schedule for widths and axes below.
pass
schedule=json.loads((R/'cad/door_schedule.json').read_text())
for d in schedule:
 if d['floor']!='GROUND':continue
 u=d['opening_direction'];p=d['origin_mm'];center=(p[0]+u[0]*d['opening_width_mm']/2,p[1]+u[1]*d['opening_width_mm']/2);cx,cy=xy(*center);hor=abs(u[0])>.5
 candidates=sorted(walls,key=lambda q:(q[0]-cx)**2+(q[1]-cy)**2)
 if not candidates or math.dist(candidates[0],(cx,cy))>1.5:continue
 q=candidates[0];n=2 if d['opening_width_mm']>1550 else 1
 start=q[0] if hor else q[1];fixed=q[1] if hor else q[0]
 hole=[(start+i,fixed) if hor else (fixed,start+i) for i in range(n)]
 ends=[(start-1,fixed),(start+n,fixed)] if hor else [(fixed,start-1),(fixed,start+n)]
 # Preserve a visible jamb at each end; adjacent openings may share a jamb.
 if set(hole+ends)&reserved_headers:continue
 if any(q in doors for q in ends) or any(q in hole for old in doorinfo for q in old['ends']):continue
 for q in ends:walls.add(q);axis[q]='H' if hor else 'V'
 reserved_headers.update(hole+ends);doors.update(hole);walls.update(hole);doorinfo.append(dict(name=d['id'],hole=hole,ends=ends,hor=hor))
parts_by_length={1:'3005',2:'3004',3:'3622',4:'3010'}
def add(layer,x,y,w,d,color,part,role='wall'):
 placements.append(dict(id=len(placements)+1,layer=layer,x=x,y=y,w=w,d=d,color=color,part=part,role=role))
for by in range(2):
 for bx in range(3):add(0,bx*32,by*32,32,32,'Light bluish gray','3811','baseplate')
layers={}
for course in range(1,5):
 grid={q:('White' if q in glazing and course in (2,3) else 'Black') for q in walls if course>2 or q not in doors}
 # Glazing uses white bricks for simple availability and easy reading at this scale.
 if course==3:
  for d in doorinfo:
   cells=d['ends'][:1]+d['hole']+d['ends'][1:]
   if not all(q in grid for q in cells):continue
   xs=[q[0] for q in cells];ys=[q[1] for q in cells];w=max(xs)-min(xs)+1;dep=max(ys)-min(ys)+1
   add(course,min(xs),min(ys),w,dep,'Black',parts_by_length[max(w,dep)],'door lintel')
   for q in cells:grid.pop(q,None)
 remaining=dict(grid)
 while remaining:
  q=min(remaining,key=lambda q:(q[1],q[0]) if course%2 else (q[0],q[1]));color=remaining[q];options=[]
  for hor in [course%2==1,course%2!=1]:
   for n in [4,3,2,1]:
    cells=[(q[0]+i,q[1]) if hor else(q[0],q[1]+i) for i in range(n)]
    if all(remaining.get(c)==color for c in cells):
     # Course 3 requires attachment to a supported stud below, including lintels.
     support=sum(c in layers.get(course-1,{}) for c in cells) if course>1 else n
     if support:options.append((n,hor,cells))
  if not options:raise RuntimeError(('Unsupported brick',course,q))
  n,hor,cells=max(options,key=lambda o:o[0]);add(course,q[0],q[1],n if hor else 1,1 if hor else n,color,parts_by_length[n])
  for c in cells:remaining.pop(c)
 # Full occupancy comes from actual placed bricks, checking duplicates.
 occ={}
 for p in placements:
  if p['layer']!=course:continue
  for x in range(p['x'],p['x']+p['w']):
   for y in range(p['y'],p['y']+p['d']):
    assert (x,y) not in occ,('Overlap',course,x,y)
    occ[x,y]=p['color']
 layers[course]=occ
# Furniture uses simple standard 2x2 and 2x4 bricks, not bespoke shapes.
def furniture(name,x,y,w,d,h=1,color='Tan'):
 x,y=xy(x*1000,y*1000)
 cells={(a,b) for a in range(x,x+w) for b in range(y,y+d)}
 if cells&walls:return
 if any(cells&c for c in occupied_furn):return
 occupied_furn.append(cells)
 for layer in range(1,h+1):add(layer,x,y,w,d,color,'3003' if (w,d)==(2,2) else '3001',name)
occupied_furn=[]
for x,y in [(3,20),(10,20),(3,26),(10,26)]:furniture('commons seat',x,y,2,2,1,'Dark bluish gray')
for x,y in [(-8,2),(-8,6)]:furniture('iLab fabrication bench',x,y,2,4,1,'Tan')
for x,y in [(-3,2),(-3,6)]:furniture('iLab collaboration table',x,y,2,4,1,'Tan')
for x,y in [(-6,3),(-10,7)]:furniture('iLab equipment',x,y,2,2,2,'Dark bluish gray')
furniture('cafe counter',13,17,2,2,1,'Tan');furniture('reception',13,6,2,2,1,'Tan')
# Three solid brick steps show both stair cores in the open-top model.
for x,y in [(-29,9),(1,6)]:
 for j in range(3):furniture('stair step',x,y+j*2,2,2,j+1,'Light bluish gray')
# Every non-base brick must engage at least one stud below; stairs and equipment fully supported.
all_occ={0:{(x,y) for x in range(W) for y in range(H)}};overlap=[];unsupported=[]
for l in range(1,5):
 occ=set()
 for p in [p for p in placements if p['layer']==l]:
  cells={(x,y) for x in range(p['x'],p['x']+p['w']) for y in range(p['y'],p['y']+p['d'])}
  if occ&cells:overlap.append(p['id'])
  if not cells&all_occ[l-1]:unsupported.append(p['id'])
  occ|=cells
 all_occ[l]=occ
assert not overlap and not unsupported,(overlap,unsupported)
colors={'Black':0,'White':15,'Tan':19,'Light bluish gray':71,'Dark bluish gray':72}
ldr=['0 Campus Center ground floor - stud aligned study model','0 Author: Campus Center project','0 !LICENSE Redistributable project model; standard parts supplied by your LDraw library.','0 !CATEGORY Architecture']
for l in range(5):
 for p in [p for p in placements if p['layer']==l]:
  x=(p['x']+(p['w']-1)/2)*20;z=-(p['y']+(p['d']-1)/2)*20;y=-24*l
  # Standard rectangular part longest side runs along X; rotate for north-south pieces.
  rotation='1 0 0 0 1 0 0 0 1' if p['w']>=p['d'] else '0 0 1 0 1 0 -1 0 0'
  ldr.append(f"1 {colors[p['color']]} {x} {y} {z} {rotation} {p['part']}.dat")
 ldr.append('0 STEP')
(O/'Campus_Center_Ground_Floor.ldr').write_text('\n'.join(ldr))
with (O/'brick_placements.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(placements[0]));w.writeheader();w.writerows(placements)
counts=collections.Counter((p['part'],p['color'],p['w']*p['d']) for p in placements)
with (O/'parts_list.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['Part','Color','Quantity']);w.writerows((part,col,n) for (part,col,_),n in sorted(counts.items()))
data=dict(studs=[W,H],board_mm=[W*8,H*8],horizontal_scale=125,wall_courses=4,wall_height_mm=38.4,origin_world_m=[-ox,-oy],placements=placements,doors=doorinfo,rooms=[r for r in geo['rooms'] if r['floor']=='GROUND'],validation=dict(overlaps=overlap,unsupported=unsupported,parts=len(placements),physical_build_tested=False),sources=['https://www.ldraw.org/article/218.html','https://library.ldraw.org/library/official/parts/3004.dat','https://library.ldraw.org/library/official/parts/3811.dat'])
(O/'lego_model.json').write_text(json.dumps(data,indent=2));print('LEGO_MODEL',len(placements),'parts',len(doorinfo),'door openings',flush=True)
