import bpy,bmesh,json,math,subprocess,numpy as np
from pathlib import Path
from mathutils import Vector
root=Path(__file__).parent;out=root/'cleaned'
bpy.ops.wm.open_mainfile(filepath=str(out/'SilverCup.blend'))
body=bpy.data.objects['Trophy_SilverCup_LOD0'];silver=bpy.data.materials['Clean_Polished_Silver']
for name in ['Trophy_SilverCup_LOD1','Trophy_SilverCup_LOD2']:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
bm=bmesh.new();bm.from_mesh(body.data)
knots=[(.157,.011),(.17,.018),(.19,.028),(.21,.035),(.24,.043),(.27,.0475),(.296,.049)]
def radius(z):return float(np.interp(z,[p[0] for p in knots],[p[1] for p in knots]))
discard=[]
for f in bm.faces:
    p=f.calc_center_median()
    if .158<p.z<.298 and not (abs(p.y)<.009 and abs(p.x)>radius(p.z)+.001):discard.append(f)
bmesh.ops.delete(bm,geom=discard,context='FACES')
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
bm.to_mesh(body.data);bm.free()
np.savez(out/'trim_repair.npz',vertices=np.array([v.co[:] for v in body.data.vertices]),faces=np.array([p.vertices[:] for p in body.data.polygons]))
embedded='T:/AI/Comfy2601/ComfyUI/ComfyUI_TRELLIS2_portable/python_embeded/python.exe'
subprocess.run([embedded,'-s',str(root/'repair_meshlib.py'),str(out/'trim_repair.npz'),'25000'],check=True)
data=np.load(out/'trim_repair_repaired.npz');mesh=bpy.data.meshes.new('Trellis_Handles_Rim_Stem_Repaired');mesh.from_pydata(data['vertices'].tolist(),[],data['faces'].tolist());mesh.update();body.data=mesh;mesh.materials.append(silver)
# Cross-section: outer base -> outer bowl -> lip -> inner bowl -> solid inner floor.
profile=[(0,.157),(.011,.157),(.018,.170),(.028,.190),(.035,.210),(.043,.240),(.0475,.270),(.049,.296),(.049,.302),(.0475,.302),(.0475,.296),(.046,.270),(.0415,.240),(.0335,.210),(.0265,.190),(.0165,.173),(.010,.164),(0,.164)]
verts=[];rings=[];faces=[];segments=128
for r,z in profile:
    if r==0:rings.append([len(verts)]);verts.append((0,0,z))
    else:
        ring=[]
        for i in range(segments):ring.append(len(verts));a=2*math.pi*i/segments;verts.append((r*math.cos(a),r*math.sin(a),z))
        rings.append(ring)
for a,b in zip(rings[:-1],rings[1:]):
    for i in range(segments):
        j=(i+1)%segments
        if len(a)==1:faces.append((a[0],b[j],b[i]))
        elif len(b)==1:faces.append((a[i],a[j],b[0]))
        else:faces.append((a[i],a[j],b[j],b[i]))
bowlmesh=bpy.data.meshes.new('Manual_Profile_Bowl');bowlmesh.from_pydata(verts,[],faces);bowlmesh.update();bowlmesh.materials.append(silver)
bowl=bpy.data.objects.new('Manual_Profile_Bowl',bowlmesh);bpy.context.collection.objects.link(bowl)
for p in bowlmesh.polygons:p.use_smooth=True
bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bowl.select_set(True);bpy.context.view_layer.objects.active=body;bpy.ops.object.join()
bm=bmesh.new();bm.from_mesh(body.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(body.data);bm.free()
for p in body.data.polygons:p.use_smooth=True
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=1.15,island_margin=.012);bpy.ops.object.mode_set(mode='OBJECT')
body['provenance']='Trellis.2 retained handles/rim/stem; bowl manually rebuilt from measured profile; plinth and blank plate rebuilt. Hybrid cleanup, raw originals archived.'
body['finish']='Clean silver PBR; original baked maps preserved separately; cleaned hybrid uses new UVs'
lodcol=bpy.data.collections['LOD Alternatives - hidden']
for lod,target in [(1,12000),(2,4500)]:
    np.savez(out/('hybrid_lod'+str(lod)+'.npz'),vertices=np.array([v.co[:] for v in body.data.vertices]),faces=np.array([p.vertices[:] for p in body.data.polygons]))
    subprocess.run([embedded,'-s',str(root/'repair_meshlib.py'),str(out/('hybrid_lod'+str(lod)+'.npz')),str(target)],check=True)
    data=np.load(out/('hybrid_lod'+str(lod)+'_repaired.npz'));m=bpy.data.meshes.new('HybridCup_LOD'+str(lod));m.from_pydata(data['vertices'].tolist(),[],data['faces'].tolist());m.update();m.materials.append(silver)
    duplicate=bpy.data.objects.new('Trophy_SilverCup_LOD'+str(lod),m);lodcol.objects.link(duplicate)
    bpy.ops.object.select_all(action='DESELECT');duplicate.select_set(True);bpy.context.view_layer.objects.active=duplicate
    for p in m.polygons:p.use_smooth=True
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=1.15,island_margin=.012);bpy.ops.object.mode_set(mode='OBJECT');duplicate.hide_set(True);duplicate.hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=str(out/'SilverCup.blend'))
(out/'hybrid_cleanup.json').write_text(json.dumps({'manual_bowl_profile_radius_z_m':profile,'retained_trellis_parts':['handles','rim','stem','foot'],'discarded_defective_bowl_faces':len(discard),'source_archived':'prototypes/cup.blend; cup_raw.npz; cup_trellis_raw.glb','new_uvs':'Smart project; original UVs/materials retained in raw assets and baked map archive'},indent=2))
print('HYBRID REBUILD COMPLETE')
