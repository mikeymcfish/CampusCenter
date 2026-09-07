from pathlib import Path
import sys,json,math,csv
R=Path(__file__).parent;sys.path.insert(0,str(R/'tmp/laserpackages'))
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3,landscape
from reportlab.lib.colors import HexColor,Color,white
from reportlab.lib.utils import ImageReader
from shapely.geometry import Polygon,box,LineString
O=R/'output_v13_laser';d=json.loads((O/'parts_manifest.json').read_text());parts=d['parts'];T=d['config']['stock_thickness_mm'];PW,PH=landscape(A3);M=40
C=canvas.Canvas(str(O/'Campus_Center_Laser_Assembly_Guide.pdf'),pagesize=(PW,PH));C.setTitle('Campus Center - 1/8 inch plywood assembly guide');page=0
INK=HexColor('#183443');ACC=HexColor('#ad6d24');MUT=HexColor('#51636d');LIGHT=HexColor('#e9edf0')
def text(x,y,s,size=11,color=INK,font='Helvetica'):
 C.setFillColor(color);C.setFont(font,size);C.drawString(x,y,str(s))
def wrap(s,width,size=11):
 out=[];line=''
 for word in str(s).split():
  test=(line+' '+word).strip()
  if C.stringWidth(test,'Helvetica',size)>width and line:out.append(line);line=word
  else:line=test
 if line:out.append(line)
 return out
def para(x,y,s,width,size=11,leading=16):
 for line in wrap(s,width,size):text(x,y,line,size);y-=leading
 return y-8
def new(title,sub=''):
 global page
 if page:C.showPage()
 page+=1;C.setFillColor(INK);C.rect(0,PH-87,PW,87,fill=1,stroke=0);text(M,PH-39,title,24,white,'Helvetica-Bold');text(M,PH-65,sub,10,HexColor('#d1dce2'));text(M,22,'CAMPUS CENTER | 1:200 | 3.175 mm PLYWOOD | LASER KIT v13',8,MUT);text(PW-80,22,f'{page:02d}',9,MUT)
def poly_draw(rings,transform,fill=None,stroke=INK,lw=.6):
 p=C.beginPath()
 for ring in rings:
  pts=[transform(x,y) for x,y in ring];p.moveTo(*pts[0])
  for pt in pts[1:]:p.lineTo(*pt)
  p.close()
 C.setLineWidth(lw);C.setStrokeColor(stroke)
 if fill:C.setFillColor(fill)
 C.drawPath(p,stroke=1,fill=bool(fill),fillMode=0)
def pic(name,x,y,w,h):
 C.drawImage(str(O/name),x,y,width=w,height=h,preserveAspectRatio=True,anchor='c',mask='auto')
def floor_map(floor,bounds,rect,labels=True):
 x,y,w,h=rect;x0,y0,x1,y1=bounds;s=min(w/(x1-x0),h/(y1-y0));ox=x+(w-(x1-x0)*s)/2;oy=y+(h-(y1-y0)*s)/2;tf=lambda a,b:(ox+(a-x0)*s,oy+(b-y0)*s)
 C.saveState();path=C.beginPath();path.rect(x,y,w,h);C.clipPath(path,stroke=0)
 fp=parts[0 if floor=='GROUND' else 1];poly_draw(fp['outline'],tf,HexColor('#f5f2eb'),MUT,.4)
 for p in parts:
  if p['floor']!=floor or p['kind'] not in ['WALL','STAIR']:continue
  pl=p['placement'];a=pl['a'];c=pl['c'];bb=Polygon(p['outline'][0],p['outline'][1:]).bounds;L0,L1=bb[0],bb[2]
  ring=[(a+L0,c-T/2),(a+L1,c-T/2),(a+L1,c+T/2),(a+L0,c+T/2)] if pl['axis']=='H' else [(c-T/2,a+L0),(c+T/2,a+L0),(c+T/2,a+L1),(c-T/2,a+L1)]
  poly_draw([ring],tf,HexColor('#ccb28c') if p['kind']=='WALL' else HexColor('#8ba7b7'),MUT,.35)
  if labels:
   xx,yy=(a+(L0+L1)/2,c) if pl['axis']=='H' else (c,a+(L0+L1)/2)
   if x0<=xx<=x1 and y0<=yy<=y1:
    tx,ty=tf(xx,yy);C.saveState();C.translate(tx,ty);C.rotate(0 if pl['axis']=='H' else 90);label=str(p['id']);fs=7 if s>3 else 6;tw=C.stringWidth(label,'Helvetica-Bold',fs);C.setFillColor(white);C.rect(-tw/2-1,-fs*.4,tw+2,fs+1,fill=1,stroke=0);C.setFont('Helvetica-Bold',fs);C.setFillColor(INK);C.drawCentredString(0,-fs*.2,label);C.restoreState()
 C.restoreState();return tf
