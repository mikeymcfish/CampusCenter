from pathlib import Path
import numpy as np, json, hashlib, collections

ROOT=Path(__file__).resolve().parents[1]
ORIGINAL_SRC=ROOT/'receiver_copy'
SRC=ROOT/'receiver_copy' if (ROOT/'receiver_copy/CampusCenter_P02plusP03B3_Assembly_1_100_UV02.obj').exists() else ORIGINAL_SRC
OBJ=SRC/'CampusCenter_P02plusP03B3_Assembly_1_100_UV02.obj'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def parse_obj(p):
    vs=[]; us=[]; parts={}; name=None
    for line in Path(p).read_text().splitlines():
        q=line.split()
        if not q: continue
        if q[0]=='v': vs.append([float(x) for x in q[1:4]])
        elif q[0]=='vt': us.append([float(x) for x in q[1:3]])
        elif q[0]=='o': name=q[1]; parts[name]={'f':[],'ft':[]}
        elif q[0]=='f':
            r=[[int(x)-1 for x in t.split('/')[:2]] for t in q[1:]]
            assert len(r)==3
            parts[name]['f'].append([x[0] for x in r]); parts[name]['ft'].append([x[1] for x in r])
    for p in parts.values():
        for k in p: p[k]=np.array(p[k],np.int32)
    return np.array(vs),np.array(us),parts
def geom(t):
    c=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]); l=np.linalg.norm(c,axis=1)
    return c/np.maximum(l[:,None],1e-30), l/2

if __name__=='__main__':
    ROOT.mkdir(exist_ok=True); (ROOT/'qa').mkdir(exist_ok=True)
    v,u,parts=parse_obj(OBJ); report={'source':str(OBJ),'sha256':sha(OBJ),'bounds':[v.min(0).tolist(),v.max(0).tolist()],'parts':{}}
    for name,p in parts.items():
        t=v[p['f']]; n,a=geom(t); top=(n[:,2]>.999); vert=abs(n[:,2])<.001
        heights=collections.defaultdict(lambda:[0,0.])
        for z,ar in zip(np.round(t[top].mean(1)[:,2],3),a[top]): heights[float(z)][0]+=1; heights[float(z)][1]+=float(ar)
        vz=collections.defaultdict(lambda:[0,0.])
        for z,ar in zip(np.round(t[vert].max(1)[:,2],3),a[vert]): vz[float(z)][0]+=1; vz[float(z)][1]+=float(ar)
        report['parts'][name]={'faces':len(t),'top_heights_by_area':sorted(heights.items(),key=lambda x:-x[1][1])[:35],'vertical_max_heights_by_area':sorted(vz.items(),key=lambda x:-x[1][1])[:35]}
    (ROOT/'qa/Receiver_Inspection.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
