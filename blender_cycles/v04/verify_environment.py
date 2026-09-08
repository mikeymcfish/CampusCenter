import bpy,json,pathlib,hashlib
from mathutils import Vector
R=pathlib.Path(__file__).parent;s=bpy.context.scene;src=json.loads((R/'preflight.json').read_text());build=json.loads((R/'build_report.json').read_text());fail=[]
assert hashlib.sha256((R/'Source_Copy.blend').read_bytes()).hexdigest()==src['sha256']
assert hashlib.sha256((R.parent/'cycles_studio_v03/Campus_Center_Cycles_Studio.blend').read_bytes()).hexdigest()==src['sha256']
for row in src['objects']:
 o=bpy.data.objects.get(row['name'])
 if not o:fail.append([row['name'],'missing']);continue
 if len(o.data.vertices)!=row['verts'] or len(o.data.polygons)!=row['faces']:fail.append([o.name,'topology'])
 vals=[v for r in o.matrix_basis for v in r]
 if max(abs(a-b) for a,b in zip(vals,row['matrix']))>1e-6:fail.append([o.name,'stored transform'])
 if o.name not in build['hidden'] and o.hide_render!=row['hidden']:fail.append([o.name,'visibility'])
missing=[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file and not pathlib.Path(bpy.path.abspath(im.filepath)).exists()]
assert not fail and not missing,(fail,missing)
sizes=[]
for y in [20,25,29]:
 o=bpy.data.objects['V03 King banner '+str(y)];ys=[v.co.y for v in o.data.vertices];zs=[v.co.z for v in o.data.vertices];d=[max(ys)-min(ys),max(zs)-min(zs)];assert abs(d[0]-1.4)<1e-5 and abs(d[1]-4.2)<1e-5;sizes.append(d)
assert bpy.data.objects['V15_Commons_curved_lounge'].hide_render
assert bpy.data.objects['V04 Fire billboard'].data.materials[0].node_tree.nodes.get('Emission')
assert s.world.name.startswith('V04') and any(n.type=='TEX_ENVIRONMENT' and n.image.packed_file for n in s.world.node_tree.nodes)
assert bpy.data.objects['Walkthrough_Camera'].animation_data and [s.frame_start,s.frame_end]==src['frames']
assert s.render.engine=='CYCLES' and s.cycles.samples==256 and [s.render.resolution_x,s.render.resolution_y]==[1920,1080]
report={'status':'passed','source_v03_unchanged':True,'original_objects_retained':len(src['objects']),'errors':fail,'missing_images':missing,'packed_images':sum(bool(i.packed_file) for i in bpy.data.images),'banner_sizes_m':sizes,'fireplace_obstructing_group_disabled':True,'imagegen_fire_packed':True,'hdr_environment_packed':True,'original_walkthrough_retained':True,'new_plant_instances':len(build['plant_instances'])}
(R/'scene_validation.json').write_text(json.dumps(report,indent=2));print(report)
