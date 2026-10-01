import bpy,pathlib,json
R=pathlib.Path(__file__).parent;records=[]
for family,name in [('ground_furnished','Ground_Furnished'),('ground_enclosed','Ground_Enclosed'),('ground_acrylic','Ground_Acrylic'),('upper_enclosed','Upper_Enclosed')]:
 o=bpy.data.objects[name];expected=json.loads((R/family/'validation.json').read_text())['dimensions_mm'];assert all(abs(o.dimensions[i]*1000-expected[i])<.003 for i in range(3));records.append({'object':name,'dimensions_mm':[float(x*1000) for x in o.dimensions]})
assert len([o for o in bpy.data.objects if o.type=='MESH'])==7;assert bpy.context.scene.unit_settings.scale_length==1
(R/'editable_reopen_validation.json').write_text(json.dumps({'status':'passed','file':bpy.data.filepath,'authoring_blender_version':bpy.app.version_string,'mesh_objects':7,'units':'metres','objects':records},indent=2));print('EDITABLE_VARIANT_REOPENED')
