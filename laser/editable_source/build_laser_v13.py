"""Parametric 1:200 slotted plywood architectural kit; units mm."""
from pathlib import Path
import sys,json,math,re,hashlib
R=Path(__file__).parent;sys.path.insert(0,str(R/'tmp/laserpackages'))
import numpy as np
from shapely.geometry import Polygon,box,LineString,Point
from shapely.ops import unary_union
from shapely import affinity,make_valid
import ezdxf
O=R/'output_v13_laser';O.mkdir(exist_ok=True)
S=200.;T=3.175;K=.15;FIT=.05;SW=609.6;SH=304.8;M=8.;GAP=3.;DZ=4267.2/S
config={'scale_denominator':S,'stock_thickness_mm':T,'assumed_kerf_mm':K,'joint_clearance_mm':FIT,'sheet_mm':[SW,SH],'edge_margin_mm':M,'part_gap_mm':GAP}
if (O/'config.json').exists():
 config.update(json.loads((O/'config.json').read_text()));T=config['stock_thickness_mm'];K=config['assumed_kerf_mm'];FIT=config['joint_clearance_mm'];S=config['scale_denominator'];DZ=4267.2/S
(O/'config.json').write_text(json.dumps(config,indent=2))
d=json.loads((R/'output_3d_v4/model_geometry.json').read_text());parts=[];notes=[]
def poly(p):return Polygon([(x/S,y/S) for x,y in p['poly']]).buffer(0)
def clean(g):
 g=make_valid(g)
 if g.geom_type=='GeometryCollection':g=unary_union([a for a in g.geoms if a.geom_type in ['Polygon','MultiPolygon']])
 return g.buffer(0)
def paths(g):
 gs=list(g.geoms) if g.geom_type=='MultiPolygon' else [g]
 return [list(r.coords) for p in gs for r in [p.exterior,*p.interiors]]
def add(name,kind,floor,geom,placement=None,engrave=None,label=None,meta=None):
 geom=clean(geom);assert geom.geom_type=='Polygon',(name,geom.geom_type)
 p={'id':len(parts)+1,'name':name,'kind':kind,'floor':floor,'geom':geom,'placement':placement,'engrave':engrave or [],'label':label,'meta':meta or {}};parts.append(p);return p
floor_shapes={}
for f,z in [('GROUND',0),('UPPER',4267.2)]:
 ps=[poly(p) for p in d['parts'] if p['kind'] in ['slab','terrace'] and abs(p['z']+p['height']-z)<1]
 floor_shapes[f]=unary_union(ps)
for v in d.get('slab_voids',[]):floor_shapes['UPPER']=floor_shapes['UPPER'].difference(Polygon([(x/S,y/S) for x,y in v['poly']]))
# The actual gym has no intermediate floor; its tall walls stay with the lower unit.
for f in ['GROUND','UPPER']:add(f+' floor plate','FLOOR',f,floor_shapes[f],{'type':'floor','z':0 if f=='GROUND' else DZ})
raw=[]
for floor,z0 in [('GROUND',0),('UPPER',4267.2)]:
 for p in d['parts']:
  if p['kind'] not in ['wall','glass'] or 'poly' not in p or 'height' not in p:continue
  if p['group'] not in ['GROUND','UPPER','GYM']:continue
  if floor=='GROUND' and p['group']=='UPPER':continue
  if floor=='UPPER' and p['group']=='GYM':continue
  if any(s in p['name'].lower() for s in ['guard','handrail','patio_','leaf','parapet']):continue
  lo=p['z'];hi=lo+p['height']
  if hi<=z0+1 or lo>=z0+4400:continue
  b=poly(p).bounds;dx=b[2]-b[0];dy=b[3]-b[1]
  if min(dx,dy)>max(dx,dy)*.4 and max(dx,dy)<4:continue
  axis='H' if dx>=dy else 'V';c=(b[1]+b[3])/2 if axis=='H' else (b[0]+b[2])/2;a,bv=(b[0],b[2]) if axis=='H' else (b[1],b[3])
  if bv-a<.6:continue
  raw.append({'floor':floor,'axis':axis,'c':c,'a':a,'b':bv,'source':p,'hi':hi})