def sheet_map(si,rect):
 x,y,w,h=rect;sw,sh=d['config']['sheet_mm'];s=min(w/sw,h/sh);tf=lambda a,b:(x+a*s,y+b*s);C.setFillColor(HexColor('#fcfaf5'));C.setStrokeColor(MUT);C.rect(x,y,sw*s,sh*s,fill=1,stroke=1)
 for p in parts:
  if p['nest']['sheet']!=si:continue
  n=p['nest']
  def pos(a,b):
   a-=n['local_min'][0];b-=n['local_min'][1]
   if n['rot90']:a,b=n['local_height']-b,a
   return tf(a+n['x'],b+n['y'])
  poly_draw(p['outline'],pos,None,HexColor('#b43d37'),.35)
  C.setStrokeColor(MUT);C.setLineWidth(.25)
  for line in p['labels']:
   a,b=map(lambda v:pos(*v),line);C.line(*a,*b)
def part_profile(p,rect):
 x,y,w,h=rect;g=Polygon(p['outline'][0],p['outline'][1:]);x0,y0,x1,y1=g.bounds;s=min(w/(x1-x0),h/(y1-y0));tf=lambda a,b:(x+(a-x0)*s,y+(b-y0)*s);poly_draw(p['outline'],tf,HexColor('#e4c89e'),INK,.7)

new('Campus Center - buildable plywood kit','Two floors, walls and stairs | No roof | 12 x 24 inch sheets')
pic('assembled_preview.png',40,150,810,590)
y=PH-130
for title,body in [('2 sheets','Each sheet is 609.6 x 304.8 mm. Cut files use millimetres and already include the stated kerf allowance.'),('157 numbered parts','Two floor plates, 131 wall panels, 22 stair laminations and two coupon parts. Numbers on cut pieces and in this guide are the same.'),('Slot-and-tab assembly','Walls and stair cores locate in floor slots. Use wood glue on these joints and on the wall butt joints.'),('Test before cutting','Run the small coupon first. Stock thickness and kerf vary; this kit has not been physically cut or assembled.')]:
 text(880,y,title,16,ACC,'Helvetica-Bold');y=para(880,y-22,body,265,11)-25
para(45,113,'Build the ground unit and upper unit separately. The upper plate rests on the lower walls; the gym walls remain full height on the ground unit. This is a laser-cut adaptation of the floor-plan model, with practical plywood wall thickness and simplified stair widths.',1090,12)

new('01  Material, fit coupon and laser layers','Complete the fit check before committing either sheet')
y=PH-125
for s in ['Material: 1/8 inch plywood, nominal 3.175 mm. Measure the actual stock before cutting.','Design: 1:200. Nominal kerf compensation is 0.15 mm, with 0.05 mm assembly clearance. Do not apply a second kerf offset in the laser software.','Sequence: engrave ENGRAVE and optional LABELS first, then cut internal openings, then outer contours. CUT is red; ENGRAVE is blue; LABELS is gray.','LABELS contains only thin vector strokes, not text objects or images. Hide or disable that entire layer to omit the numbers. Keep the numbered guide available if you do.']:
 y=para(45,y,s,1090,12,18)
