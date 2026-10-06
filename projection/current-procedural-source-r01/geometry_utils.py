from pathlib import Path
import sys,json,hashlib,collections
import numpy as np
R=Path(__file__).parent;sys.path.insert(0,str(R/'reused_packages'))
import trimesh,manifold3d as mf

def rotation(r):
 roll,pitch,yaw=np.radians(r);sr,sp,sy=np.sin([roll,pitch,yaw]);cr,cp,cy=np.cos([roll,pitch,yaw])
 return np.array([[cp*cy,cp*sy,sp],[sr*sp*cy-cr*sy,sr*sp*sy+cr*cy,-sr*cp],[-cr*sp*cy-sr*sy,cy*sr-cr*sp*sy,cr*cp]])

def actor_mesh(a):
 fn=R/'native_meshes'/(hashlib.sha1(a['mesh'].encode()).hexdigest()[:16]+'.json')
 d=json.loads(fn.read_text());ids=np.array(list(map(int,d['vertices'])));v=np.zeros((int(ids.max())+1,3));v[ids]=list(d['vertices'].values());f=np.array(d['faces'],int);mat=np.array(d['material_ids'],int)
 t=a['transform'] or [a['actor_transform']['location'],a['actor_transform']['rotation'],a['actor_transform']['scale']]
 v=(v*np.array(t[2])*d['build_scale3d'])@rotation(t[1])+t[0]
 expected=np.array(a['bounds_cm']);actual=np.array([v[ids].min(0),v[ids].max(0)])
 # Bounds are actor AABBs, which may use rotated mesh local AABB rather than exact triangle extrema.
 excess=max(float((expected[0]-actual[0]).max()),float((actual[1]-expected[1]).max()))
 assert excess<.05,(a['label'],'world transform does not fit native actor bounds',excess)
 # UE SOURCE triangles use clockwise winding. Reflect Y to the Blender/print
 # right-handed frame; that reflection makes the existing winding outward.
 v[:,1]*=-1
 m=trimesh.Trimesh(vertices=v,faces=f,process=False);norm=np.cross(m.triangles[:,1]-m.triangles[:,0],m.triangles[:,2]-m.triangles[:,0]);good=np.linalg.norm(norm,axis=1)>1e-6
 m.update_faces(good);mat=mat[good];m.merge_vertices(digits_vertex=4)
 return m,mat,d,{'bounds_excess_cm':excess,'native_bounds_cm':expected.tolist(),'triangle_bounds_cm':actual.tolist()}

def components(mesh):
 # Vertex adjacency suffices for source component inventory. Shared edges are independently checked in QA.
 n=len(mesh.vertices);parent=np.arange(n)
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for tri in mesh.faces:
  x=find(int(tri[0]))
  for y in tri[1:]:
   y=find(int(y))
   if x!=y:parent[y]=x
 groups=collections.defaultdict(list)
 for i,tri in enumerate(mesh.faces):groups[find(int(tri[0]))].append(i)
 return list(groups.values())

def shells(m):
 counts={};bad=0;start=0;out=[]
 for i,t in enumerate(m.faces):
  for a,b in zip(t,np.roll(t,-1)):
   k=tuple(sorted((int(a),int(b))));old=counts.get(k,0);new=old+1
   if old and old!=2:bad-=1
   if new!=2:bad+=1
   counts[k]=new
  if bad==0:
   out.append(list(range(start,i+1)));start=i+1;counts={}
 if start<len(m.faces):out.extend([[j for j in c if j>=start] for c in components(m) if any(j>=start for j in c)])
 return out

def solid(mesh):
 return mf.Manifold(mf.Mesh64(np.round(np.asarray(mesh.vertices,np.float64),4),np.asarray(mesh.faces,np.uint64)))
def mesh(man):
 q=man.to_mesh64();return trimesh.Trimesh(np.asarray(q.vert_properties)[:,:3],np.asarray(q.tri_verts),process=True)
def box(lo,hi):return mf.Manifold.cube(tuple(np.array(hi)-lo)).translate(tuple(lo))
def union(xs):return mf.Manifold.batch_boolean(xs,mf.OpType.Add) if xs else mf.Manifold()

def submesh(m,mask):return m.submesh([mask],append=True,repair=False)

def qa(man,label):
 m=mesh(man);edges=np.sort(m.edges,axis=1);_,cnt=np.unique(edges,axis=0,return_counts=True)
 assert len(m.faces)>0 and m.is_watertight and m.is_winding_consistent and (cnt==2).all(),(label,m.is_watertight,m.is_winding_consistent,dict(zip(*np.unique(cnt,return_counts=True))))
 assert man.status()==mf.Error.NoError and man.volume()>0,label
 return {'label':label,'watertight':True,'winding_consistent':True,'nonmanifold_edges':int((cnt!=2).sum()),'components':len(man.decompose()),'vertices':len(m.vertices),'triangles':len(m.faces),'bounds_mm':m.bounds.tolist(),'dimensions_mm':m.extents.tolist(),'volume_mm3':float(m.volume)}
