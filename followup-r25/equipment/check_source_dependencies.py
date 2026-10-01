import bpy,json,pathlib
O=pathlib.Path(__file__).parent
images=[]
for image in bpy.data.images:
 if image.source=='FILE':
  packed=bool(image.packed_file or image.packed_files);path=pathlib.Path(bpy.path.abspath(image.filepath));images.append({'name':image.name,'packed':packed,'external_path':str(path),'exists':path.exists(),'portable':packed})
linked=[{'name':l.name,'filepath':l.filepath} for l in bpy.data.libraries]
data={'saved_source':bpy.data.filepath,'blender':bpy.app.version_string,'mesh_objects':sum(o.type=='MESH' for o in bpy.context.scene.objects),'units':bpy.context.scene.unit_settings.scale_length,'images':images,'linked_libraries':linked,'missing_images':[i for i in images if not i['packed'] and not i['exists']]}
(O/'source_dependency_check.json').write_text(json.dumps(data,indent=2));print('DEPENDENCIES',len(images),'missing',len(data['missing_images']),'linked',len(linked))
assert not data['missing_images'] and not linked