cp=next(p for p in parts if p['name'].startswith('Fit coupon -'));part_profile(cp,(55,350,570,150));text(55,330,f"Coupon part {cp['id']}; insert tongue {cp['id']+1}",12,ACC,'Helvetica-Bold')
text(690,495,'Coupon slots (raw cut-path widths)',13,INK,'Helvetica-Bold')
for i,tr in enumerate(cp['meta']['trial_slots']):
 col=i//6;row=i%6;text(695+col*210,470-row*22,f"{tr['index']:02d}     {tr['raw_cut_slot_width_mm']:.3f} mm",11)
y=290
for s in ['Cut Test_Fit_Coupon.svg or select only the coupon and tongue from sheet 2. Insert the plywood edge of the tongue into each numbered slot. Choose a fit that seats fully with light hand pressure. Do not force a narrow slot.','Slot 6 (3.075 mm cut path) corresponds to the supplied compensation: 3.175 + 0.05 - 0.15 = 3.075 mm. If slot 6 is suitable, use the supplied sheets unchanged.','If another slot is better, revise the kerf setting and regenerate first: assumed kerf = measured stock thickness + desired clearance - preferred raw slot width. The editable config and generator are included. This is a starting calibration; confirm with another coupon.']:
 y=para(45,y,s,1090,12,18)

new('02  How the joints work','Dry-fit first; glue after confirming the panel position and direction')
# Large schematic cross section, deliberately separate from cut-ready geometry.
C.setFillColor(HexColor('#dfbf8f'));C.setStrokeColor(INK);C.rect(100,420,460,55,fill=1);C.setFillColor(white);C.rect(300,420,60,55,fill=1);C.setFillColor(HexColor('#bd8c4f'));C.rect(300,505,60,160,fill=1);C.setFillColor(HexColor('#dfbf8f'));C.rect(200,560,260,105,fill=1)
text(610,640,'Wall body',16,ACC,'Helvetica-Bold');para(610,616,'The body stands above the floor. The bottom tab passes through the matching slot; its end finishes flush with the floor underside.',490,12)
text(610,535,'Floor slot',16,ACC,'Helvetica-Bold');para(610,511,'The slot width matches the stock thickness plus fit clearance. Its length matches the tab width plus clearance. Both are kerf-compensated in the supplied sheet files.',490,12)
text(610,430,'Wall intersections',16,ACC,'Helvetica-Bold');para(610,406,'Horizontal plan panels remain continuous. Vertical plan panels butt against their faces. Floor slots locate the joint; apply a small bead of wood glue along the butt seam. There are no interlocking wall-edge fingers to force.',490,12)
para(55,295,'Assembly habits: keep the numbered face oriented as shown on the maps, test the adjacent panels before glue sets, check walls for square, and support delicate window mullions while handling. Narrow tabs belong to narrow wall piers; they are locating features rather than force-fit fasteners.',1080,12)
para(55,208,'Geometry adaptations: wall centerlines are consolidated to suit 3.175 mm stock; some fine partitions and frame widths are therefore thicker than scale. Window openings retain solid webs and headers. Floor edges have local material around slots, rather than an added rectangular plinth. The stair side profiles reproduce the rise and run with a practical laminated width.',1080,12)

