from pathlib import Path
import json,csv,collections,textwrap
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3,landscape
from reportlab.lib.colors import HexColor,Color,black,white
R=Path(__file__).resolve().parents[1];O=R/'lego';d=json.loads((O/'lego_model.json').read_text());ps=d['placements'];W,H=landscape(A3)
c=canvas.Canvas(str(O/'Campus_Center_LEGO_Build_Guide.pdf'),pagesize=(W,H));c.setTitle('Campus Center ground floor - LEGO building guide');page=0
palette={'Black':HexColor('#282d33'),'White':HexColor('#f4f0df'),'Tan':HexColor('#c6a36c'),'Light bluish gray':HexColor('#c5cbd0'),'Dark bluish gray':HexColor('#737c83')}
def text(x,y,t,size=12,color=black):c.setFillColor(color);c.setFont('Helvetica',size);c.drawString(x,y,t)
def para(x,y,t,width=63,size=12):
 for line in textwrap.wrap(t,width):text(x,y,line,size);y-=size*1.4
 return y-12
def start(title,sub=''):
 global page
 if page:c.showPage()
 page+=1;c.setFillColor(HexColor('#183849'));c.rect(0,H-87,W,87,fill=1,stroke=0);text(35,H-40,title,25,white);text(35,H-65,sub,11,HexColor('#cbe0e9'));text(35,21,'CAMPUS CENTER  |  GROUND FLOOR  |  STUD-ALIGNED STUDY MODEL',9,HexColor('#5b6870'));text(W-65,21,str(page),10)
def plan(parts,x,y,scale,bounds=(0,0,96,64),showrooms=False,ghost=False):
 x0,y0,x1,y1=bounds
 c.setLineWidth(.2);c.setStrokeColor(HexColor('#d9dfe3'))
 for xx in range(x0,x1+1):c.line(x+(xx-x0)*scale,y,x+(xx-x0)*scale,y+(y1-y0)*scale)
 for yy in range(y0,y1+1):c.line(x,y+(yy-y0)*scale,x+(x1-x0)*scale,y+(yy-y0)*scale)
 for p in parts:
  if p['layer']==0:continue
  a=max(x0,p['x']);b=max(y0,p['y']);e=min(x1,p['x']+p['w']);f=min(y1,p['y']+p['d'])
  if e<=a or f<=b:continue
  c.setFillColor(palette[p['color']]);c.setStrokeColor(HexColor('#52616b'));c.setLineWidth(.55);c.rect(x+(a-x0)*scale+.12,y+(b-y0)*scale+.12,(e-a)*scale-.24,(f-b)*scale-.24,fill=1,stroke=1)
  c.setStrokeColor(HexColor('#8d969c') if p['color']=='Black' else HexColor('#899196'));c.setLineWidth(.28)
  for xx in range(a,e):
   for yy in range(b,f):c.circle(x+(xx-x0+.5)*scale,y+(yy-y0+.5)*scale,scale*.21,fill=0,stroke=1)
 c.setLineWidth(1.1);c.setStrokeColor(HexColor('#2a799c'))
 for xx in range(0,97,32):
  if x0<=xx<=x1:c.line(x+(xx-x0)*scale,y,x+(xx-x0)*scale,y+(y1-y0)*scale)
 for yy in range(0,65,32):
  if y0<=yy<=y1:c.line(x,y+(yy-y0)*scale,x+(x1-x0)*scale,y+(yy-y0)*scale)
 for xx in range(x0,x1,4):text(x+(xx-x0)*scale+1,y-13,str(xx),8)
 for yy in range(y0,y1,4):text(x-22,y+(yy-y0)*scale+1,str(yy),8)
 if showrooms:
  for r in d['rooms']:
   xx=r['center_mm'][0]/1000+60;yy=r['center_mm'][1]/1000+8
   if x0<=xx<x1 and y0<=yy<y1:
    c.setFont('Helvetica',6.4);c.setFillColor(HexColor('#243e4b'));c.drawCentredString(x+(xx-x0+.5)*scale,y+(yy-y0+.5)*scale,r['number'])
def legend(x,y):
 for name in ['Black','White','Tan','Dark bluish gray']:
  c.setFillColor(palette[name]);c.setStrokeColor(black);c.rect(x,y,13,13,fill=1);text(x+22,y+2,{'Black':'Walls / lintels','White':'Glazing representation','Tan':'Counters / tables','Dark bluish gray':'Seats / equipment'}[name],11);y-=24
