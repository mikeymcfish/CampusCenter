"""Infinity Rooms R02: virtual colour animation on the unchanged UV02 mesh."""
from pathlib import Path
import json,hashlib,math,subprocess,os
import numpy as np
from PIL import Image,ImageFilter
from production_common import cache_arrays,barypatch
from uvprep_common import parse_obj,geom

R=Path(__file__).parent
T=R/'madmapper_infinity_rooms_R02';D=T/'deliverables';C=T/'cache'
for p in [T,D,C]:p.mkdir(parents=True,exist_ok=True)
OBJ=R/'madmapper_hybrid_UV02/deliverables/CampusCenter_P02plusP03B3_Assembly_1_100_UV02.obj'
OBJ_SHA='b949784cbb3f833d10d82fdd48d469ac3fac1b8ac723f7cc08588ca633a59fba'
EYE=np.array([348.25,-600.,850.]);TARGET=np.array([348.25,252.875,12.]);FLOOR_Z=4.5
W,H=1024,768;HFOV=42.;RES=4096;FPS=20;SECONDS=24;FRAMES=FPS*SECONDS
FF=Path(os.environ.get('FFMPEG','ffmpeg'));FP=FF.with_name('ffprobe.exe')
PALETTE=np.array([[40,225,240],[70,176,248],[115,149,240],[45,214,203]],np.float32)

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()

def write_json(p,q):p.write_text(json.dumps(q,indent=2),encoding='utf-8')

def camera_basis():
    forward=(TARGET-EYE);forward/=np.linalg.norm(forward)
    right=np.cross(forward,[0,0,1]);right/=np.linalg.norm(right)
    up=np.cross(right,forward)
    return right,up,forward,W/(2*np.tan(np.radians(HFOV/2)))

def front_cache():
    meta=C/'Fixed_Front_Receiver_Cache_QA.json'
    if meta.exists():
        q=json.loads(meta.read_text());assert q['receiver_SHA256']==sha(OBJ)==OBJ_SHA
        return {k:np.load(C/(k+'.npy'),mmap_mode='r') for k in ['front_u','front_v','front_part','front_z']}
    v,uv,n,parts=parse_obj(OBJ);right,up,forward,f=camera_basis();delta=v-EYE
    vv=np.stack([delta@right,delta@up,delta@forward],1);px=np.stack([W/2+f*vv[:,0]/vv[:,2],H/2-f*vv[:,1]/vv[:,2]],1)
    assert vv[:,2].min()>0
    assert np.all(px[:,0]>0) and np.all(px[:,0]<W) and np.all(px[:,1]>0) and np.all(px[:,1]<H),'Front framing crops the original mesh'
    z=np.full((H,W),np.inf,np.float32);tu=np.zeros((H,W),np.float32);tv=np.zeros((H,W),np.float32);part=np.zeros((H,W),np.uint8)
    for mi,(name,p) in enumerate(parts.items(),1):
        tris=p['f'];uts=uv[p['ft']]
        for fi,(tri,ut) in enumerate(zip(tris,uts)):
            pp=px[tri];zs=vv[tri,2];patch=barypatch(pp,np.array([W,H]))
            if patch is None:continue
            (x0,y0,x1,y1),a,b,c,ok=patch;sl=np.s_[y0:y1+1,x0:x1+1]
            iz=a/zs[0]+b/zs[1]+c/zs[2];depth=1/np.maximum(iz,1e-12);ok&=depth<z[sl]
            if not ok.any():continue
            uu=(a*ut[0,0]/zs[0]+b*ut[1,0]/zs[1]+c*ut[2,0]/zs[2])/iz
            ve=(a*ut[0,1]/zs[0]+b*ut[1,1]/zs[1]+c*ut[2,1]/zs[2])/iz
            z[sl][ok]=depth[ok];tu[sl][ok]=uu[ok];tv[sl][ok]=ve[ok];part[sl][ok]=mi
        print('FRONT CACHE PART',name,len(tris),flush=True)
    for k,x in [('front_u',tu),('front_v',tv),('front_part',part),('front_z',z)]:np.save(C/(k+'.npy'),x)
    write_json(meta,{'status':'PASS','receiver_SHA256':sha(OBJ),'width':W,'height':H,'eye_mm':EYE.tolist(),'target_mm':TARGET.tolist(),'horizontal_FOV_degrees':HFOV,'projection':'Perspective-correct barycentric UV interpolation and nearest-depth triangle visibility, fixed pinhole camera; original opaque/glazing/loops/fireplace geometry retained','all_original_vertices_inside_frame':True,'whole_receiver_parts':list(parts),'occupied_visible_pixels':int((part>0).sum()),'original_geometry_or_UVs_changed':False,'front_side_assumption':'South / negative Y; +Y north. No earlier front-side choice was available.','physical_projector_pose_calibrated':False})
    return {'front_u':tu,'front_v':tv,'front_part':part,'front_z':z}

