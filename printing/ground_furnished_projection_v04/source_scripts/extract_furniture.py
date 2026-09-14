import bpy, pathlib, hashlib, json, numpy as np
from mathutils import Vector
R=pathlib.Path(__file__).parent
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
source=R.parent/'projection_print_v03/Campus_Center_Detailed_Projection.blend'
sha=hashlib.sha256(source.read_bytes()).hexdigest()
deps=bpy.context.evaluated_depsgraph_get()
accepted=[];omitted=[];triangles=[];owners=[]
for o in s.objects:
    if o.type!='MESH' or o.hide_render:continue
    n=o.name.lower();cols=[c.name for c in o.users_collection]
    reason=None
    if n.startswith(('receiver ','student_','loop occupant')):reason='existing shell or people'
    elif any('artwork' in c.lower() or c.startswith('AV -') for c in cols):reason='artwork or suspended AV'
    elif 'V03 PROJECTED DETAIL - floor content only' in cols:
        if not any(t in n for t in ['bench','bleacher','scorer','changing bench','locker top','ceramic pot']):reason='projection-only surface detail'
    elif any(t in n for t in ['frame ','tape ','poster','flame','glass','glazing','partition_header','exhaust','vent louver','fittings','accessories','keyboard','mouse','nozzle','spool','filament','gantry','z screw','touchscreen','ui readout','ink label','label','loading slide','platen','control button','net cord','hoop','backboard','stanchion']):reason='fragile, internal or suspended detail'
    points=[o.matrix_world@Vector(p) for p in o.bound_box]
    lo=np.min([list(p) for p in points],axis=0);hi=np.max([list(p) for p in points],axis=0)
    if lo[2]>3.6 or hi[2]<.08:reason='not ground-floor furniture'
    if reason:omitted.append({'name':o.name,'reason':reason});continue
    ev=o.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles()
    vv=np.array([list(ev.matrix_world@v.co) for v in me.vertices],dtype=np.float32)
    tt=np.array([t.vertices for t in me.loop_triangles],dtype=np.int32)
    if len(tt):
        tris=vv[tt];cross=np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0]);valid=np.abs(cross[:,2])>1e-9;tris=tris[valid]
        # Both face windings count: vertical filling is based on the visible envelope.
        idx=len(accepted);triangles.append(tris);owners.append(np.full(len(tris),idx,dtype=np.int32))
        accepted.append({'name':o.name,'collections':cols,'bounds_m':[lo.tolist(),hi.tolist()],'triangles':len(tris)})
    ev.to_mesh_clear()
np.savez_compressed(R/'furniture_surfaces.npz',triangles=np.concatenate(triangles),owners=np.concatenate(owners))
(R/'furniture_source.json').write_text(json.dumps({'source':str(source),'source_sha256':sha,'blender_version':bpy.app.version_string,'objects':accepted,'omitted':omitted,'triangle_count':sum(r['triangles'] for r in accepted),'transform':'print_mm = (world_m - (-47, -2.3, -0.42)) / 0.0875','source_unchanged':hashlib.sha256(source.read_bytes()).hexdigest()==sha},indent=2))
print('EXTRACTED',len(accepted),sum(r['triangles'] for r in accepted),flush=True)
