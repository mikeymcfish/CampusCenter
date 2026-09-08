from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import struct,json
R=Path(__file__).parent;rows=[]
def exr_info(path):
 with path.open('rb') as f:
  assert struct.unpack('<I',f.read(4))[0]==20000630;version=struct.unpack('<I',f.read(4))[0]
  def word():
   data=b''
   while True:
    c=f.read(1)
    if c==b'\0':return data.decode()
    if not c:raise ValueError('Truncated EXR')
    data+=c
  parts=[];attrs={}
  while True:
   name=word()
   if not name:
    if not attrs:break
    parts.append(attrs);attrs={}
    if not version&4096:break
    continue
   typ=word();size=struct.unpack('<I',f.read(4))[0];attrs[name]=(typ,f.read(size))
 channels=[]
 for attrs in parts:
  data=attrs['channels'][1];i=0
  while data[i:i+1]!=b'\0':
   end=data.index(b'\0',i);channels.append(data[i:end].decode());i=end+1+16
 dims=struct.unpack('<4i',parts[0]['dataWindow'][1]);return {'parts':len(parts),'channels':channels,'dimensions':[dims[2]-dims[0]+1,dims[3]-dims[1]+1]}
contact=Image.new('RGB',(1920,2360),(25,28,30));draw=ImageDraw.Draw(contact);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',25)
for i,name in enumerate(['01_Entrance','02_Commons','03_iLab','04_Gallery','05_Printer_Detail','06_Entrance_Planting','07_Fireplace','08_iLab_Posters']):
 p=R/'stills'/(name+'.png');head=p.read_bytes()[:29];assert head[24]==16,(name,'not16bit')
 with Image.open(p) as im:
  im.load();assert im.size==(1920,1080);im.convert('RGB').save(R/'stills'/(name+'_preview.jpg'),quality=95);thumb=im.convert('RGB').resize((960,540))
  x=(i%2)*960;y=(i//2)*590;contact.paste(thumb,(x,y));draw.text((x+15,y+551),name.replace('_',' '),font=font,fill='white')
 e=exr_info(R/'stills'/(name+'.exr'));assert e['dimensions']==[1920,1080];assert any('Combined' in c for c in e['channels']);assert any('Normal' in c for c in e['channels'])
 rows.append({'file':name,'png_bits':16,'exr':e})
contact.save(R/'stills/Eight_Views.jpg',quality=95)
(R/'image_validation.json').write_text(json.dumps({'status':'passed','images':rows},indent=2))
