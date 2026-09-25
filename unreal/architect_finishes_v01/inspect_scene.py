import bpy
import json
from mathutils import Vector
from pathlib import Path

out = Path(__file__).with_name('scene_inventory.json')
terms = ('commons', 'gallery', 'corridor', 'slab', 'ceiling', 'soffit', 'wood_base', 'entry_acoustic', 'fireplace', 'roof')
objects = []
for obj in bpy.data.objects:
    if obj.type != 'MESH':
        continue
    bb = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    spatial = min(v.x for v in bb) < 16 and max(v.x for v in bb) > 0 and min(v.y for v in bb) < 31 and max(v.y for v in bb) > 14 and max(v.z for v in bb) > 7.5
    if not spatial and not any(t in obj.name.lower() for t in terms):
        continue
    objects.append({
        'name': obj.name,
        'min': [round(min(v[i] for v in bb), 3) for i in range(3)],
        'max': [round(max(v[i] for v in bb), 3) for i in range(3)],
        'materials': [m.name if m else None for m in obj.data.materials],
        'polygons': len(obj.data.polygons),
    })
out.write_text(json.dumps({'scene': bpy.context.scene.name, 'objects': objects}, indent=2))
print('INSPECTED', len(objects), out)
