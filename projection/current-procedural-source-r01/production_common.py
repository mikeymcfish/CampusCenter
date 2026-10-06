from uvprep_common import *
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import time, argparse

PROD=R/'madmapper_production_P01';CACHE=PROD/'cache';EXPORT=PROD/'deliverables'
for q in [PROD,CACHE,EXPORT]:q.mkdir(parents=True,exist_ok=True)
H02=V/'highlight_scope_H02/deliverables'
FONT=Path(r'C:\Windows\Fonts\segoeui.ttf')
BOLD=Path(r'C:\Windows\Fonts\segoeuib.ttf')
COPY=json.loads((H02/'copy/Usable_13_Stop_Copy.json').read_text(encoding='utf-8'))

def config(scale=100):
 folder='assembly_1_100' if scale==100 else 'sample_1_250'
 stem='CampusCenter_P02_Assembly_1_100_UV01' if scale==100 else 'CampusCenter_P02_Sample_1_250_UV01'
 src=D/folder
 c=json.loads((SOURCE/'projection/Projection_Coordinate_Contract.json').read_text())
 return {'scale':scale,'folder':folder,'stem':stem,'source':src,'obj':src/(stem+'.obj'),
         'canvas':np.array(c['canvas_mm'])*100/scale,'center':np.array(c['center_mm'])*100/scale,
         'top_size':(c['width'],c['height']),'base':4.2 if scale==100 else 2.0}

def barypatch(px,limit):
 lo=np.maximum(np.floor(px.min(0)).astype(int),0);hi=np.minimum(np.ceil(px.max(0)).astype(int),limit-1)
 x0,y0=lo;x1,y1=hi
 if x1<x0 or y1<y0:return None
 (ax,ay),(bx,by),(cx,cy)=px;den=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
 if abs(den)<1e-14:return None
 yy,xx=np.mgrid[y0:y1+1,x0:x1+1];xx=xx+.5;yy=yy+.5
 a=((by-cy)*(xx-cx)+(cx-bx)*(yy-cy))/den;b=((cy-ay)*(xx-cx)+(ax-cx)*(yy-cy))/den;c=1-a-b
 good=(a>=-1e-8)&(b>=-1e-8)&(c>=-1e-8)
 return (x0,y0,x1,y1),a,b,c,good

def build_cache(scale=100,res=8192):
 cfg=config(scale);root=CACHE/f'{cfg["folder"]}_{res}_world64';root.mkdir(exist_ok=True)
 meta=root/'Cache_Contract.json'
 if meta.exists():
  m=json.loads(meta.read_text())
  assert m['OBJ_sha256']==sha(cfg['obj'])
  return root
 v,u,n,parts=parse_obj(cfg['obj']);p=parts['Opaque'];tri=v[p['f']];uv=u[p['ft']];centers,norm,areas=geom(v,p['f'])
 # World coordinates are stored in sixty-fourths of a 1:100 model millimetre.
 # Both physical scales share the 1:100 presentation design without rescaling meshes.
 arrays={k:np.lib.format.open_memmap(root/(k+'.npy'),mode='w+',dtype=dt,shape=(res,res)) for k,dt in [('x','uint16'),('y','uint16'),('z','uint16'),('light','uint8'),('up','uint8'),('valid','uint8')]}
 for arr in arrays.values():arr[:]=0
 light=np.array([-.38,.50,.78]);light/=np.linalg.norm(light)
 factor=scale/100
 receiver=np.asarray(Image.open(cfg['source']/'Default_Opaque_Receiver_Mask.png').convert('L').resize((res,res),Image.Resampling.NEAREST))>0
 overlap=0
 for i,(t,ut,nn) in enumerate(zip(tri,uv,norm)):
  patch=barypatch(ut*np.array([res,-res])+[0,res],np.array([res,res]))
  if patch is None:continue
  (x0,y0,x1,y1),a,b,c,ok=patch;sl=np.s_[y0:y1+1,x0:x1+1]
  ok&=receiver[sl]
  if not ok.any():continue
  w=a[:,:,None]*t[0]+b[:,:,None]*t[1]+c[:,:,None]*t[2];w*=factor
  overlap+=int(np.count_nonzero((arrays['valid'][sl]>0)&ok))
  for k,j in [('x',0),('y',1),('z',2)]:arrays[k][sl][ok]=np.uint16(np.clip(np.round(w[:,:,j]*64),0,65535)[ok])
  arrays['light'][sl][ok]=np.uint8(np.clip((.40+.60*max(0,float(nn@light)))*255,0,255))
  arrays['up'][sl][ok]=255 if nn[2]>.9 else 0
  arrays['valid'][sl][ok]=255
  if i%10000==0:print('UV world-transfer cache',scale,res,i,'/',len(tri),flush=True)
 for arr in arrays.values():arr.flush()
 m={'OBJ':str(cfg['obj']),'OBJ_sha256':sha(cfg['obj']),'scale':scale,'resolution':res,
    'mesh_and_UV_changes':[],'coordinate_encoding':'uint16 sixty-fourths of a 1:100 presentation model millimetre; divide by64; physical meshes unchanged',
    'bake':'Barycentric surface-colour/render transfer through each original indexed triangle UV; no source UV changes',
    'light_direction_world_XYZ':light.tolist(),'occupied_texels':int(np.count_nonzero(arrays['valid'])),
    'shared_edge_center_hits':overlap,'top_visibility_assumption':'Orthographic projector approximately normal to floor, +Z; no hidden-wall projection claim'}
 meta.write_text(json.dumps(m,indent=2));print('CACHE COMPLETE',root,flush=True);return root

