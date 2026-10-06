from pathlib import Path
import json, hashlib, sys, collections, math
import numpy as np
R=Path(__file__).parent; V=R/'madmapper_p02';D=V/'deliverables';D.mkdir(parents=True,exist_ok=True)
SOURCE=R/'print_revision02/deliverables'
def parse_obj(path):
 vs=[];uv=[];norm=[];parts={};name=None
 for line in Path(path).read_text().splitlines():
  row=line.split()
  if not row:continue
  if row[0]=='v':vs.append([float(x) for x in row[1:4]])
  elif row[0]=='vt':uv.append([float(x) for x in row[1:3]])
  elif row[0]=='vn':norm.append([float(x) for x in row[1:4]])
  elif row[0]=='o':name=row[1];parts.setdefault(name,{'f':[],'ft':[],'fn':[]})
  elif row[0]=='f':
   q=[[int(x)-1 if x else -1 for x in s.split('/')] for s in row[1:]]
   assert len(q)==3
   parts[name]['f'].append([x[0] for x in q]);parts[name]['ft'].append([x[1] for x in q]);parts[name]['fn'].append([x[2] for x in q])
 for p in parts.values():
  for k in p:p[k]=np.asarray(p[k],np.int32)
 return np.asarray(vs,np.float64),np.asarray(uv,np.float64),np.asarray(norm,np.float64),parts
def geom(v,f):
 t=v[f];cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);length=np.linalg.norm(cross,axis=1)
 return t.mean(1),cross/np.maximum(length[:,None],1e-30),length/2
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
