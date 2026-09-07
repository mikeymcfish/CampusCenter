from pathlib import Path
import sys,json,shutil
R=Path(__file__).parent;sys.path.insert(0,str(R/'tmp/laserpackages'))
from shapely.geometry import Polygon
import ezdxf
O=R/'output_v13_laser';d=json.loads((O/'parts_manifest.json').read_text());SW,SH=d['config']['sheet_mm'];layers={'CUT':[],'LABELS':[]};xoff=8
for p in [p for p in d['parts'] if p['kind']=='COUPON']:
 g=Polygon(p['outline'][0],p['outline'][1:]);b=g.bounds;tx=lambda q:(q[0]-b[0]+xoff,q[1]-b[1]+8)
 layers['CUT'] += [[tx(q) for q in r] for r in p['outline']];layers['LABELS'] += [[tx(q) for q in l] for l in p['labels']];xoff+=b[2]-b[0]+10
doc=ezdxf.new('R2010');doc.units=4;doc.header['$INSUNITS']=4;ms=doc.modelspace();svg=[f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="{SW}mm" height="{SH}mm" viewBox="0 0 {SW} {SH}">']
for layer in ['CUT','ENGRAVE','LABELS']:
 doc.layers.new(layer,dxfattribs={'color':{'CUT':1,'ENGRAVE':5,'LABELS':8}[layer]});svg.append(f'<g id="{layer}" inkscape:groupmode="layer" inkscape:label="{layer}" fill="none" stroke="'+{'CUT':'#ff0000','ENGRAVE':'#0000ff','LABELS':'#777777'}[layer]+'" stroke-width="0.06">')
 for line in layers.get(layer,[]):
  closed=layer=='CUT';ms.add_lwpolyline(line[:-1] if closed else line,close=closed,dxfattribs={'layer':layer});path='M '+' L '.join(f'{x:.4f},{SH-y:.4f}' for x,y in line)+(' Z' if closed else '');svg.append(f'<path d="{path}"/>')
 svg.append('</g>')
svg.append('</svg>');(O/'Test_Fit_Coupon.svg').write_text('\n'.join(svg));doc.saveas(O/'Test_Fit_Coupon.dxf')
src=O/'editable_source';src.mkdir(exist_ok=True)
for fn in ['build_laser_v13.py','create_laser_guide_v13.py','audit_laser_v13.py','finish_laser_v13.py']:shutil.copy2(R/fn,src/fn)
for folder,fn in [('output_3d_v4','model_geometry.json'),('output_v10_stack_print','validation.json')]:
 (src/folder).mkdir(exist_ok=True);shutil.copy2(R/folder/fn,src/folder/fn)
(src/'output_v13_laser').mkdir(exist_ok=True);shutil.copy2(O/'config.json',src/'output_v13_laser/config.json')
for fn in ['assembled_preview.png','exploded_preview.png','ground_preview.png','upper_preview.png']:shutil.copy2(O/fn,src/'output_v13_laser'/fn)
(src/'requirements.txt').write_text('numpy\nshapely>=2.1\nezdxf\nreportlab\n')
print('COUPON_AND_SOURCE_READY')
