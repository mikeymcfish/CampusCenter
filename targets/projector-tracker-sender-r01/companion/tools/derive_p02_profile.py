"""Read-only exact sample registration/footprint extraction; no third-party packages."""
from pathlib import Path
from collections import Counter,defaultdict
import hashlib,json

SOURCE=Path(__import__('os').environ['CC_P02_SOURCE_DIR'])
OUT=Path(__file__).resolve().parents[1]/'profiles'
obj=SOURCE/'Ground_R29_P02_Sample_1_250.obj'
verts=[];bottom=[]
for line in obj.read_text().splitlines():
    if line.startswith('v '):verts.append(tuple(map(float,line.split()[1:4])))
    elif line.startswith('f '):
        f=[int(t.split('/')[0])-1 for t in line.split()[1:]]
        if len(f)==3 and all(abs(verts[i][2])<1e-7 for i in f):bottom.append(f)
assert bottom,'No foundation underside faces'
edges=Counter(tuple(sorted((a,b))) for f in bottom for a,b in zip(f,f[1:]+f[:1]))
boundary=[e for e,c in edges.items() if c==1]
adj=defaultdict(list)
for a,b in boundary:adj[a].append(b);adj[b].append(a)
assert all(len(v)==2 for v in adj.values()),'Footprint not a closed manifold boundary'
seen=set();loops=[]
for start in adj:
    if start in seen:continue
    loop=[];prev=None;cur=start
    while cur not in seen:
        seen.add(cur);loop.append(cur)
        nxt=next(a for a in adj[cur] if a!=prev);prev,cur=cur,nxt
    assert cur==start
    loops.append(loop)
polygons=[];areas=[]
for loop in loops:
    points=[verts[i][:2] for i in loop]
    # Remove only exactly collinear intermediate points; retain all stair-step corners.
    while True:
        slim=[]
        for i,b in enumerate(points):
            a=points[i-1];c=points[(i+1)%len(points)]
            cross=(b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0])
            if abs(cross)>1e-9:slim.append(b)
        if len(slim)==len(points):break
        points=slim
    areas.append(abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1])))/2)
    polygons.append(points)
land=json.loads((SOURCE/'Calibration_Landmarks.json').read_text())['landmarks']
landpoints=[dict(X=l['assembly_xyz_mm'][0]*.4,Y=l['assembly_xyz_mm'][1]*.4) for l in land]
p={'Id':'campuscenter-r29-p02-sample-1-250-v1','MinX':4.48,'MinY':2.72,'MaxX':267.84,'MaxY':199.52,
   'FootprintLoops':[[dict(X=x,Y=y) for x,y in points] for points in polygons],'Landmarks':landpoints,'LandmarkIds':[l['id'] for l in land],
   'SourceSha256':hashlib.sha256(obj.read_bytes()).hexdigest()}
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'p02-sample-1-250.json').write_text(json.dumps(p,indent=2))
audit={'source':str(obj),'source_sha256':p['SourceSha256'],'sample_scale':250,
 'world_cm_to_model_mm':{'x':'(worldX+4700)/25','y':'(-worldY+230)/25'},
 'origin_world_cm':[-4700,230],'source_bounds_mm':[[4.48,2.72,0],[267.84,199.52,19.0688]],
 'footprint_method':'exact z=0 foundation underside triangle boundary; only collinear vertices removed',
 'bottom_triangles':len(bottom),'boundary_loops':len(loops),'footprint_points':[len(p) for p in polygons],'loop_absolute_areas_mm2':areas,
 'footprint_fill_rule':'even-odd across all exact boundary loops; retains holes and disconnected pieces',
 'bounds_area_mm2':263.36*196.8,'landmarks_method':'inherited 1:100 XY landmarks times 0.4; independently equal world formula; landmarks near wall edges remain reference, physically verify',
 'registration_verified':all(abs(q['X']-(l['UE_world_cm'][0]+4700)/25)<1e-7 and abs(q['Y']-(-l['UE_world_cm'][1]+230)/25)<1e-7 for q,l in zip(landpoints,land)),
 'physical_projection_tested':False}
(OUT/'P02_REGISTRATION_AUDIT.json').write_text(json.dumps(audit,indent=2))
print(json.dumps(audit,indent=2))
