"""Export only the additive architectural finish layer for Unreal."""
import bpy
from mathutils import Matrix
from pathlib import Path

root = Path(__file__).parent
col = bpy.data.collections['Architect_Finishes_v01']
bpy.ops.object.select_all(action='DESELECT')
copies = []
for source in col.objects:
    copy = source.copy()
    copy.data = source.data.copy()
    bpy.context.scene.collection.objects.link(copy)
    copy.data.transform(source.matrix_world)
    copy.matrix_world = Matrix.Identity(4)
    copy.select_set(True)
    copies.append(copy)
bpy.context.view_layer.objects.active = copies[0]
bpy.ops.object.join()
joined = bpy.context.object
joined.name = 'Architect_Finishes_v05'
joined.data.name = 'Architect_Finishes_v05'
bpy.ops.export_scene.gltf(
    filepath=str(root / 'Architect_Finishes_v05.glb'),
    export_format='GLB',
    export_animations=False,
    export_cameras=False,
    export_lights=False,
    use_selection=True,
)
print('FINISH_LAYER_EXPORTED', len(joined.data.vertices), len(joined.data.polygons))
