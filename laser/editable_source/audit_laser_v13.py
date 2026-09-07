from pathlib import Path
import sys,json
R=Path(__file__).parent;sys.path.insert(0,str(R/'tmp/laserpackages'))
from shapely.geometry import Polygon,box,LineString
import ezdxf
O=R/'output_v13_laser';d=json.loads((O/'parts_manifest.json').read_text());T=d['config']['stock_thickness_mm'];parts=d['parts'];errors=[];collisions=[]
def shape(p):return Polygon(p['outline'][0],p['outline'][1:])
def bounds(p):
 pl=p['placement'];g=shape(p);x0,y0,x1,y1=g.bounds
 if pl['type']=='floor':return (x0,y0,pl['z'],x1,y1,pl['z']+T)
 if pl['axis']=='H':return (pl['a']+x0,pl['c']-T/2,pl['z']+y0,pl['a']+x1,pl['c']+T/2,pl['z']+y1)
 return (pl['c']-T/2,pl['a']+x0,pl['z']+y0,pl['c']+T/2,pl['a']+x1,pl['z']+y1)
walls=[p for p in parts if p['kind']=='WALL']
for i,p in enumerate(walls):
 a=bounds(p)
 for q in walls[:i]:
  b=bounds(q);over=[min(a[j+3],b[j+3])-max(a[j],b[j]) for j in range(3)]
  if min(over)>.08:collisions.append({'a':p['id'],'b':q['id'],'overlap_mm':over})
floor_clashes=[]
for floor in [p for p in parts if p['kind']=='FLOOR']:
 fg=shape(floor);zm=floor['placement']['z']+T/2
 for p in parts:
  if p['kind'] not in ['WALL','STAIR']:continue
  pl=p['placement'];g=shape(p);v=zm-pl['z'];x0,y0,x1,y1=g.bounds
  if not y0<v<y1:continue
  section=g.intersection(LineString([(x0-1,v),(x1+1,v)]));lines=[section] if section.geom_type=='LineString' else list(section.geoms) if hasattr(section,'geoms') else []
  for line in lines:
   if line.geom_type!='LineString':continue
   lo,_,hi,_=line.bounds
   footprint=box(pl['a']+lo,pl['c']-T/2,pl['a']+hi,pl['c']+T/2) if pl['axis']=='H' else box(pl['c']-T/2,pl['a']+lo,pl['c']+T/2,pl['a']+hi)
   area=fg.intersection(footprint).area
   if area>.005:floor_clashes.append({'floor':floor['id'],'part':p['id'],'area_mm2':area})
for p in parts:
 g=shape(p)
 if not g.is_valid:errors.append('invalid '+str(p['id']))
for f in O.glob('Sheet_*.dxf'):
 doc=ezdxf.readfile(f);audit=doc.audit()
 if audit.errors:errors.append(str(f)+' DXF audit')
 assert doc.header['$INSUNITS']==4
 assert all(l in doc.layers for l in ['CUT','ENGRAVE','LABELS'])
 assert not list(doc.modelspace().query('TEXT MTEXT IMAGE'))
out={'parts':len(parts),'sheets':len(d['sheets']),'errors':errors,'wall_aabb_collisions':collisions,'floor_solid_clashes':floor_clashes,'all_number_labels_are_vector_lines':True,'units':'mm'};(O/'audit.json').write_text(json.dumps(out,indent=2));print('AUDIT',len(errors),'errors',len(collisions),'wall overlaps',len(floor_clashes),'floor clashes');print(collisions[:15],floor_clashes[:20])