# Consolidate coincident wall faces before imposing the thicker plywood material.
clusters=[]
for r in sorted(raw,key=lambda x:x['b']-x['a'],reverse=True):
 matches=[c for c in clusters if c['floor']==r['floor'] and c['axis']==r['axis'] and (abs(c['c']-r['c'])<.05 or (abs(c['c']-r['c'])<T*.75 and any(min(v['b'],r['b'])-max(v['a'],r['a'])>0 for v in c['rows'])))]
 match=matches[0] if matches else None
 if match:match['rows'].append(r)
 else:clusters.append({'floor':r['floor'],'axis':r['axis'],'c':r['c'],'rows':[r]})
runs=[]
for c in clusters:
 rows=sorted(c['rows'],key=lambda r:r['a']);groups=[]
 for r in rows:
  if groups and r['a']<=max(v['b'] for v in groups[-1])+.65:groups[-1].append(r)
  else:groups.append([r])
 for rs in groups:runs.append({**c,'rows':rs,'a':min(r['a'] for r in rs),'b':max(r['b'] for r in rs)})
# Horizontal panels are continuous. Vertical panels butt against their faces.
segments=[]
for r in runs:
 intervals=[(r['a'],r['b'])]
 if r['axis']=='V':
  for h in runs:
   if h['floor']!=r['floor'] or h['axis']!='H' or not h['a']-T/2<=r['c']<=h['b']+T/2:continue
   cut0=h['c']-T/2-FIT;cut1=h['c']+T/2+FIT;new=[]
   for a,b in intervals:
    if cut1<=a or cut0>=b:new.append((a,b))
    else:
     if cut0-a>=2:new.append((a,cut0))
     if b-cut1>=2:new.append((cut1,b))
   intervals=new
 for a,b in intervals:
  if b-a>=3:segments.append({**r,'a':a,'b':b})
# The full-height gym panels replace coincident upper panels and receive butt ends.
gyms=[r for r in runs if r['floor']=='GROUND' and any(v['source']['group']=='GYM' for v in r['rows'])]
adjusted=[]
for r in segments:
 intervals=[(r['a'],r['b'])]
 if r['floor']=='UPPER':
  for gym in gyms:
   cuts=[]
   if gym['axis']==r['axis'] and abs(gym['c']-r['c'])<T:cuts=[(gym['a']-.05,gym['b']+.05)]
   elif gym['axis']!=r['axis'] and gym['a']-T/2<=r['c']<=gym['b']+T/2:cuts=[(gym['c']-T/2-FIT,gym['c']+T/2+FIT)]
   for lo,hi in cuts:
    new=[]
    for a,b in intervals:
     if hi<=a or lo>=b:new.append((a,b))
     else:
      if lo-a>=3:new.append((a,lo))
      if b-hi>=3:new.append((hi,b))
    intervals=new
 for a,b in intervals:adjusted.append({**r,'a':a,'b':b})
segments=adjusted
slots={'GROUND':[],'UPPER':[]};footprints={'GROUND':[],'UPPER':[]}
def local_rect_world(axis,c,a,rect):
 x0,y0,x1,y1=rect
 return box(a+x0,c+y0,a+x1,c+y1) if axis=='H' else box(c+y0,a+x0,c+y1,a+x1)
def wall_tabs(g,L,axis,c,a,floor):
 width=min(6.,max(1.8,L-1.6));candidates=np.linspace(width/2+.4,L-width/2-.4,max(5,int(L/2))) if L>width+.8 else [L/2]
 good=[float(x) for x in candidates if g.covers(box(x-width/2,.02,x+width/2,1.5))]
 if not good:
  width=1.2;candidates=np.linspace(.65,L-.65,max(20,int(L*5)));good=[float(x) for x in candidates if g.covers(box(x-width/2,.02,x+width/2,1.2))]
 assert good,('No tab landing',L)
 centers=[good[0]]
 if good[-1]-good[0]>width+3:centers.append(good[-1])
 if L>90:
  mid=min(good,key=lambda x:abs(x-L/2))
  if all(abs(mid-x)>width+3 for x in centers):centers.append(mid)
 for x in centers:
  g=g.union(box(x-width/2,-T,x+width/2,.2));sl=local_rect_world(axis,c,a,(x-(width+FIT)/2,-(T+FIT)/2,x+(width+FIT)/2,(T+FIT)/2));slots[floor].append({'geom':sl,'part':len(parts)+1,'width':width,'center':x})
 return clean(g),centers,width
