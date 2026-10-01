import numpy as np
def write_stl(h,pitch,path):
 ny,nx=h.shape;n=np.zeros((ny+1,nx+1),np.float32)
 for dy,dx in [(0,0),(0,1),(1,0),(1,1)]:n[dy:dy+ny,dx:dx+nx]=np.maximum(n[dy:dy+ny,dx:dx+nx],h)
 verts=[];faces=[];ids={};active=h>0
 def vertex(x,y,top):
  key=(int(x),int(y),top)
  if key not in ids:ids[key]=len(verts);verts.append((x*pitch,y*pitch,float(n[y,x]) if top else 0.))
  return ids[key]
 def quad(q):faces.extend([(q[0],q[1],q[2]),(q[0],q[2],q[3])])
 for y,x in zip(*np.where(active)):
  c=[(x,y),(x+1,y),(x+1,y+1),(x,y+1)];top=[vertex(*v,1) for v in c];bot=[vertex(*v,0) for v in c];quad(top);quad(bot[::-1])
  for j,(dy,dx) in enumerate([(-1,0),(0,1),(1,0),(0,-1)]):
   yy=y+dy;xx=x+dx
   if not(0<=yy<ny and 0<=xx<nx and active[yy,xx]):k=(j+1)%4;quad([top[j],bot[j],bot[k],top[k]])
 v=np.array(verts,np.float32);f=np.array(faces,np.int32);tri=v[f];norm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);norm/=np.linalg.norm(norm,axis=1)[:,None]
 rec=np.zeros(len(f),dtype=[('n','<f4',3),('v','<f4',(3,3)),('a','<u2')]);rec['n']=norm;rec['v']=tri
 with path.open('wb') as fh:fh.write(b'Campus Center print model, millimetres'.ljust(80,b' '));fh.write(np.uint32(len(f)).tobytes());rec.tofile(fh)
 return {'dimensions_mm':(v.max(0)-v.min(0)).tolist(),'triangles':len(f)}
