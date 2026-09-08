import bpy,json,pathlib,hashlib
from mathutils import Vector
root=pathlib.Path(__file__).parent;s=bpy.context.scene
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
report={'file':bpy.data.filepath,'sha256':hashlib.sha256(pathlib.Path(bpy.data.filepath).read_bytes()).hexdigest(),'blender':bpy.app.version_string,'scene':s.name,'camera':s.camera.name,'frame_range':[s.frame_start,s.frame_end],'fps':s.render.fps,'engine':s.render.engine,'objects':len(s.objects),'meshes':sum(o.type=='MESH' for o in s.objects),'materials':[],'lights':[],'images':[],'devices':[{'name':d.name,'type':d.type} for d in prefs.devices],'world_nodes':[],'collections':[],'settings':{'view_transform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure,'resolution':[s.render.resolution_x,s.render.resolution_y]}}
for m in bpy.data.materials:
 bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m.use_nodes else None
 report['materials'].append({'name':m.name,'users':m.users,'base':list(bs.inputs['Base Color'].default_value) if bs else None,'roughness':bs.inputs['Roughness'].default_value if bs else None})
for o in s.objects:
 if o.type=='LIGHT':report['lights'].append({'name':o.name,'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'p':list(o.location),'rotation':list(o.rotation_euler),'size':getattr(o.data,'size',None)})
for im in bpy.data.images:report['images'].append({'name':im.name,'packed':bool(im.packed_file),'path':im.filepath})
for c in bpy.data.collections:report['collections'].append({'name':c.name,'hide_render':c.hide_render})
if s.world and s.world.use_nodes:
 for n in s.world.node_tree.nodes:report['world_nodes'].append({'type':n.type,'name':n.name,'inputs':{i.name:list(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value for i in n.inputs if hasattr(i,'default_value') and isinstance(i.default_value,(float,int,bpy.types.bpy_prop_array))}})
(root/'preflight.json').write_text(json.dumps(report,indent=2));print('PREFLIGHT_DONE',flush=True)