for r in sorted(segments,key=lambda x:(x['floor'],x['axis'],x['c'],x['a'])):
 f=r['floor'];a,b,c=r['a'],r['b'],r['c'];L=b-a;axis=r['axis'];z0=0 if f=='GROUND' else 4267.2
 isgym=any(v['source']['group']=='GYM' for v in r['rows'])
 H=(8687./S if isgym else DZ-T) if f=='GROUND' else (8661.4-4267.2)/S
 g=box(0,0,L,H);engr=[];openings=[]
 for row in r['rows']:
  p=row['source']
  if p['kind']!='glass':continue
  x0=max(1.6,row['a']-a+.6);x1=min(L-1.6,row['b']-a-.6);y0=max(1.8,(p['z']-z0)/S);y1=min(H-1.8,(p['z']+p['height']-z0)/S)
  if x1-x0<1.4 or y1-y0<1.4:continue
  n=max(1,math.ceil((x1-x0)/12));w=((x1-x0)-(n-1)*1.3)/n
  for i in range(n):openings.append(box(x0+i*(w+1.3),y0,x0+i*(w+1.3)+w,y1))
 for door in d['doors']:
  if door['floor']!=f:continue
  ox,oy=[v/S for v in door['origin_mm']];direction=door['opening_direction'];da='H' if abs(direction[0])>.9 else 'V' if abs(direction[1])>.9 else None
  if da!=axis or abs((oy if axis=='H' else ox)-c)>T*.8:continue
  start=ox if axis=='H' else oy;end=start+door['opening_width_mm']/S*(direction[0] if axis=='H' else direction[1]);x0=max(1.6,min(start,end)-a);x1=min(L-1.6,max(start,end)-a);y1=min(H-2,door['opening_height_mm']/S)
  if x1-x0>2.2 and y1>3:openings.append(box(x0,-.1,x1,y1))
 if openings:g=clean(g.difference(unary_union(openings)))
 if g.geom_type!='Polygon':raise ValueError('Disconnected wall '+str(r))
 g,centers,tabw=wall_tabs(g,L,axis,c,a,f)
 placement={'type':'wall','axis':axis,'a':a,'c':c,'z':T+(0 if f=='GROUND' else DZ)}
 fp=local_rect_world(axis,c,a,(0,-T/2,L,T/2));footprints[f].append(fp)
 add(r['rows'][0]['source']['name'].split('_wall')[0]+' panel','WALL',f,g,placement,engr,label=(centers[0],-T/2) if tabw>=4 else (L/2,H-.9),meta={'axis':axis,'a':a,'b':b,'c':c,'body_height':H,'tabs':centers,'tab_width':tabw,'window_door_cutouts':len(openings),'source_names':sorted(set(v['source']['name'] for v in r['rows'])),'gym_full_height':isgym})
# Stair flights and landings are aligned laminations of side profiles.
stair_groups={}
for p in d['parts']:
 if p['kind']!='stair' or 'poly' not in p or p.get('z',0)+p.get('height',0)<=0:continue
 n=p['name'];key=None
 if '_tread_' in n:key=n.split('_tread_')[0]
 elif re.match(r'Stair_B_(lower|upper)_\d+$',n):key=re.sub(r'_\d+$','',n)
 elif 'landing' in n.lower() and not any(s in n.lower() for s in ['rail','post']):key=n
 if key:stair_groups.setdefault(key,[]).append(p)
