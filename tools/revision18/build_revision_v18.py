from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector,Matrix
R=Path(__file__).parent;O=R/'output_v18';O.mkdir(exist_ok=True)
src=Path('P:/_code/CampusCenter/scene/Campus_Center_Current.blend');sha=hashlib.sha256(src.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
changes=[]
def move(name,d):
 ob=bpy.data.objects[name];ob.location+=Vector(d);changes.append({'object':name,'translation':d})
def move_group(name,d):
 ob=bpy.data.objects[name];pts=[ob.matrix_world@Vector(v) for v in ob.bound_box];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
 for st in list(s.objects):
  if st.name.startswith('Student_') and all(lo[i]-.1<st.location[i]<hi[i]+.1 for i in [0,1]) and st.location.z<2:move(st.name,d)
 move(name,d)
move('V15_Janitor_washer',(-.45,-.9,0));move('V15_Janitor_dryer',(-1.15,-1.7,0))
for room in [121,122]:
 for suffix in ['north','south']:move(f'V15_Locker_{room}_return_west{suffix}',(.18,0,0))
move('V15_Locker_121_perimeter_1',(0,.14,0))
move_group('V15_Commons_lounge_cluster_3',(.65,0,0));move_group('V15_Commons_round_dining_2',(-1.4,0,0))
move('V15_Commons_north_perimeter_benches',(0,-.85,0))
for ob in list(s.objects):
 if ob.name.startswith('V5_Commons_bench'):
  changes.append({'object':ob.name,'removed':'Superseded by V15 perimeter seating; duplicate overlaps'});bpy.data.objects.remove(ob,do_unlink=True)
move('V15_Athletics_ice_maker',(.32,0,0));move_group('V15_Athletics_office_visitor_table',(1.85,.85,0));move('Student_046',(-.4,0,0));move('Student_058',(0,-.6,0));move('Student_064',(.65,-.15,0))
# Attach displays to solid wall faces. Leave a 10 mm stand-off.
for name,x,y in [('V15_Wall_information_display_0',-30.322,27.0),('V15_Wall_information_display_1',-30.412,18.7),('V15_Wall_information_display_2',-14.855,12.23)]:
 ob=bpy.data.objects[name];pts=[ob.matrix_world@Vector(v) for v in ob.bound_box];c=sum(pts,Vector())/8;move(name,(x-c.x,y-c.y,0))
# Raised display case: extend its existing bottom trim down to the floor, no new prop.
ob=bpy.data.objects['V8_DETAIL_Trophy_display_case'];ob.data=ob.data.copy()
for v in ob.data.vertices:
 p=ob.matrix_world@v.co
 if p.z<.14:p.z=.005;v.co=ob.matrix_world.inverted()@p
changes.append({'object':ob.name,'repair':'Existing lowest trim extended to floor'})
# Textures: real-world UV mapping and packed portable image maps.
T=R/'output_3d_v4/textures'
materials={'Natural oak':('oak', (2.4,1.2),.48),'Acoustic panel neutral':('oak',(2.4,1.2),.7),'Gray thin brick':('brick_gray',(1.0,1.2),.85),'Warm ivory facade brick':('brick_ivory',(1.0,1.2),.85),'Light stone paving':('stone',(1.2,1.2),.7)}
for name,(tex,scale,rough) in materials.items():
 m=bpy.data.materials[name];m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');bs=nt.nodes.new('ShaderNodeBsdfPrincipled');nt.links.new(bs.outputs['BSDF'],out.inputs['Surface']);bs.inputs['Roughness'].default_value=rough
 for suffix,socket in [('base','Base Color'),('normal','Normal')]:
  im=bpy.data.images.load(str(T/(tex+'_'+suffix+'.png')),check_existing=True);im.pack();n=nt.nodes.new('ShaderNodeTexImage');n.image=im
  if suffix=='normal':im.colorspace_settings.name='Non-Color';nn=nt.nodes.new('ShaderNodeNormalMap');nn.inputs['Strength'].default_value=.22;nt.links.new(n.outputs['Color'],nn.inputs['Color']);nt.links.new(nn.outputs['Normal'],bs.inputs[socket])
  else:nt.links.new(n.outputs['Color'],bs.inputs[socket])
 m['v18_finish']=tex
# Subtle roughness/physical finishes for the remaining palette.
for m in bpy.data.materials:
 if not m.use_nodes:continue
 bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
 if not bs:continue
 n=m.name.lower()
 if any(k in n for k in ['aluminum','stainless','dark metal']):bs.inputs['Metallic'].default_value=.8;bs.inputs['Roughness'].default_value=.3
 elif 'porcelain' in n:bs.inputs['Roughness'].default_value=.2
 elif 'glazing' in n:bs.inputs['Transmission Weight'].default_value=1;bs.inputs['IOR'].default_value=1.45;bs.inputs['Roughness'].default_value=.065;bs.inputs['Alpha'].default_value=1
 elif 'plaster' in n:bs.inputs['Roughness'].default_value=.85
 elif 'upholstery' in n or 'chair shell' in n:bs.inputs['Roughness'].default_value=.82
 elif 'rubber' in n:bs.inputs['Roughness'].default_value=.94
# UVs by polygon orientation, dimensions in metres. Preserve other shared meshes.
uvcount=0
for ob in s.objects:
 if ob.type!='MESH' or not any(m and m.name in materials for m in ob.data.materials):continue
 ob.data=ob.data.copy();me=ob.data;uv=me.uv_layers.get('V18_RealWorld') or me.uv_layers.new(name='V18_RealWorld');me.uv_layers.active=uv;uv.active_render=True
 for face in me.polygons:
  m=me.materials[face.material_index] if face.material_index<len(me.materials) else None
  if not m or m.name not in materials:continue
  scale=materials[m.name][1];normal=ob.matrix_world.to_3x3()@face.normal;axis=max(range(3),key=lambda i:abs(normal[i]));axes=(0,1) if axis==2 else ((0,2) if axis==1 else (1,2))
  for li in face.loop_indices:
   p=ob.matrix_world@me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]/scale[0],p[axes[1]]/scale[1])
 uvcount+=1
s['revision']=18;s['finish_pass']='First reference-based packed texture pass; blank mannequins retained';s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Campus_Center_Textured.blend'))
(O/'changes.json').write_text(json.dumps({'source':str(src),'source_sha256':sha,'changes':changes,'uv_mapped_objects':uvcount,'textured_materials':list(materials)},indent=2));assert hashlib.sha256(src.read_bytes()).hexdigest()==sha
print('V18_REPAIRS_MATERIALS_SAVED',flush=True)
