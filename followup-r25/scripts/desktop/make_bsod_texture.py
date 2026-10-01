from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
root=Path(__file__).parent/'combined_r01';out=root/'bsod_source';out.mkdir(exist_ok=True)
im=Image.new('RGB',(1920,1080),(0,120,215));d=ImageDraw.Draw(im)
def font(size):return ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',size)
d.text((200,60),':(',font=font(280),fill='white')
d.multiline_text((200,430),'Your PC ran into a problem.\nYour system needs to restart.\nCollecting some error info…',font=font(76),fill='white',spacing=15)
d.text((200,785),'0% complete',font=font(64),fill='white')
d.text((200,940),'Stop code: CAMPUS_CENTER_BREAK_TIME',font=font(46),fill='white')
im.save(out/'ReceptionTV65_BSOD_R01.png')
print('Created static fictional BSOD display texture; no QR, URL, personal data or executable behavior.')
