"""Measure visible batten bounds from the architect reference; no image alteration."""
from pathlib import Path
import sys,json
root=Path(__file__).parent
sys.path.insert(0,str(root/'analysis_deps'))
import cv2,numpy as np
source=Path('C:/Users/mikef/Downloads/gisolfillp_260922_king-school-commons_v01-jpg_2026-09-22_1337/260922_King School Commons_v01.jpg')
im=cv2.imread(str(source));sy=im.shape[0]/1153;sx=im.shape[1]/2048
quad=np.float32([[421*sx,276*sy],[1083*sx,185*sy],[1083*sx,652*sy],[421*sx,652*sy]])
W,H=1600,1000
matrix=cv2.getPerspectiveTransform(quad,np.float32([[0,0],[W,0],[W,H],[0,H]]))
flat=cv2.warpPerspective(im,matrix,(W,H));hsv=cv2.cvtColor(flat,cv2.COLOR_BGR2HSV)
result=[]
for color,lo,hi in [('blue',(90,90,35),(125,255,255)),('wood',(7,60,55),(34,255,225))]:
 mask=cv2.inRange(hsv,np.array(lo),np.array(hi))
 mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((7,1),np.uint8))
 # Split by vertical strips rather than connected components: fins join in the
 # dark top edge and K silhouette, but must remain individual pieces of geometry.
 occupied=(mask[20:980]>0).sum(axis=0)>45
 edges=np.diff(np.r_[False,occupied,False].astype(int)); starts=np.where(edges==1)[0];ends=np.where(edges==-1)[0]
 for xa,xb in zip(starts,ends):
  width=xb-xa
  centers=[(xa+xb)/2] if width<=30 else list(np.arange(xa+4,xb,8))
  for center in centers:
   x=int(center); col=(mask[:,max(0,x-1):x+2]>0).mean(axis=1)>.4
   # Close small highlight interruptions along a single fin.
   col=cv2.morphologyEx(col.astype(np.uint8).reshape(-1,1),cv2.MORPH_CLOSE,np.ones((10,1),np.uint8)).ravel()>0
   edges=np.diff(np.r_[False,col,False].astype(int));ys=np.where(edges==1)[0];ye=np.where(edges==-1)[0]
   for y0,y1 in zip(ys,ye):
    if y1-y0<25:continue
    result.append({'color':color,'x':round(center/W,5),'bottom':round(1-y1/H,5),'top':round(1-y0/H,5),'width':round(min(width,7 if width>30 else width)/W,5)})
result.sort(key=lambda v:(v['x'],v['bottom']))
data={'source':source.name,'method':'Perspective rectification and HSV connected components; visible segments only; occluded extents not inferred.','quad_in_2048px_preview':[[421,276],[1083,185],[1083,652],[421,652]],'segments':result}
(root/'reference_batten_measurements.json').write_text(json.dumps(data,indent=2))
print('Measured',len(result),'segments', {c:sum(s['color']==c for s in result) for c in ['blue','wood']})
print(json.dumps(result[:5]))
