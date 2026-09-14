from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).parent;g=np.load(R/'print_height_data.npz')['structural_reference'];mask=g>0
ny,nx=mask.shape;report=json.loads((R/'print_validation.json').read_text());xs=report['split_x_mm'];ys=report['split_y_mm'];colors=[(184,223,234),(184,221,209),(220,218,235),(240,218,177),(222,219,179),(228,202,199)]
arr=np.full((ny,nx,3),248,dtype=np.uint8)
for j in range(2):
    for i in range(3):
        a=np.zeros_like(mask);a[round(ys[j]*2):round(ys[j+1]*2),round(xs[i]*2):round(xs[i+1]*2)]=True;arr[a&mask]=colors[j*3+i]
arr[(g>4.801)&mask]=(74,83,95)
im=Image.new('RGB',(1700,1400),(248,249,251));im.paste(Image.fromarray(arr[::-1]),(50,100));d=ImageDraw.Draw(im)
def f(s,b=False):return ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf' if b else 'C:/Windows/Fonts/segoeui.ttf',s)
def xy(x,y):return (50+x*2,100+ny-y*2)
d.text((65,25),'CAMPUS CENTER / SIX-TILE ASSEMBLY',fill=(28,47,61),font=f(32,True))
d.text((65,68),'Top view · North up · Ground floor with furniture · No extra ground plane',fill=(77,94,108),font=f(20))
for j in range(2):
    for i in range(3):
        x=(xs[i]+xs[i+1])/2;y=(ys[j]+ys[j+1])/2
        d.text(xy(x,y),f'{chr(65+j)}{i+1}',font=f(58,True),fill=(28,47,61),anchor='mm',stroke_width=2,stroke_fill=(248,249,251))
for x in xs[1:-1]:
    for y in range(8,570,10):d.line([xy(x,y),xy(x,y+5)],fill=(40,120,147),width=3)
for x in range(13,756,10):d.line([xy(x,289),xy(x+5,289)],fill=(40,120,147),width=3)
d.text((65,1325),'North row: B1 · B2 · B3     |     South row: A1 · A2 · A3     |     Assembly: 743 × 562 mm',font=f(23,True),fill=(28,47,61))
d.text((65,1360),'Match shared cut edges. Outside corners and local tile origins differ. Illustration is not a full-size paper template.',font=f(18),fill=(77,94,108))
im.save(R/'Assembly_Map.png')
print('ASSEMBLY_MAP_COMPLETE')