def cache_arrays(scale=100,res=8192):
 root=build_cache(scale,res)
 return {k:np.load(root/(k+'.npy'),mmap_mode='r') for k in ['x','y','z','light','up','valid']}

def top_indices(scale=100):
 cfg=config(scale);root=CACHE/(cfg['folder']+'_top');root.mkdir(exist_ok=True)
 if (root/'Complete.json').exists():return root
 v,u,n,parts=parse_obj(cfg['obj']);W,H=cfg['top_size'];height=np.full((H,W),-1,np.float32);tu=np.zeros((H,W),np.float32);tv=np.zeros((H,W),np.float32);material=np.zeros((H,W),np.uint8)
 for mi,name in enumerate(['Opaque','Glazing','HangingLoops'],1):
  if name not in parts:continue
  p=parts[name];tri=v[p['f']];uv=u[p['ft']];centers,norm,area=geom(v,p['f']);pix=(tri[:,:,:2]-cfg['center']+cfg['canvas']/2)/cfg['canvas']*[W,H];pix[:,:,1]=H-pix[:,:,1]
  for t,ut,px,nn in zip(tri,uv,pix,norm):
   if nn[2]<=.001:continue
   patch=barypatch(px,np.array([W,H]))
   if patch is None:continue
   (x0,y0,x1,y1),a,b,c,ok=patch;sl=np.s_[y0:y1+1,x0:x1+1];z=a*t[0,2]+b*t[1,2]+c*t[2,2];ok&=z>=height[sl]-1e-8
   height[sl][ok]=z[ok];tu[sl][ok]=(a*ut[0,0]+b*ut[1,0]+c*ut[2,0])[ok];tv[sl][ok]=(a*ut[0,1]+b*ut[1,1]+c*ut[2,1])[ok];material[sl][ok]=mi
 for k,arr in [('height',height),('u',tu),('v',tv),('material',material)]:np.save(root/(k+'.npy'),arr)
 (root/'Complete.json').write_text(json.dumps({'source_OBJ_sha256':sha(cfg['obj']),'geometry_changes':[],'UV_changes':[],'preview':'Exact original triangles and UVs, orthographic +Z receiver'}));return root

def actual_top(atlas,scale=100):
 root=top_indices(scale);tu=np.load(root/'u.npy');tv=np.load(root/'v.npy');mat=np.load(root/'material.npy');S=atlas.shape[0]
 xx=np.clip(np.floor(tu*S).astype(int),0,S-1);yy=np.clip(np.floor((1-tv)*S).astype(int),0,S-1)
 image=np.zeros((*mat.shape,3),np.uint8);image[mat==1]=atlas[yy[mat==1],xx[mat==1]]
 return image

def labelled_preview(raw,title,path):
 W,H=raw.shape[1],raw.shape[0];out=Image.new('RGB',(W,H+90),(12,17,23));out.paste(Image.fromarray(raw),(0,90));dr=ImageDraw.Draw(out)
 dr.text((22,14),title,font=ImageFont.truetype(str(FONT),27),fill='white')
 dr.text((22,51),'Mapped receiver preview | frozen P02 UV01 geometry | emission only | +Z normal view | physical projection untested',font=ImageFont.truetype(str(FONT),18),fill=(178,192,205));out.save(path)

def preservation():
 baseline=json.loads((V/'highlight_scope_H02/Source_Baseline.json').read_text())
 for p in (H02).rglob('*'):
  if p.is_file():baseline[str(p)]=sha(p)
 return baseline

def verify_preservation(baseline):
 bad=[p for p,h in baseline.items() if sha(p)!=h]
 assert not bad,bad
 return {'files_verified':len(baseline),'all_source_P02_UV01_H01_H02_files_unchanged':True,'changed_files':[]}
