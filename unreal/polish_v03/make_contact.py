from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json
root=Path(__file__).resolve().parent.parent/'unreal_project/ReviewV03'
names=['Entrance','Commons','Innovation Lab','Printers','Student lockers','Student bathroom','Fitness','Upper commons','Balcony']
canvas=Image.new('RGB',(1920,1194),(22,25,29));draw=ImageDraw.Draw(canvas)
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',22)
rows=[]
for i,name in enumerate(names):
 p=root/f'room_{i:02d}.png'
 with Image.open(p) as im:
  im.load();assert im.size==(1920,1080),(p,im.size)
  canvas.paste(im.convert('RGB').resize((640,360)),((i%3)*640,(i//3)*398))
 draw.text(((i%3)*640+14,(i//3)*398+367),name,font=font,fill='white')
 rows.append({'file':p.name,'size':[1920,1080],'name':name})
canvas.save(root/'Cinematic_Review.jpg',quality=94)
(root/'image_validation.json').write_text(json.dumps({'images':rows,'count':len(rows),'status':'passed'},indent=2))