stair_footprints=[];stair_sets=[]
for name,rs in sorted(stair_groups.items()):
 footprint=unary_union([poly(p) for p in rs]);x0,y0,x1,y1=footprint.bounds;axis='H' if x1-x0>=y1-y0 else 'V';a=x0 if axis=='H' else y0;c=(y0+y1)/2 if axis=='H' else (x0+x1)/2;L=(x1-x0) if axis=='H' else (y1-y0);W=(y1-y0) if axis=='H' else (x1-x0)
 profiles=[]
 for p in rs:
  b=poly(p).bounds;lo=b[0] if axis=='H' else b[1];hi=b[2] if axis=='H' else b[3];ht=(p['z']+p['height'])/S
  # Where the stair enters the upper plate, the plate supplies the final tread.
  rect=local_rect_world(axis,c,a,(lo-a,-W/2,hi-a,W/2))
  if floor_shapes['UPPER'].intersects(rect):ht=min(ht,DZ-T)
  profiles.append(box(lo-a,0,hi-a,ht))
 g=clean(unary_union(profiles));layers=max(2,math.floor(W/T));layers=min(6,layers);ids=[]
 if g.geom_type!='Polygon':continue
 center_index=layers//2
 for j in range(layers):
  shift=(j-(layers-1)/2)*T;gj=g;label=(L*.6,min(g.bounds[3]*.5,5))
  if j==center_index:
   gj,centers,tabw=wall_tabs(g,L,axis,c+shift,a,'GROUND');label=(centers[0],-T/2)
  # Etched registration lines align the laminations without separate pins.
  engr=[[(L*.25,1),(L*.25,min(4,g.bounds[3]-.3))],[(L*.75,1),(L*.75,min(4,g.bounds[3]-.3))]]
  p=add(name+f' lamination {j+1}/{layers}','STAIR','GROUND',gj,{'type':'wall','axis':axis,'a':a,'c':c+shift,'z':T},engr,label,{'stair_set':name,'lamination':j+1,'count':layers,'body_height':g.bounds[3]});ids.append(p['id'])
 stair_sets.append({'name':name,'pieces':ids,'layers':layers,'assembled_width_mm':layers*T,'plan_width_mm':W});stair_footprints.append(footprint)
# Lower plate follows the stair runs too. Narrow source landing paths join exterior flights.
floor_shapes['GROUND']=unary_union([floor_shapes['GROUND'],*stair_footprints])
old=json.loads((R/'output_v10_stack_print/validation.json').read_text())
for tie in old['stair_abutments']:
 line=LineString([((x*350-47000)/S,(y*350-2300)/S) for x,y in tie['path_xy_mm']]);floor_shapes['GROUND']=floor_shapes['GROUND'].union(line.buffer(2.5,cap_style=3))
for f in ['GROUND','UPPER']:
 # Local edge allowance provides wood around the slots, rather than a rectangular plinth.
 outline=unary_union([floor_shapes[f],*[g.buffer(2,join_style=2) for g in footprints[f]],*[s['geom'].buffer(2,join_style=2) for s in slots[f]]]).buffer(0)
 if f=='UPPER':
  gym_clear=[]
  for p in parts:
   if p['kind']=='WALL' and p['meta'].get('gym_full_height'):
    pl=p['placement'];gym_clear.append(local_rect_world(pl['axis'],pl['c'],pl['a'],(0,-T/2-FIT,p['meta']['b']-pl['a'],T/2+FIT)))
  outline=outline.difference(unary_union(gym_clear))
  for p in parts:
   if p['kind']!='STAIR':continue
   pl=p['placement'];g=p['geom'];bb=g.bounds;section=g.intersection(box(bb[0]-1,DZ-T+.001,bb[2]+1,DZ+.01))
   gs=list(section.geoms) if hasattr(section,'geoms') else [section]
   for q in gs:
    if q.is_empty or q.area<.001:continue
    lo,_,hi,_=q.bounds;outline=outline.difference(local_rect_world(pl['axis'],pl['c'],pl['a'],(lo-FIT,-T/2-FIT,hi+FIT,T/2+FIT)))
 outline=clean(outline)
 if outline.geom_type!='Polygon':raise ValueError('Disconnected floor '+f+str([(g.area,g.bounds) for g in outline.geoms]))
 floor=parts[0 if f=='GROUND' else 1];floor['geom']=clean(outline.difference(unary_union([s['geom'] for s in slots[f]])));floor['meta']['slots']=[{'part':s['part'],'bounds':s['geom'].bounds} for s in slots[f]]
 floor['label']=(floor['geom'].representative_point().x,floor['geom'].representative_point().y)
 for p in parts:
  if p['floor']==f and p['kind']=='WALL':
   pl=p['placement'];L=p['meta']['b']-pl['a'];floor['engrave'].append([(pl['a'],pl['c']),(pl['a']+L,pl['c'])] if pl['axis']=='H' else [(pl['c'],pl['a']),(pl['c'],pl['a']+L)])