start('Build the Campus Center','A practical ground-floor LEGO model from the architectural plan')
img=O/'LEGO_preview.png'
if img.exists():c.drawImage(str(img),30,120,width=790,height=527,preserveAspectRatio=True,anchor='c',mask='auto')
y=H-130
for t in ['662 pieces | 6 baseplates','96 x 64 studs','76.8 x 51.2 cm display footprint','Approximately 1:125 in plan','Four wall courses; open top','29 simplified door openings']:
 text(840,y,t,13);y-=32
para(840,y-8,'This is a buildable interpretation with standard bricks. Wall thickness, window bays and stairs are simplified to the stud grid.',37)
legend(840,260)
start('Before you build','Read this page, then use the baseplate maps for each wall course')
y=H-125
for head,body in [('1. Prepare a flat board','Arrange six 32 x 32 baseplates as three columns by two rows. The whole assembly is large: support all six on a flat board when moving it. Do not lift it by the building walls.'),('2. Follow the coordinates','The southwest corner is (0,0). X increases right; Y increases up on every plan. Coordinates refer to the southwest occupied stud of a brick. Baseplates A/B/C are the bottom row; D/E/F are the top row.'),('3. Build four wall courses','Start with course 1 on all six baseplates, then course 2, 3 and 4. Each outlined rectangle is one brick. Count studs to identify its length. The maps are top views, not full-size print templates.'),('4. Preserve door gaps','Leave the indicated gaps empty on courses 1 and 2. Course 3 bridges them with a single 1 x 3 or 1 x 4 lintel attached to both jambs. Course 4 caps the walls. Do not substitute loose 1 x 1 bricks over a doorway.'),('5. Add the interior blocks','The furniture pages give exact positions. Furniture uses common blocks and is schematic. White bricks represent glass; transparent alternatives are optional and are not assumed in the bill of materials.')]:
 text(40,y,head,16);y=para(40,y-25,body,133,12)-10
start('Baseplate layout and room key','Use the blue 32-stud boundaries to match the six detailed maps')
plan([p for p in ps if p['layer']==1 and p['role'] in ['wall','door lintel']],45,100,8.1,showrooms=True)
for j in range(2):
 for i in range(3):text(45+(i*32+1)*8.1,100+(j*32+30)*8.1,'ABCDEF'[j*3+i],18,HexColor('#287597'))
y=H-120
for r in d['rooms']:
 label=r['number']+'  '+r['name'].title()
 for line in textwrap.wrap(label,38):text(850,y,line,9);y-=12
 if y<75:break
start('Parts to gather','Counts match the complete digital model, including baseplates and interior blocks')
counts=collections.Counter((p['part'],p['color']) for p in ps);names={'3811':'Baseplate 32 x 32','3001':'Brick 2 x 4','3003':'Brick 2 x 2','3004':'Brick 1 x 2','3005':'Brick 1 x 1','3010':'Brick 1 x 4','3622':'Brick 1 x 3'}
y=H-130
for col,x in [('PART',45),('DESCRIPTION',150),('COLOR',430),('COUNT',670)]:text(x,y,col,12)
y-=28
for (part,color),n in sorted(counts.items()):
 text(45,y,part,12);text(150,y,names[part],12);text(430,y,color,12);text(670,y,str(n),12);y-=25
