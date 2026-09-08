import bpy,json,pathlib,hashlib
from mathutils import Vector
root=pathlib.Path(__file__).parent
s=bpy.context.scene
report={'version':bpy.app.version_string,'filepath':bpy.data.filepath,'units':s.unit_settings.system,'unit_scale':s.unit_settings.scale_length,'camera':s.camera.name if s.camera else None,'frames':[s.frame_start,s.frame_end],'fps':s.render.fps,'collections':{c.name:len(c.objects) for c in bpy.data.collections},'objects':[],'images':[{'name':i.name,'packed':bool(i.packed_file),'path':i.filepath} for i in bpy.data.images]}
for o in s.objects:
 if o.type=='MESH':
  corners=[o.matrix_world@Vector(v) for v in o.bound_box]
  report['objects'].append({'name':o.name,'collections':[c.name for c in o.users_collection],'materials':[m.name for m in o.data.materials if m],'bounds':[[min(p[i] for p in corners) for i in range(3)],[max(p[i] for p in corners) for i in range(3)]],'polygons':len(o.data.polygons),'hidden':o.hide_render})
(root/'blender_inventory.json').write_text(json.dumps(report,indent=2))
print('INVENTORY',len(report['objects']),report['collections'])
