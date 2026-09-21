import cv2,numpy as np,json,sys
from PIL import Image,ImageDraw
from pathlib import Path
R=Path(__file__).parent;name=sys.argv[1];D=R/('retry' if '--retry' in sys.argv else 'final' if '--final' in sys.argv else 'trials')/name
status=json.loads((D/'status.json').read_text());p=Path(status['generated_files'][0]);prefix=''
if '--projection' in sys.argv:p=D/'Projection_Lossless.mkv';prefix='Projection_'
cap=cv2.VideoCapture(str(p));frames=[]
while True:
    ok,bgr=cap.read()
    if not ok:break
    frames.append(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB))
fps=cap.get(cv2.CAP_PROP_FPS);cap.release();assert frames
indices=np.linspace(0,len(frames)-1,8).round().astype(int);sheet=Image.new('RGB',(4*320,2*345),(20,20,20))
for k,i in enumerate(indices):
    im=Image.fromarray(frames[i]);im.thumbnail((320,320));sheet.paste(im,(k%4*320,k//4*345));ImageDraw.Draw(sheet).text((k%4*320+5,k//4*345+321),f'frame {i} / {i/fps:.2f}s',fill='white')
sheet.save(D/(prefix+'Contact_Sheet.jpg'))
orb=cv2.ORB_create(nfeatures=2000);first=cv2.cvtColor(frames[0],cv2.COLOR_RGB2GRAY);k0,d0=orb.detectAndCompute(first,None);measures=[]
for i in indices[1:]:
    gray=cv2.cvtColor(frames[i],cv2.COLOR_RGB2GRAY);k,d=orb.detectAndCompute(gray,None)
    pairs=cv2.BFMatcher(cv2.NORM_HAMMING).knnMatch(d0,d,k=2);good=[a for a,b in pairs if a.distance<.7*b.distance]
    if len(good)<8:continue
    a=np.float32([k0[m.queryIdx].pt for m in good]);b=np.float32([k[m.trainIdx].pt for m in good]);M,inliers=cv2.estimateAffinePartial2D(a,b,method=cv2.RANSAC,ransacReprojThreshold=2)
    if M is None:continue
    measures.append({'frame':int(i),'matches':len(good),'inliers':int(inliers.sum()),'translation_px':float(np.linalg.norm(M[:,2])),'rotation_deg':float(np.degrees(np.arctan2(M[1,0],M[0,0]))),'scale':float(np.hypot(M[0,0],M[1,0]))})
report={'video':str(p),'frames':len(frames),'fps':fps,'seconds':len(frames)/fps,'size':list(frames[0].shape[:2][::-1]),'endpoint_mean_absolute_difference':float(np.abs(frames[-1].astype(float)-frames[0]).mean()),'feature_registration':measures,'caveat':'Feature fit is diagnostic only; moving people and repeated furniture can bias it. Visual review required.'}
transitions=[float(np.abs(b.astype(np.int16)-a.astype(np.int16)).mean()) for a,b in zip(frames[:-1],frames[1:])]
report['temporal_difference']={'median_adjacent_frame_rgb_mae':float(np.median(transitions)),'p95_adjacent_frame_rgb_mae':float(np.percentile(transitions,95)),'maximum_adjacent_frame_rgb_mae':max(transitions),'loop_seam_rgb_mae':report['endpoint_mean_absolute_difference'],'note':'Whole-frame differences include compression and lighting; this is a seam diagnostic, not proof of natural gait.'}
(D/(prefix+'review.json')).write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
