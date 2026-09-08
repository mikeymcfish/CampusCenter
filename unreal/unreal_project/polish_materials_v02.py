import unreal,pathlib,json
root=pathlib.Path(unreal.Paths.project_dir());assets=root.parent/'polish_v02/assets';edit=unreal.MaterialEditingLibrary;at=unreal.AssetToolsHelpers.get_asset_tools()
dest='/Game/Campus/PolishV02';report={'adjusted':[],'slot_replacements':0,'new_materials':[]}
def texture(asset,kind):
 f=assets/asset/(asset+'_1K-JPG_'+kind+'.jpg');name=f.stem
 t=unreal.load_asset(dest+'/Textures/'+name)
 if not t:
  task=unreal.AssetImportTask();task.filename=str(f);task.destination_path=dest+'/Textures';task.automated=True;task.save=True;at.import_asset_tasks([task]);t=unreal.load_asset(task.imported_object_paths[0])
 if kind=='NormalDX':t.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_NORMALMAP);t.set_editor_property('srgb',False)
 elif kind=='Roughness':t.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_MASKS);t.set_editor_property('srgb',False)
 unreal.EditorAssetLibrary.save_loaded_asset(t);return t
def material(name,asset,color,normalstrength,roughlo,roughhi,tiling):
 m=unreal.load_asset(dest+'/Materials/'+name)
 if not m:m=at.create_asset(name,dest+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
 edit.delete_all_material_expressions(m)
 def node(cls):return edit.create_material_expression(m,cls)
 def scalar(v):n=node(unreal.MaterialExpressionConstant);n.r=v;return n
 def vec(v):n=node(unreal.MaterialExpressionConstant3Vector);n.constant=unreal.LinearColor(*v,1);return n
 def wire(a,out,b,input):edit.connect_material_expressions(a,out,b,input)
 def prop(a,out,p):edit.connect_material_property(a,out,p)
 uv=node(unreal.MaterialExpressionTextureCoordinate);uv.u_tiling=tiling;uv.v_tiling=tiling
 maps={}
 for kind in ['Color','NormalDX','Roughness']:
  n=node(unreal.MaterialExpressionTextureSample);n.texture=texture(asset,kind)
  if kind=='NormalDX':n.sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL
  elif kind=='Roughness':n.sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_MASKS
  wire(uv,'',n,'Coordinates');maps[kind]=n
 shade=node(unreal.MaterialExpressionLinearInterpolate);wire(scalar(.88),'',shade,'A');wire(scalar(1.08),'',shade,'B');wire(maps['Color'],'R',shade,'Alpha')
 mult=node(unreal.MaterialExpressionMultiply);wire(vec(color),'',mult,'A');wire(shade,'',mult,'B');prop(mult,'',unreal.MaterialProperty.MP_BASE_COLOR)
 rough=node(unreal.MaterialExpressionLinearInterpolate);wire(scalar(roughlo),'',rough,'A');wire(scalar(roughhi),'',rough,'B');wire(maps['Roughness'],'R',rough,'Alpha');prop(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
 norm=node(unreal.MaterialExpressionLinearInterpolate);wire(vec((0,0,1)),'',norm,'A');wire(maps['NormalDX'],'RGB',norm,'B');wire(scalar(normalstrength),'',norm,'Alpha');prop(norm,'',unreal.MaterialProperty.MP_NORMAL)
 prop(scalar(.35),'',unreal.MaterialProperty.MP_SPECULAR)
 edit.recompile_material(m);unreal.EditorAssetLibrary.save_loaded_asset(m);report['new_materials'].append(m.get_path_name());return m
cloth=material('M_Sage_Woven_Fabric','Fabric030',(.24,.31,.27),.28,.73,.93,2)
plaster=material('M_Warm_Painted_Plaster','PaintedPlaster017',(.76,.74,.69),.12,.68,.84,3)
# Preserve the original architectural UVs and textures, tuning their physical response.
tuning={'Natural_oak':(.38,0,.13),'Acoustic_panel_neutral':(.62,0,.11),'Gray_thin_brick':(.9,0,.30),'Gray_thin_brick1':(.9,0,.30),'Warm_ivory_facade_brick':(.88,0,.24),'Warm_ivory_facade_brick1':(.88,0,.24),'Light_stone_paving':(.57,0,.12),'Light_stone_paving1':(.57,0,.12),'Anodized_aluminum':(.31,1,None),'Brushed_stainless_hardware':(.24,1,None),'Dark_metal':(.34,.9,None),'V8_plain_porcelain':(.16,0,None),'V8_plain_rubber':(.92,0,None),'V8_plain_light_table_surface':(.39,0,None),'V8_plain_chair_shell':(.43,0,None),'V8_plain_dark_screen':(.21,0,None)}
for name,(rough,metal,normal) in tuning.items():
 m=unreal.load_asset('/Game/Campus/Imported/Campus_Transfer/Materials/'+name);assert m,name
 edit.set_material_instance_scalar_parameter_value(m,'RoughnessFactor',rough);edit.set_material_instance_scalar_parameter_value(m,'MetallicFactor',metal)
 if normal is not None:edit.set_material_instance_scalar_parameter_value(m,'NormalScale',normal)
 edit.update_material_instance(m);unreal.EditorAssetLibrary.save_loaded_asset(m);report['adjusted'].append({'name':name,'roughness':rough,'metallic':metal,'normal_strength':normal})
for p in unreal.EditorAssetLibrary.list_assets('/Game/Campus/Imported',recursive=True):
 mesh=unreal.load_asset(p)
 if not isinstance(mesh,unreal.StaticMesh):continue
 changed=False
 for i,slot in enumerate(mesh.static_materials):
  m=slot.material_interface;name=m.get_name() if m else ''
  replacement=cloth if name in ['V8_plain_sage_upholstery','M_Sage_Woven_Fabric'] else plaster if name in ['Warm_white_plaster','M_Warm_Painted_Plaster'] else None
  if replacement:mesh.set_material(i,replacement);changed=True;report['slot_replacements']+=1
 if changed:unreal.EditorAssetLibrary.save_loaded_asset(mesh)
(root/'polish_v02_report.json').write_text(json.dumps(report,indent=2));unreal.log('POLISH_V02_SAVED')
