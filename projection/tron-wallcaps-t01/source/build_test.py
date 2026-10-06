"""UV02 wall-only authoring. No writes to receiver/source folders."""
from inspect_receiver import *
from PIL import Image
from scipy.ndimage import distance_transform_edt, binary_dilation
from scipy.spatial import cKDTree
from collections import defaultdict, deque
import time, argparse, subprocess, sys, os, shutil

S=8192; FPS=24; DURATION=10.; PYTHON=Path(sys.executable)
FFMPEG=Path(os.environ.get('CC_FFMPEG', shutil.which('ffmpeg') or 'ffmpeg.exe'))
OUT=ROOT/'deliverables'; CACHE=ROOT/'cache'; QA=ROOT/'qa'
for d in [OUT,CACHE,QA]: d.mkdir(parents=True,exist_ok=True)

def patch(pix,extra=0):
    lo=np.maximum(np.floor(pix.min(0)).astype(int)-extra,0); hi=np.minimum(np.ceil(pix.max(0)).astype(int)+extra,S-1)
    x0,y0=lo; x1,y1=hi
    if x1<x0 or y1<y0:return None
    yy,xx=np.mgrid[y0:y1+1,x0:x1+1]
    return (int(x0),int(y0),int(x1),int(y1)),xx,yy

def bary(pix,xx,yy):
    (ax,ay),(bx,by),(cx,cy)=pix; den=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
    if abs(den)<1e-12:return None
    a=((by-cy)*(xx-cx)+(cx-bx)*(yy-cy))/den
    b=((cy-ay)*(xx-cx)+(ax-cx)*(yy-cy))/den
    return a,b,1-a-b

def cover_square(pix,xx,yy):
    ok=np.ones(xx.shape,bool)
    for axis in [[1.,0.],[0.,1.]]+[[-(pix[(i+1)%3,1]-pix[i,1]),pix[(i+1)%3,0]-pix[i,0]] for i in range(3)]:
        axis=np.asarray(axis); p=pix@axis; q=xx*axis[0]+yy*axis[1]
        ok &= (q+max(0,axis[0])+max(0,axis[1])>=p.min()-1e-8)&(q+min(0,axis[0])+min(0,axis[1])<=p.max()+1e-8)
    return ok

def select(v,parts):
    p=parts['Opaque']; t=v[p['f']]; n,area=geom(t)
    cap=(n[:,2]>.9999)&(abs(t[:,:,2]-46.872).max(1)<.0002)
    edges=defaultdict(list)
    for i,f in enumerate(p['f']):
        for j in range(3):edges[tuple(sorted([int(f[j]),int(f[(j+1)%3])]))].append(i)
    sides=np.zeros(len(t),bool); frontier=deque(np.flatnonzero(cap).tolist()); visited=cap.copy()
    while frontier:
        i=frontier.popleft()
        for j in range(3):
            for k in edges[tuple(sorted([int(p['f'][i,j]),int(p['f'][i,(j+1)%3])]))]:
                if not visited[k] and abs(n[k,2])<.30 and t[k,:,2].max()>4.6:
                    visited[k]=True;sides[k]=True;frontier.append(k)
    # Directed oriented edges of the actual union of upward wall-cap triangles.
    boundary=[]
    for i in np.flatnonzero(cap):
        f=p['f'][i]
        for j in range(3):
            ids=edges[tuple(sorted([int(f[j]),int(f[(j+1)%3])]))]
            if sum(cap[k] for k in ids)==1:boundary.append((int(f[j]),int(f[(j+1)%3])))
    nex=defaultdict(list)
    for a,b in boundary:nex[a].append(b)
    unused=set(boundary); loops=[]
    while unused:
        a,b=min(unused); start=a; path=[a];unused.remove((a,b))
        for _ in range(len(boundary)+1):
            path.append(b)
            if b==start:break
            choices=[c for c in nex[b] if (b,c) in unused]
            if not choices:break
            a,b=b,choices[0];unused.remove((a,b))
        if path[-1]==path[0]:loops.append(v[np.array(path),:2])
    return cap,sides,n,area,loops