for floor,title,range_ids in [('GROUND','03  Ground floor',[]),('UPPER','04  Upper floor',[])]:
 fp=parts[0 if floor=='GROUND' else 1];g=Polygon(fp['outline'][0],fp['outline'][1:]);b=g.bounds
 new(title+' - orientation',f"Floor plate {fp['id']:03d} | Numbers identify wall and stair parts")
 floor_map(floor,(b[0]-3,b[1]-3,b[2]+3,b[3]+3),(45,80,850,640))
 y=700;group=[p for p in parts if p['floor']==floor and p['kind']=='WALL']
 steps=['Lay the floor plate numbered face upward. Sort the wall panels by their IDs.','Fit the long horizontal-map walls first. Add the vertical-map partitions, butting them to the continuous panels.','Use the four detail maps that follow to locate every wall. The parts list gives the sheet and dimensions.']
 if floor=='GROUND':steps+=['Install the full-height gym walls as part of this lower unit. Their height is intentional.','Fit the stair assemblies after the surrounding walls are located; see the stair pages.']
 else:steps+=['Build this unit on a flat surface separately from the lower unit. Bottom tabs finish flush.','The gym is open at this level. Its full-height walls belong to the ground unit; do not add duplicate upper walls.']
 for i,s in enumerate(steps,1):text(925,y,str(i),15,ACC,'Helvetica-Bold');y=para(947,y,s,200,11,16)-15
 # Four large, legible part-location maps.
 midx=(b[0]+b[2])/2;midy=(b[1]+b[3])/2
 for zone,(x0,y0,x1,y1) in [('NW',(b[0]-2,midy-4,midx+4,b[3]+2)),('NE',(midx-4,midy-4,b[2]+2,b[3]+2)),('SW',(b[0]-2,b[1]-2,midx+4,midy+4)),('SE',(midx-4,b[1]-2,b[2]+2,midy+4))]:
  new(title+f' - {zone} detail','Locate the panel by number; tabs enter the matching numbered floor slots')
  floor_map(floor,(x0,y0,x1,y1),(45,95,900,625));ids=[]
  for p in group:
   pl=p['placement'];m=p['meta'];xx,yy=((m['a']+m['b'])/2,m['c']) if m['axis']=='H' else (m['c'],(m['a']+m['b'])/2)
   if x0<=xx<=x1 and y0<=yy<=y1:ids.append(p['id'])
  text(980,690,'Panels in this view',12,ACC,'Helvetica-Bold');para(980,662,', '.join(map(str,ids)),160,12,19);text(45,65,'Tan = wall footprints   Blue = stair laminations   White openings = cutouts / slots',10,MUT)

for start in [0,6]:
 new('05  Stairs - laminate, then locate','Match the stepped profiles, glue flat face to flat face, then insert the core tab')
 sets=d['stairs'][start:start+6]
 for j,st in enumerate(sets):
  col=j%2;row=j//2;x=50+col*560;y=PH-135-row*220;p=parts[st['pieces'][-1]-1]
  text(x,y,st['name'].replace('_',' '),14,ACC,'Helvetica-Bold');text(x,y-22,'Pieces '+', '.join(map(str,st['pieces'])),12)
  part_profile(p,(x,y-155,290,105));para(x+315,y-50,f"Glue {st['layers']} layers to make a {st['assembled_width_mm']:.2f} mm wide stair. Align the bottom edge and the etched registration marks. The tabbed layer locates the unit in the ground plate.",210,10,14)
 if start==6:para(50,90,'The upper floor provides the final arrival surface where a stair meets its opening. Minor profile trimming and floor clearance are intentional. Exterior stairs stay connected to the lower floor through narrow floor extensions following their landing paths.',1080,11)

new('06  Bring the two floors together','Keep the upper floor removable unless you specifically want a permanently glued model')
pic('exploded_preview.png',45,85,800,640)
y=690
for title,body in [('1  Confirm the lower unit','Let the ground walls and stair laminations dry square. Check that tabs are seated fully and that the top wall edges are even.'),('2  Lower the upper unit','Align the gym edge and the stair openings. Lower the upper floor vertically onto the ground wall tops. The full-height gym walls pass beside it.'),('3  Check the stair arrivals','The upper plate must not bear on a misplaced stair. Recheck the matching stair IDs and the laminated width if it does not sit flat.'),('4  Finish','Keep the upper floor unglued for access to both layouts. No roof parts are included.')]:
 text(880,y,title,15,ACC,'Helvetica-Bold');y=para(880,y-24,body,260,11,16)-25

