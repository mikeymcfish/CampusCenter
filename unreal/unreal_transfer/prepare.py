import bpy,json,pathlib,math,hashlib,re
from mathutils import Vector,Matrix
root=pathlib.Path(__file__).parent; out=root/'exports';out.mkdir(exist_ok=True)
s=bpy.context.scene;s.frame_set(1)
source=root/'source/Campus_Center_Source.blend'
report={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'groups':{},'lights':[],'camera_samples':[]}
for f in range(1,s.frame_end+1,6):
 s.frame_set(f);c=s.camera;pos=c.matrix_world.translation;direction=c.matrix_world.to_quaternion()@Vector((0,0,-1))
 report['camera_samples'].append({'time':(f-1)/24,'p':[pos.x*100,-pos.y*100,pos.z*100],'dir':[direction.x,-direction.y,direction.z]})
s.frame_set(1)
for o in list(s.objects):
 if o.type=='LIGHT':report['lights'].append({'name':o.name,'p':list(o.matrix_world.translation),'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'size':getattr(o.data,'size',1)})
groups={};dep=bpy.context.evaluated_depsgraph_get()
for o in list(s.objects):
 if o.type not in {'MESH','FONT','CURVE'} or o.hide_render:continue
 if any(c.name=='ROOM_LABELS' for c in o.users_collection):continue
 name=o.name.lower();cols=' '.join(c.name for c in o.users_collection).lower()
 category='Students' if name.startswith('student_') else 'Roof' if 'roof' in cols else 'Equipment' if any(w in cols for w in ['equipment','technology','fixtures','cafe','plumbing']) else 'Furniture' if any(w in cols for w in ['furniture','lockers']) else 'Architecture'
 if 'lowered screen' in cols:category='Screen'
 if '_leaf' in name or 'lever' in name or 'pull_' in name:category='Doors'
 center=sum((o.matrix_world@Vector(v) for v in o.bound_box),Vector())/8
 level='Upper' if center.z>3.9 else 'Ground'
 tile=f'{math.floor(center.x/8)+10:02d}_{math.floor(center.y/8)+10:02d}'
 key=f'{category}_{level}_{tile}'
 ev=o.evaluated_get(dep);m=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=dep)
 if not m.vertices:bpy.data.meshes.remove(m);continue
 m.transform(o.matrix_world)
 if o.matrix_world.determinant()<0:
  import bmesh
  bm=bmesh.new();bm.from_mesh(m);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free()
 ob=bpy.data.objects.new('transfer_'+o.name,m);s.collection.objects.link(ob)
 groups.setdefault(key,[]).append(ob);report['groups'].setdefault(key,{'objects':[],'category':category,'level':level})['objects'].append(o.name)
originals=[o for o in s.objects if not o.name.startswith('transfer_')]
for o in originals:bpy.data.objects.remove(o,do_unlink=True)
for key,objects in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();ob=bpy.context.object;ob.name=key;ob.data.name=key
 report['groups'][key]['vertices']=len(ob.data.vertices);report['groups'][key]['polygons']=len(ob.data.polygons)
 # Keep the origin at zero: imported mesh vertices retain world placement.
 ob.matrix_world=Matrix.Identity(4)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(out/'Campus_Transfer.glb'),export_format='GLB',export_animations=False,export_cameras=False,export_lights=False,use_selection=True)
(out/'transfer_manifest.json').write_text(json.dumps(report,indent=2))
print('TRANSFER_READY',len(groups),flush=True)