para(790,H-145,'Use the supplied parts_list.csv as the exact shopping or sorting list. Color is a suggested visual scheme, not a claim of current store stock.',42)
para(790,H-260,'The LDraw file uses these standard part identifiers. Open it in a compatible brick editor with an installed LDraw parts library. No proprietary brick meshes are bundled.',42)
para(790,H-390,'The model uses black walls and white glazing for easy reading. The white pieces can be replaced with equivalent transparent bricks where available.',42)
for course in range(1,5):
 parts=[p for p in ps if p['layer']==course and p['role'] in ['wall','door lintel']]
 start(f'Wall course {course} - overview',f'{len(parts)} bricks in this wall course | build across all baseplates before proceeding')
 plan(parts,55,100,8.1);legend(880,H-140)
 para(880,H-280,['Door gaps remain empty. Build the lowest wall course directly onto the baseplates.','Add white glazing blocks where shown. Door gaps stay open below their lintels.','Use the long black lintel bricks shown over each doorway; their ends must sit on the two jambs.','Add the continuous top course. Alternate joints where the map changes brick lengths.'][course-1],35)
 for by in range(2):
  for bx in range(3):
   bounds=(bx*32,by*32,(bx+1)*32,(by+1)*32);letter='ABCDEF'[by*3+bx]
   start(f'Course {course} - baseplate {letter}',f'X {bounds[0]} to {bounds[2]-1} | Y {bounds[1]} to {bounds[3]-1} | north is up')
   plan(parts,65,95,18.6,bounds);legend(730,H-135)
   y=H-285
   y=para(730,y,'Each brick has its own outline; the small circles are studs. A brick crossing a blue baseplate edge is one complete brick, not two pieces.',48)
   y=para(730,y,'The same boundary brick is shown clipped on the adjacent page. Place it only once. Keep baseplates touching on the supporting board.',48)
   local=[p for p in parts if bounds[0]<=p['x']<bounds[2] and bounds[1]<=p['y']<bounds[3]]
   ct=collections.Counter((p['part'],p['color']) for p in local)
   text(730,y,'Bricks starting on this baseplate:',12);y-=25
   for (part,color),n in sorted(ct.items()):text(730,y,f'{n:3}   {names[part]}   {color}',11);y-=23
   para(730,135,'If a placement is unclear, brick_placements.csv gives its exact X, Y, width, depth, color and course.',49,11)
start('Interior blocks and stairs','Add these after the wall shell; they remain accessible from above')
interior=[p for p in ps if p['role'] not in ['wall','door lintel','baseplate']]
plan([p for p in ps if p['layer']==1],50,115,8.1,showrooms=True)
y=H-130
for role in sorted(set(p['role'] for p in interior)):
 text(860,y,role.title(),12);y-=21
 for p in [p for p in interior if p['role']==role and p['layer']==1]:text(860,y,f"({p['x']},{p['y']})  {p['w']} x {p['d']}",10);y-=17
 y-=9
start('Interior construction details','Exact repeated footprints are listed in brick_placements.csv')
y=H-125
for head,body in [('Tables and counters','Tan 2 x 4 bricks represent the lab work surfaces. Tan 2 x 2 bricks represent the cafe counter and reception. They are one brick high and attach directly to the baseplates.'),('Equipment and seating','Dark gray 2 x 2 blocks are one brick high for commons seats. Stack two at each equipment station. These are schematic markers rather than miniature replicas of individual machines.'),('Two stair cores','Each core has three adjacent 2 x 2 footprints. Stack one, two and three bricks respectively along the indicated direction. Every block is supported from the baseplate. These are symbolic ground-floor stairs; no upper floor is included.'),('Display and handling','The open-top model exposes the rooms and circulation. Keep all baseplates on a supporting board when moving it. If you want a fully bonded base, design a separate plate foundation before construction; it is not included in the listed parts.')]:
 text(45,y,head,17);y=para(45,y-25,body,132,13)-18
start('Accuracy, validation and source notes','Digital assembly checked; no physical LEGO build has been tested')
y=H-125
for t in ['Plan source: Architectural Plans King School Campus Center, ground-floor sheet A-101; the current structural model supplies wall runs and room positions. The iLab reference is 250825 Innovation Lab REV Design.','The plan is rounded to a 1 metre-per-stud grid, approximately 1:125 horizontally. Walls are one stud thick. Four brick courses are 38.4 mm high, deliberately kept low for a readable cutaway. Doors are one or two studs wide and two courses high.','Some closely spaced doors and very small architectural offsets cannot be represented independently on this grid. 29 openings are retained. The building is not a measured replica of individual wall thicknesses, steps or furniture.','Validation checked every brick footprint for same-course overlap and attachment to studs below. Door lintels are single pieces supported at both ends. The bill of materials and coordinate CSV are generated from the same placements as the LDraw file.','Standard part IDs and coordinate units were checked against the official LDraw library and format specification. The editable LDraw file needs your installed standard parts library; the supplied Blender preview is a schematic visualization.']:
 y=para(45,y,t,145,13)-10
text(45,y,'Sources',15);y-=28
for url in d['sources']:
 text(45,y,url,11,HexColor('#246383'));c.linkURL(url,(45,y-2,1000,y+12),relative=0);y-=25
c.save();print('LEGO_GUIDE_PAGES',page,flush=True)
