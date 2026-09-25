"""Load only the finish collection; correct closed-box normals in an isolated scene."""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
with bpy.data.libraries.load(str(R.parent/'architect_finishes_v01/Campus_Center_Architect_Finishes_v01.blend'),link=False) as (src,dst):
 dst.collections=['Architect_Finishes_v01']
col=dst.collections[0];bpy.context.scene.collection.children.link(col)
count=0;flipped=0
for o in col.objects:
 if o.type!='MESH':continue
 if len(o.data.vertices)==8 and len(o.data.polygons)==6:
  bm=bmesh.new();bm.from_mesh(o.data)
  if bm.calc_volume(signed=True)<0:flipped+=1
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();count+=1
 o.data.transform(o.matrix_world);o.matrix_world=Matrix.Identity(4);o.select_set(True)
bpy.context.view_layer.objects.active=next(o for o in col.objects if o.type=='MESH');bpy.ops.object.join()
o=bpy.context.object;o.name='Architect_Finishes_v06';o.data.name=o.name
bpy.ops.export_scene.gltf(filepath=str(R/'Architect_Finishes_v06.glb'),export_format='GLB',use_selection=True,export_animations=False,export_cameras=False,export_lights=False)
(R/'normal_correction.json').write_text(json.dumps({'closed_box_meshes':count,'inward_boxes_corrected':flipped,'original_blend_unmodified':True},indent=2))
