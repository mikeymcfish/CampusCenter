from pathlib import Path
import sys,re
R=Path(__file__).parent;sys.path.insert(0,str(R/'python_packages'))
import pymupdf
from PIL import Image,ImageDraw,ImageFont
for name in ['King_seal','King_wordmark']:
 svg=(R/'assets'/(name+'.svg')).read_text()
 # MuPDF does not resolve SVG stylesheet classes: inline their declared fills.
 for cls,fill in re.findall(r'\.(cls-\d+)\{fill:(#[0-9a-fA-F]+);\}',svg):svg=svg.replace('class="'+cls+'"','fill="'+fill+'"')
 d=pymupdf.open(stream=svg.encode(),filetype='svg');d[0].get_pixmap(matrix=pymupdf.Matrix(6,6),alpha=True).save(str(R/'assets'/(name+'.png')))
im=Image.new('RGB',(700,2100),'#082e50');d=ImageDraw.Draw(im)
d.rectangle((22,22,678,2078),outline='#b39a65',width=3)
seal=Image.open(R/'assets/King_seal.png').convert('RGBA');seal.thumbnail((485,620));im.paste(seal,((700-seal.width)//2,430),seal)
for txt,y,size in [('KING',1120,155),('SCHOOL',1300,80)]:
 f=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',size);bb=d.textbbox((0,0),txt,font=f);d.text(((700-bb[2])/2,y),txt,font=f,fill='#f7f5ee')
im.save(R/'assets/King_banner.png')
