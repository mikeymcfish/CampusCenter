from pathlib import Path
import numpy as np,json
from PIL import Image,ImageDraw
R=Path(__file__).parent;P=R.parent/'projection_acrylic_v06'
records=[];sheet=Image.new('RGB',(1024,5*300),(25,25,25))
for i,n in enumerate(['108','102','121','122','GYM']):
    d=R/'depth'/n;a=np.load(d/'camera_depth_metres.npy')
    mask=np.array(Image.open(P/'rooms'/n/'Room_Mask_1024.png').convert('L'))>127
    assert a.shape==(1024,1024) and np.isfinite(a[mask]).all()
    values=a[mask];assert values.max()>values.min()+.2,(n,values.min(),values.max())
    # Constant camera-distance range across all rooms/frames, near white.
    normalized=np.where(mask,np.clip(1-a/4.5,0,1),0)
    Image.fromarray((normalized*65535).round().astype(np.uint16)).save(d/'Depth_16bit.png')
    Image.fromarray((normalized*255).round().astype(np.uint8)).save(d/'Depth_Control.png')
    for j,f in enumerate([P/'rooms'/n/'Topdown_Black.png',d/'Depth_Control.png']):
        im=Image.open(f).convert('RGB');im.thumbnail((480,280));sheet.paste(im,(j*512+(512-im.width)//2,i*300))
    ImageDraw.Draw(sheet).text((5,i*300+280),n+' beauty / Blender camera depth',fill='white')
    records.append({'room':n,'min_m':float(values.min()),'max_m':float(values.max()),'near_m':0,'far_m':4.5,'outside_mask_zero':True,'source':'Blender camera depth emission float EXR, not estimated image depth'})
sheet.save(R/'Depth_Contact_Sheet.jpg')
(R/'depth_validation.json').write_text(json.dumps(records,indent=2))
print(json.dumps(records,indent=2))
