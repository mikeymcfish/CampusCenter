import bpy,json,pathlib
from mathutils import Vector
root=pathlib.Path(__file__).parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(root/'Trophy_Optimized.glb'))
objects=[o for o in bpy.context.scene.objects if o.type=='MESH'];points=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
height=max(v.z for v in points)-min(v.z for v in points)
report={'mesh_objects':len(objects),'triangles':sum(len(p.vertices)-2 for o in objects for p in o.data.polygons),'height_m':height,'materials':len({m.name for o in objects for m in o.data.materials}),'status':'passed' if abs(height-.3)<.001 and len(objects)==1 else 'needs_review'}
(root/'trophy_reopen.json').write_text(json.dumps(report,indent=2));assert report['status']=='passed'