for sh in d['sheets']:
 new(f"07  Sheet {sh['sheet']:02d} - 12 x 24 inches",'Cut from the SVG or DXF at 1:1 millimetres, not from this reduced guide drawing')
 sheet_map(sh['sheet'],(45,180,PW-90,550));para(45,120,'The sheet files include only the part geometry: there is no cutting rectangle around the sheet boundary. Keep the three layers separate. The gray number strokes can be hidden; they are not cut contours.',1090,11)
 text(45,77,f"{len(sh['parts'])} pieces on this sheet. Minimum sheet-edge margin: 8 mm. Nominal spacing between packed parts: 3 mm.",11)

for start in range(0,len(parts),34):
 new('08  Parts list',f'Part numbers {start+1:03d}-{min(start+34,len(parts)):03d} | Dimensions include tabs')
 cols=[45,100,160,255,395,1120];y=PH-115
 for x,s in zip(cols,['ID','Sheet','Type / floor','Size (mm)','Part / source description']):text(x,y,s,10,ACC,'Helvetica-Bold')
 y-=25
 for p in parts[start:start+34]:
  g=Polygon(p['outline'][0],p['outline'][1:]);b=g.bounds
  if p['id']%2==0:C.setFillColor(HexColor('#f2f4f5'));C.rect(40,y-5,PW-80,18,fill=1,stroke=0)
  row=[f"{p['id']:03d}",str(p['nest']['sheet']),p['kind']+' / '+p['floor'][0],f'{b[2]-b[0]:.2f} x {b[3]-b[1]:.2f}',p['name']]
  for x,s in zip(cols,row):text(x,y,s,9)
  y-=18

new('09  Verification and fabrication notes','Digitally checked; the coupon is still required for your stock and laser')
y=PH-130
for title,body in [('Checked','Both sheet files were reopened as DXF, checked for millimetre units, separate CUT / ENGRAVE / LABELS layers, and vector-only numeric labels. Parts are nested within the sheet margins without overlaps. Actual part polygons were extruded into the assembly preview.'),('Joint and assembly checks','The floor slots and tab cross sections were checked for solid clashes. Wall-to-wall intersections were checked after consolidating the full-height gym walls and upper partitions. The digital checks do not replace a physical test cut.'),('Material allowances','The supplied files assume 3.175 mm stock, 0.15 mm kerf, and 0.05 mm clearance. The coupon slot widths are intentionally uncompensated. Other cut contours include compensation. Fit changes with actual plywood thickness, glue, charring and machine settings.'),('Source fidelity','The source is the existing architectural floor-plan model derived from the supplied King School PDFs. This kit prioritizes room relationships, floor outlines, stairs and major openings. Laser-cut thickness, broadened window webs, merged wall faces and laminated stair widths are fabrication adaptations.'),('Files','Use Sheet_01_12x24.svg / .dxf and Sheet_02_12x24.svg / .dxf. Test_Fit_Coupon.svg / .dxf isolates the coupon. LABELS is optional. parts_manifest.json and parts_list.csv contain the piece register. The Blender assembly is a visual reference, not a laser toolpath.'),('Scope','Two floors, walls and stairs only. No roof, furniture or loose glazing is included. Original Blender, STEP and earlier print files were preserved.')]:
 text(50,y,title,15,ACC,'Helvetica-Bold');y=para(50,y-24,body,1080,12,18)-15
C.save()
with (O/'parts_list.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['ID','Sheet','Kind','Floor','Name','Width_mm','Height_mm'])
 for p in parts:
  b=Polygon(p['outline'][0],p['outline'][1:]).bounds;w.writerow([p['id'],p['nest']['sheet'],p['kind'],p['floor'],p['name'],round(b[2]-b[0],3),round(b[3]-b[1],3)])
print('ASSEMBLY_GUIDE',page,'pages',flush=True)
