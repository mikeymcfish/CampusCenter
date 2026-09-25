import bpy
import json
from pathlib import Path

root = Path(__file__).parent
out = {
    'filepath': bpy.data.filepath,
    'objects': len(bpy.data.objects),
    'finish_objects': len(bpy.data.collections['Architect_Finishes_v01'].objects),
    'furniture': sorted((o.name, len(o.data.vertices), len(o.data.polygons)) for o in bpy.data.objects if o.type == 'MESH' and ('Furniture' in o.name or o.name.startswith(('V8_', 'V9_')))),
    'cameras': [{'name': o.name, 'location': list(o.location), 'rotation': list(o.rotation_euler)} for o in bpy.data.objects if o.type == 'CAMERA'],
}
(root / 'verification.json').write_text(json.dumps(out, indent=2))
print('VERIFIED', out['objects'], out['finish_objects'], len(out['furniture']), len(out['cameras']))