class Effect:
    def __init__(self):
        assert sha(OBJ)==OBJ_SHA
        self.g=np.load(C/'Infinity_Room_Apertures_And_Depth.npz',allow_pickle=False)
        self.meta=json.loads((C/'Infinity_Geometry_And_View_Contract.json').read_text())
        self.arr=cache_arrays(100,RES);valid=self.arr['valid']>0
        self.floor=valid&(self.arr['up']>0)&(self.arr['z']<=5.4*64)
        flat=np.flatnonzero(self.floor);wx=self.arr['x'].reshape(-1)[flat].astype(np.float32)/64;wy=self.arr['y'].reshape(-1)[flat].astype(np.float32)/64
        origin=self.g['origin'];pitch=float(self.g['pitch']);gh,gw=self.g['owner'].shape
        gx=np.floor((wx-origin[0])/pitch).astype(int);gy=np.floor((wy-origin[1])/pitch).astype(int)
        inside=(gx>=0)&(gx<gw)&(gy>=0)&(gy<gh);flat=flat[inside];gx=gx[inside];gy=gy[inside]
        chosen=self.g['aperture'][gy,gx];self.flat=flat[chosen];self.ix=gx[chosen];self.iy=gy[chosen]
        self.owner=self.g['owner'];self.hole=self.g['aperture'];self.wall_depth=self.g['wall_depth'];self.axis=self.g['wall_axis'];self.dist=self.g['edge_distance'];self.yy,self.xx=np.nonzero(self.hole)
        self.ids=self.owner[self.yy,self.xx].astype(int)
        size=int(self.owner.max())+1;self.maxdepth=np.zeros(size,np.float32);self.spacing=np.zeros(size,np.float32);self.phase=np.zeros(size,np.float32);self.tint=np.zeros((size,3),np.float32)
        for i,row in enumerate(self.meta['regions']):
            rid=row['region_id'];self.maxdepth[rid]=row['maximum_virtual_depth_mm'];self.spacing[rid]=row['layer_spacing_mm'];self.phase[rid]=row['phase_radians'];self.tint[rid]=row['colour_RGB']
        self.base=np.zeros((RES,RES,3),np.uint8)
        # Static physical support surfaces remain at their actual model heights.
        raised=valid&~self.floor;light=self.arr['light'][raised].astype(np.float32)/255;up=self.arr['up'][raised]>0
        col=np.where(up[:,None],np.array([50,126,150]),np.array([20,49,67]))
        self.base[raised]=np.uint8(np.rint(col*light[:,None]))
        self.base[self.floor]=[7,17,24]
        fire=R/'madmapper_hybrid_UV02/deliverables';mask=np.array(Image.open(fire/'Fireplace_New_Chart_Mask_8192.png').resize((RES,RES),Image.Resampling.NEAREST))>0
        patch=np.array(Image.open(fire/'Fireplace_Only_Patch_8192.png').convert('RGB').resize((RES,RES),Image.Resampling.NEAREST))
        factor=patch.max(2).astype(np.float32)/255;self.base[mask]=np.uint8(np.rint(factor[mask,None]*[36,95,115]))
        self.dynamic_mask=np.zeros((RES,RES),bool);self.dynamic_mask.reshape(-1)[self.flat]=True
        self.front=front_cache();self.front_ax=np.clip(np.floor(self.front['front_u']*RES).astype(int),0,RES-1);self.front_ay=np.clip(np.floor((1-self.front['front_v'])*RES).astype(int),0,RES-1)
        print('INFINITY TRANSFER',len(self.flat),'animated floor texels; fixed front cache ready',flush=True)

    def grid(self,frame):
        q=self.ids;t=frame/FPS;angle=2*np.pi*t/SECONDS+self.phase[q]
        frac=.5-.5*np.cos(angle)
        depth=self.spacing[q]*1.25+(self.maxdepth[q]-self.spacing[q]*1.25)*frac
        wall=self.wall_depth[self.yy,self.xx];edge=self.dist[self.yy,self.xx]
        spacing=self.spacing[q];tone=self.tint[q]
        # First-exit depths follow the actual aperture/obstacle shape. Only
        # virtual below-floor sidewalls and floor positions are animated.
        side=wall<depth
        p=((wall+spacing*.16*np.sin(angle))/spacing+.5)%1-.5
        width=np.maximum(.65,spacing*.075)/spacing
        band=np.exp(-(p/width)**2)
        fade=np.exp(-wall/np.maximum(self.maxdepth[q]*1.1,1))
        axis=self.axis[self.yy,self.xx];normal=np.where(axis==2,1.,.66)
        rgb=np.zeros((len(q),3),np.float32)
        rgb[:]=[1,3,7]
        strength=(.08+.68*band)*fade*normal
        rgb[side]=tone[side]*strength[side,None]
        # Descending plane uses local room-shaped contours instead of a shared grid.
        local=np.clip(edge/np.maximum(spacing*.65,1),0,1)
        bottom=.025+.08*(1-local)+.055*np.exp(-((wall-depth)/np.maximum(.7,spacing*.09))**2)
        rgb[~side]=tone[~side]*bottom[~side,None]
        rim=np.exp(-(edge/.85)**2)
        rgb=np.maximum(rgb,tone*rim[:,None]*.7)
        # Geometry-local supports and walls are fixed. No flashes, noise or bloom.
        out=np.zeros((*self.hole.shape,3),np.uint8);out[self.yy,self.xx]=np.uint8(np.clip(np.rint(rgb),0,248))
        return out

    def render(self,frame):
        field=self.grid(frame);atlas=self.base.copy();atlas.reshape(-1,3)[self.flat]=field[self.iy,self.ix]
        assert np.array_equal(atlas[~self.dynamic_mask],self.base[~self.dynamic_mask])
        return atlas

    def mapped(self,atlas):
        out=np.zeros((H,W,3),np.uint8);mask=self.front['front_part']>0
        out[mask]=atlas[self.front_ay[mask],self.front_ax[mask]]
        return Image.fromarray(out)