# Calibration coupon: no assumed kerf compensation on its trial openings.
coupon=box(0,0,115,35);trial=[]
for i,width in enumerate([2.90,2.95,3.,3.025,3.05,3.075,3.10,3.125,3.15,3.175,3.20,3.25]):
 x=5+i*9;coupon=coupon.difference(box(x-width/2,15,x+width/2,35.1));trial.append({'index':i+1,'raw_cut_slot_width_mm':width,'center_x':x})
cp=add('Fit coupon - uncorrected trial slots','COUPON','TEST',coupon,None,label=(57,5),meta={'trial_slots':trial,'no_kerf_compensation':True})
add('Fit coupon insert tongue','COUPON','TEST',box(0,0,10,25),None,label=(5,5),meta={'no_kerf_compensation':True})
# Thin single-stroke vector numerals. No font objects or raster labels.
segs={'a':[(0,1),(1,1)],'b':[(1,1),(1,.5)],'c':[(1,.5),(1,0)],'d':[(0,0),(1,0)],'e':[(0,.5),(0,0)],'f':[(0,1),(0,.5)],'g':[(0,.5),(1,.5)]};digits=['ab cdef'.replace(' ',''),'bc','abged','abgcd','fgbc','afgcd','afgecd','abc','abcdefg','abfgcd']
def number_lines(number,x,y,height=2):
 s=str(number);w=height*.55;total=len(s)*w+(len(s)-1)*height*.2;out=[]
 for i,ch in enumerate(s):
  for seg in digits[int(ch)]:out.append([(x-total/2+i*(w+height*.2)+px*w,y-height/2+py*height) for px,py in segs[seg]])
 return out
for p in parts:
 if p['label'] is None:rp=p['geom'].representative_point();p['label']=(rp.x,rp.y)
 p['labels']=number_lines(p['id'],*p['label'],height=1.6 if p['kind'] in ['WALL','STAIR'] else 3)
 if p['kind'] in ['WALL','STAIR'] and not all(p['geom'].buffer(.02).covers(LineString(l)) for l in p['labels']):
  bb=p['geom'].bounds;options=[]
  for yy in np.arange(bb[1]+.9,bb[3]-.8,.5):
   for xx in np.arange(bb[0]+1.8,bb[2]-1.7,.5):
    if p['geom'].covers(box(xx-1.75,yy-.85,xx+1.75,yy+.85)):options.append(((xx-p['label'][0])**2+(yy-p['label'][1])**2,xx,yy))
  assert options,('No label area',p['id'])
  _,xx,yy=min(options);p['label']=(float(xx),float(yy));p['labels']=number_lines(p['id'],xx,yy,1.6)
 if p['kind']=='FLOOR':
  seen=set();occupied=[]
  for s in slots[p['floor']]:
   if s['part'] in seen:continue
   seen.add(s['part']);rp=s['geom'].centroid
   for dx,dy in [(3,3),(-3,3),(3,-3),(-3,-3),(6,0),(-6,0),(0,6),(0,-6)]:
    bb=box(rp.x+dx-2.2,rp.y+dy-1,rp.x+dx+2.2,rp.y+dy+1)
    if p['geom'].covers(bb) and not any(bb.intersects(o) for o in occupied):p['labels']+=number_lines(s['part'],rp.x+dx,rp.y+dy,1.7);occupied.append(bb);break
 if p is cp:
  for tr in trial:p['labels']+=number_lines(tr['index'],tr['center_x'],10,1.5)
# Deterministic rectangle nesting, deliberately avoiding inside-hole nesting.
sheets=[]
for p in sorted(parts,key=lambda p:p['geom'].envelope.area,reverse=True):
 g=p['geom'];b=g.bounds;w=b[2]-b[0]+K;hh=b[3]-b[1]+K;choices=[]
 for si,sh in enumerate(sheets):
  for fi,(x,y,rw,rh) in enumerate(sh['free']):
   for rot,(pw,ph) in [(False,(w,hh)),(True,(hh,w))]:
    if pw+GAP<=rw and ph+GAP<=rh:choices.append((rw*rh-pw*ph,si,fi,rot,pw,ph))
 if not choices:
  sheets.append({'free':[(M,M,SW-2*M,SH-2*M)],'parts':[]});si=len(sheets)-1
  for rot,(pw,ph) in [(False,(w,hh)),(True,(hh,w))]:
   if pw+GAP<=SW-2*M and ph+GAP<=SH-2*M:choices.append((0,si,0,rot,pw,ph))
  assert choices,('Oversize part',p['id'],w,hh)
 _,si,fi,rot,pw,ph=min(choices);sh=sheets[si];x,y,rw,rh=sh['free'].pop(fi);sh['free'] +=[(x+pw+GAP,y,rw-pw-GAP,ph+GAP),(x,y+ph+GAP,rw,rh-ph-GAP)];sh['free']=[r for r in sh['free'] if r[2]>2 and r[3]>2];sh['parts'].append(p['id'])
 p['nest']={'sheet':si+1,'x':x+K/2,'y':y+K/2,'rot90':rot,'local_min':[b[0],b[1]],'local_height':b[3]-b[1]}