def prepare():
    tic=time.time();v,u,parts=parse_obj(OBJ);cap,sides,n,a,loops=select(v,parts)
    p=parts['Opaque'];np.savez_compressed(CACHE/'face_selection.npz',cap=cap,sides=sides)
    # Sample only real cap boundary paths, keeping physical arclength per loop.
    points=[];arcs=[];loopids=[];lengths=[]
    for lid,poly in enumerate(loops):
        lens=np.linalg.norm(np.diff(poly,axis=0),axis=1); L=float(lens.sum());lengths.append(L);off=0.
        for p0,p1,ll in zip(poly[:-1],poly[1:],lens):
            k=max(1,int(np.ceil(ll/.20)));r=np.arange(k)/k
            points.extend(p0[None]+r[:,None]*(p1-p0));arcs.extend(off+r*ll);loopids.extend([lid]*k);off+=ll
    tree=cKDTree(np.array(points));arcs=np.array(arcs);loopids=np.array(loopids,np.int16);lengths=np.array(lengths)
    # Excluded surface pixel-square union veto, including floors, furniture,
    # glazing, eyelets and all fireplace faces. No bounding-box masks.
    forbidden=np.zeros((S,S),bool)
    for name,pr in parts.items():
        ids=np.flatnonzero(~cap) if name=='Opaque' else np.arange(len(pr['f']))
        for i in ids:
            pix=u[pr['ft'][i]]*[S,-S]+[0,S]; q=patch(pix)
            if q is None:continue
            (x0,y0,x1,y1),xx,yy=q
            forbidden[y0:y1+1,x0:x1+1] |= cover_square(pix,xx,yy)
        print('Excluded class rasterized',name,len(ids),flush=True)
    alpha=np.zeros((S,S),np.float32);wx=np.zeros((S,S),np.float32);wy=np.zeros((S,S),np.float32)
    side_mask=np.zeros((S,S),np.uint8)
    for i in np.flatnonzero(cap|sides):
        pix=u[p['ft'][i]]*[S,-S]+[0,S];q=patch(pix)
        if q is None:continue
        (x0,y0,x1,y1),xx,yy=q;w=bary(pix,xx+.5,yy+.5)
        if w is None:continue
        aa,bb,cc=w;inside=(aa>=-1e-8)&(bb>=-1e-8)&(cc>=-1e-8);sl=np.s_[y0:y1+1,x0:x1+1]
        if sides[i]:side_mask[sl][inside]=255;continue
        # 4x4 exact triangle coverage, unioned across all cap faces.
        coverage=np.zeros(xx.shape,np.float32)
        for dx in [.125,.375,.625,.875]:
            for dy in [.125,.375,.625,.875]:
                A,B,C=bary(pix,xx+dx,yy+dy);coverage+=((A>=-1e-8)&(B>=-1e-8)&(C>=-1e-8))/16
        # Adjacent triangles partition a cap pixel: add their subpixel coverage
        # to avoid a dark diagonal seam through an otherwise continuous cap.
        alpha[sl]=np.minimum(1.,alpha[sl]+coverage)
        t=v[p['f'][i]];W=aa[:,:,None]*t[0]+bb[:,:,None]*t[1]+cc[:,:,None]*t[2]
        valid=coverage>0;wx[sl][valid]=W[:,:,0][valid];wy[sl][valid]=W[:,:,1][valid]
    alpha[forbidden]=0
    raw=alpha>0
    # Copy edge colours four atlas pixels into empty gutters only. Excluded
    # triangle pixel-square coverage is always vetoed, including AA edges.
    dist,inds=distance_transform_edt(~raw,return_indices=True)
    pad=(dist<=4)&(~raw)&(~forbidden)
    wx[pad]=wx[inds[0][pad],inds[1][pad]];wy[pad]=wy[inds[0][pad],inds[1][pad]]
    # Gutter alpha copies the true edge alpha; no UV border tracing is drawn.
    alpha[pad]=alpha[inds[0][pad],inds[1][pad]]
    active=alpha>0;flat=np.flatnonzero(active);xy=np.column_stack([wx.ravel()[flat],wy.ravel()[flat]])
    d,near=tree.query(xy,workers=2); lid=loopids[near]; L=lengths[lid];s=arcs[near]
    np.savez_compressed(CACHE/'effect_samples.npz',flat=flat,alpha=alpha.ravel()[flat],distance=d.astype(np.float32),arc=s.astype(np.float32),lid=lid,length=L.astype(np.float32))
    np.save(CACHE/'forbidden.npy',forbidden);np.save(CACHE/'cap_raw.npy',raw)
    Image.fromarray(np.uint8(np.clip(alpha*255,0,255))).save(OUT/'UV02_WallCaps_Selection_8192.png')
    Image.fromarray(side_mask).save(OUT/'UV02_WallSides_DIAGNOSTIC_8192.png')
    Image.fromarray(np.uint8(forbidden)*255).save(QA/'Excluded_Triangle_Square_Coverage_8192.png')
    pathrows=[{'id':i,'length_mm':float(lengths[i]),'vertices_xy_mm':poly.tolist()} for i,poly in enumerate(loops)]
    (OUT/'Wall_Outline_Paths.json').write_text(json.dumps(pathrows,indent=2))
    report={'receiver_sha256':sha(OBJ),'scope':'Full-height opaque architectural wall caps seeded at Z46.872mm; adjoining wall sides diagnostic only. Shorter partitions, furniture, fireplace, glass, floor, hanging accessories and undersides excluded.',
      'cap_faces':int(cap.sum()),'cap_area_mm2':float(a[cap].sum()),'side_faces':int(sides.sum()),'side_area_mm2':float(a[sides].sum()),'physical_path_loops':len(loops),'closed_path_edges':sum(len(q)-1 for q in loops),'raw_cap_texels':int(raw.sum()),'gutter_texels':int(pad.sum()),'forbidden_active_overlap':int((active&forbidden).sum()),'elapsed_seconds':time.time()-tic,
      'projection_assumption':'+Z orthographic/front normal to model floor XY. Production caps only; vertical faces have zero incidence and are not promised visible. No physical alignment, MadMapper playback or projector test.'}
    (QA/'Mask_QA.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)

def colours(q,t):
    L=q['length'];lid=q['lid'];phase=(t/DURATION + lid*.173)%1
    signed=(q['arc']-phase*L+L/2)%L-L/2
    # Comets use wrapped Gaussian arclength fields, fully periodic in time.
    sig=np.minimum(180.,L*.14)
    tail=sum(np.exp(-((signed+sig*.6+k*L)/np.maximum(sig,1.))**2/2) for k in [-1,0,1])
    hs=np.maximum(2.,np.minimum(15.,L*.04))
    head=sum(np.exp(-((signed+k*L)/hs)**2/2) for k in [-1,0,1])
    across=np.exp(-(q['distance']/.95)**2/2)
    blue=np.array([5.,42.,86.])[None,:]+tail[:,None]*np.array([0.,82.,140.])[None,:]*across[:,None]
    cyan=head[:,None]*across[:,None]*np.array([70.,200.,190.])[None,:]
    goldphase=(t/DURATION*1+lid*.317+.42)%1
    gd=(q['arc']-goldphase*L+L/2)%L-L/2
    gs=np.maximum(2.,np.minimum(12.,L*.03))
    gold=sum(np.exp(-((gd+k*L)/gs)**2/2) for k in [-1,0,1])*across*((lid%7==0)&(L>70))
    rgb=(blue+cyan)*(1-.8*gold[:,None])+gold[:,None]*np.array([180.,112.,20.])[None,:]
    return np.uint8(np.clip(rgb*q['alpha'][:,None],0,255))

def make_atlas(q,t):
    im=np.zeros((S*S,3),np.uint8);im[q['flat']]=colours(q,t);return im.reshape(S,S,3)

def mapped(atlas):
    # Read-only published UV02 nearest-neighbour camera cache; full model occlusion.
    own=ROOT/'camera_mapping.npz'
    if own.exists():
        cam=np.load(own);U=cam['u'];V=cam['v'];M=cam['material']
    else:
        c=ORIGINAL_SRC.parent/'cache/top';U=np.load(c/'u.npy');V=np.load(c/'v.npy');M=np.load(c/'material.npy')
    xx=np.clip(np.floor(U*S).astype(int),0,S-1);yy=np.clip(np.floor((1-V)*S).astype(int),0,S-1)
    out=np.zeros((*M.shape,3),np.uint8);ok=M>0;out[ok]=atlas[yy[ok],xx[ok]]
    return np.asarray(Image.fromarray(out).resize((1024,786),Image.Resampling.LANCZOS))

def qa():
    q=dict(np.load(CACHE/'effect_samples.npz'));forbid=np.load(CACHE/'forbidden.npy',mmap_mode='r');checks=[]
    # A separate read-only face-barycentric sampling check on all excluded faces.
    v,u,parts=parse_obj(OBJ);cap=np.load(CACHE/'face_selection.npz')['cap']
    probes=[]
    for name,p in parts.items():
        ix=np.flatnonzero(~cap) if name=='Opaque' else np.arange(len(p['f']))
        for weights in [[1/3]*3,[.8,.1,.1],[.1,.8,.1],[.1,.1,.8],[.49,.49,.02],[.49,.02,.49],[.02,.49,.49]]:
            uv=(u[p['ft'][ix]]*np.array(weights)[None,:,None]).sum(1)
            probes.append((name,np.clip(np.floor((1-uv[:,1])*S).astype(int),0,S-1),np.clip(np.floor(uv[:,0]*S).astype(int),0,S-1)))
    mask=np.asarray(Image.open(OUT/'UV02_WallCaps_Selection_8192.png').convert('L'));Image.fromarray(mapped(np.repeat(mask[:,:,None],3,axis=2))).save(OUT/'WallCaps_Static_FrontNormal_Mapped_1024.png')
    for i,t in enumerate([0.,2.5,5.,7.5]):
        a=make_atlas(q,t);path=OUT/f'Tron_UV02_QA_Atlas_{i:02d}_8192.png';Image.fromarray(a).save(path)
        Image.fromarray(mapped(a)).save(OUT/f'Tron_QA_FrontNormal_Mapped_{i:02d}_1024.png')
        classes={}
        for name,yy,xx in probes:classes[name]=max(classes.get(name,0),int(a[yy,xx].max(initial=0)))
        checks.append({'time_seconds':t,'max_excluded_texel_RGB':int(a[forbid].max(initial=0)),'excluded_barycentric_samples_max_RGB':classes})
    looperr=int(np.abs(colours(q,0).astype(int)-colours(q,DURATION).astype(int)).max())
    stats={'representative_frames':checks,'loop_time_0_vs_10_max_RGB_difference':looperr,'excluded_samples_per_frame':sum(len(x[1]) for x in probes),'all_pass':all(c['max_excluded_texel_RGB']==0 and max(c['excluded_barycentric_samples_max_RGB'].values())==0 for c in checks) and looperr==0}
    (QA/'Representative_Frame_QA.json').write_text(json.dumps(stats,indent=2));assert stats['all_pass'];print(json.dumps(stats),flush=True)

def encode():
    q=dict(np.load(CACHE/'effect_samples.npz'));N=int(FPS*DURATION)
    atlaspath=OUT/'Tron_WallCaps_UV02_Atlas_8192_10s24_Lossless.mov'
    viewpath=OUT/'Tron_WallCaps_UV02_FrontNormal_Mapped_1024_10s24.mp4'
    common=[str(FFMPEG),'-y','-loglevel','warning','-f','rawvideo','-pix_fmt','rgb24','-r',str(FPS)]
    # qtrle keeps exact black exclusions and full RGB; no subsampled colour bleed.
    a=subprocess.Popen(common+['-s',f'{S}x{S}','-i','pipe:0','-an','-c:v','qtrle','-pix_fmt','rgb24',str(atlaspath)],stdin=subprocess.PIPE,stderr=(QA/'atlas_encode.log').open('w'))
    b=subprocess.Popen(common+['-s','1024x786','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(viewpath)],stdin=subprocess.PIPE,stderr=(QA/'preview_encode.log').open('w'))
    tic=time.time();activity=[]
    for i in range(N):
        frame=make_atlas(q,i/FPS); view=mapped(frame);a.stdin.write(frame.tobytes());b.stdin.write(view.tobytes())
        if i%24==0:activity.append({'frame':i,'visible_nonzero_pixels':int((view.max(2)>10).sum())});print('ENCODE',i,'/',N,'elapsed',round(time.time()-tic,1),flush=True)
    a.stdin.close();b.stdin.close();assert a.wait()==0;assert b.wait()==0
    (QA/'Encode_Progress.json').write_text(json.dumps({'frames':N,'seconds':DURATION,'fps':FPS,'elapsed_seconds':time.time()-tic,'activity':activity},indent=2));print('ENCODE COMPLETE',atlaspath.stat().st_size,viewpath.stat().st_size,flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['prepare','qa','encode']);args=ap.parse_args();globals()[args.mode]()
