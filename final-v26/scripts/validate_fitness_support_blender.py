import bpy,pathlib,json,hashlib
from mathutils import Vector
R=pathlib.Path('C:/Users/mikef/Documents/Codex/2026-09-30/task/CampusCenter-new-plans');D=R/'downstream/furniture_art_v26_r01/fitness_support_patch_r01'
def snap():return {o.name:{'vertices':hashlib.sha256(str([tuple(v.co) for v in o.data.vertices]).encode()).hexdigest(),'basis':[list(v) for v in o.matrix_basis],'materials':[s.material.name if s.material else None for s in o.material_slots],'hidden':o.hide_render} for o in bpy.data.objects if o.type=='MESH'}
before=snap();bpy.ops.wm.open_mainfile(filepath=str(R/'scene/Campus_Center_New_Plans_Furniture_v26_b05.blend'));after=snap();assert set(before)==set(after);changes=[n for n in before if before[n]!=after[n]];allowed=['RE07_PH02_Fitness218_'+n+'_0' for n in ['010','012','014','016','018','035','036']];assert set(changes)==set(allowed),changes;tests=[]
for n in allowed:
 assert all(before[n][k]==after[n][k] for k in ['basis','materials','hidden']);o=bpy.data.objects[n];vs=[o.matrix_world@v.co for v in o.data.vertices];num=n.split('_')[-2]
 if num in ['035','036']:assert max(v.z for v in vs)<5;tests.append({'object':n,'loaded_bar_removed':True,'floor_gap_m':min(v.z for v in vs)-4.2672,'body_height_m':max(v.z for v in vs)-min(v.z for v in vs)})
 else:
  shaft=vs[128:152];assert len(shaft)==24;lo=Vector([min(v[i] for v in shaft) for i in range(3)]);hi=Vector([max(v[i] for v in shaft) for i in range(3)]);checks=[]
  for suffix in ['0','1']:
   rack=bpy.data.objects['RE07_PH02_Fitness218_'+f'{int(num)-1:03d}'+'_'+suffix];rv=[rack.matrix_world@Vector(v) for v in rack.bound_box];rl=Vector([min(v[i] for v in rv) for i in range(3)]);rh=Vector([max(v[i] for v in rv) for i in range(3)]);overlap=[min(hi[i],rh[i])-max(lo[i],rl[i]) for i in range(3)];assert min(overlap)>0,(n,overlap);checks.append({'rack_object':rack.name,'shaft_upright_overlap_m':list(overlap)})
  tests.append({'object':n,'both_supports_intersect_shaft':True,'checks':checks})
(D/'source-support-validation.json').write_text(json.dumps({'changed_objects':changes,'unchanged_mesh_objects':len(before)-len(changes),'iLab_unchanged':True,'all_mesh_basis_materials_visibility_unchanged':True,'support_tests':tests,'limit':'Positive schematic shaft/support intersection is not certified rack hardware or product safety.'},indent=2));print('SOURCE_SUPPORT_VALIDATION_PASS',len(before),len(changes))