def tx(p,pt):
 n=p['nest'];x=pt[0]-n['local_min'][0];y=pt[1]-n['local_min'][1]
 if n['rot90']:x,y=n['local_height']-y,x
 return x+n['x'],y+n['y']
def svg_path(pts,closed=False):return 'M '+' L '.join(f'{x:.4f},{SH-y:.4f}' for x,y in pts)+(' Z' if closed else '')
for si,sh in enumerate(sheets,1):
 layers={'CUT':[],'ENGRAVE':[],'LABELS':[]};nominal=[]
 for id in sh['parts']:
  p=parts[id-1];g=p['geom'] if p['meta'].get('no_kerf_compensation') else p['geom'].buffer(K/2,join_style=2)
  assert g.geom_type=='Polygon' and g.is_valid
  layers['CUT'] += [[tx(p,v) for v in ring] for ring in paths(g)]
  for line in p['engrave']:
   clipped=p['geom'].intersection(LineString(line));items=[clipped] if clipped.geom_type=='LineString' else list(clipped.geoms) if hasattr(clipped,'geoms') else []
   layers['ENGRAVE'] += [[tx(p,v) for v in seg.coords] for seg in items if seg.geom_type=='LineString' and seg.length>.3]
  layers['LABELS'] += [[tx(p,v) for v in line] for line in p['labels']]
  ng=Polygon([tx(p,v) for v in p['geom'].exterior.coords]);nominal.append((p['id'],ng))
 for i,(pid,g) in enumerate(nominal):
  assert box(M-.1,M-.1,SW-M+.1,SH-M+.1).covers(g)
  for qid,q in nominal[:i]:assert g.distance(q)>=GAP-.2,(pid,qid)
 doc=ezdxf.new('R2010');doc.units=4;doc.header['$INSUNITS']=4;ms=doc.modelspace();colors={'CUT':1,'ENGRAVE':5,'LABELS':8}
 svg=[f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="{SW}mm" height="{SH}mm" viewBox="0 0 {SW} {SH}">']
 for layer,lines in layers.items():
  doc.layers.new(layer,dxfattribs={'color':colors[layer]});svg.append(f'<g id="{layer}" inkscape:groupmode="layer" inkscape:label="{layer}" fill="none" stroke="'+{'CUT':'#ff0000','ENGRAVE':'#0000ff','LABELS':'#777777'}[layer]+'" stroke-width="0.06">')
  for pts in lines:
   closed=layer=='CUT';ms.add_lwpolyline(pts[:-1] if closed else pts,close=closed,dxfattribs={'layer':layer});svg.append(f'<path d="{svg_path(pts,closed)}"/>')
  svg.append('</g>')
 svg.append('</svg>');(O/f'Sheet_{si:02d}_12x24.svg').write_text('\n'.join(svg));doc.saveas(O/f'Sheet_{si:02d}_12x24.dxf')
serial=[]
for p in parts:
 serial.append({k:v for k,v in p.items() if k not in ['geom'] }|{'outline':paths(p['geom']),'area_mm2':p['geom'].area})
(O/'parts_manifest.json').write_text(json.dumps({'config':config,'source':'output_3d_v4/model_geometry.json','parts':serial,'sheets':[{'sheet':i+1,'parts':s['parts']} for i,s in enumerate(sheets)],'stairs':stair_sets,'notes':notes},indent=2))
print('LASER_KIT_BUILT',len(parts),'parts',len(sheets),'sheets',flush=True)
