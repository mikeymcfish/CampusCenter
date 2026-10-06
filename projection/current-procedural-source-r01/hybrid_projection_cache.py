from pathlib import Path
import json,numpy as np
from production_common import top_indices,barypatch,config,sha
from uvprep_common import parse_obj,geom
R=Path(__file__).parent;C=R/'madmapper_hybrid_UV02/cache/top';C.mkdir(parents=True,exist_ok=True)
OBJ=R/'madmapper_hybrid_UV02/deliverables/CampusCenter_P02plusP03B3_Assembly_1_100_UV02.obj'
def load():
    meta=C/'Complete.json'
    if not meta.exists():
        old=top_indices(100);height=np.load(old/'height.npy');u=np.load(old/'u.npy');v=np.load(old/'v.npy');material=np.load(old/'material.npy')
        vv,uv,n,p=parse_obj(OBJ);new=p['Opaque_Fireplace_P03_B3'];tri=vv[new['f']];ut=uv[new['ft']];_,nn,a=geom(vv,new['f']);cfg=config();W,H=cfg['top_size'];pix=(tri[:,:,:2]-cfg['center']+cfg['canvas']/2)/cfg['canvas']*[W,H];pix[:,:,1]=H-pix[:,:,1]
        for t,q,px,norm in zip(tri,ut,pix,nn):
            if norm[2]<=.001:continue
            patch=barypatch(px,np.array([W,H]))
            if patch is None:continue
            (x0,y0,x1,y1),a,b,c,ok=patch;sl=np.s_[y0:y1+1,x0:x1+1];z=a*t[0,2]+b*t[1,2]+c*t[2,2];ok&=z>=height[sl]-1e-8
            height[sl][ok]=z[ok];u[sl][ok]=(a*q[0,0]+b*q[1,0]+c*q[2,0])[ok];v[sl][ok]=(a*q[0,1]+b*q[1,1]+c*q[2,1])[ok];material[sl][ok]=1
        for name,x in [('height',height),('u',u),('v',v),('material',material)]:np.save(C/(name+'.npy'),x)
        meta.write_text(json.dumps({'receiver':str(OBJ),'receiver_sha256':sha(OBJ),'original_cached_top_geometry_and_UV_preserved':True,'new_fireplace_visibility_rasterised_from_actual_triangles':True,'projection':'Unchanged +Z orthographic 2048x1572 canvas726.25mm center348.25,252.875; nearest texture sampling; reference only'},indent=2))
    else:assert json.loads(meta.read_text())['receiver_sha256']==sha(OBJ)
    return {k:np.load(C/(k+'.npy')) for k in ['height','u','v','material']}
def map_atlas(atlas):
    a=load();res=atlas.shape[0];xx=np.clip(np.floor(a['u']*res).astype(int),0,res-1);yy=np.clip(np.floor((1-a['v'])*res).astype(int),0,res-1);mask=a['material']>0
    result=np.zeros((*mask.shape,3),np.uint8);result[mask]=atlas[yy[mask],xx[mask]];return result
