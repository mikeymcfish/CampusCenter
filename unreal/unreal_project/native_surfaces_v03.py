import unreal,pathlib,json
root=pathlib.Path(unreal.Paths.project_dir());ed=unreal.MaterialEditingLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();replacements={};report=[]
names=['Gray_thin_brick','Gray_thin_brick1','Warm_ivory_facade_brick','Warm_ivory_facade_brick1','Light_stone_paving','Light_stone_paving1','Anodized_aluminum','Brushed_stainless_hardware','Dark_metal']
for name in names:
 old=unreal.load_asset('/Game/Campus/Imported/Campus_Transfer/Materials/'+name)
 dest='/Game/Campus/PolishV03/Materials/M_'+name
 m=unreal.load_asset(dest) or at.create_asset('M_'+name,'/Game/Campus/PolishV03/Materials',unreal.Material,unreal.MaterialFactoryNew())
 ed.delete_all_material_expressions(m)
 def node(c):return ed.create_material_expression(m,c)
 def const(v):n=node(unreal.MaterialExpressionConstant);n.r=v;return n
 def prop(n,p,out=''):ed.connect_material_property(n,out,p)
 def wire(a,o,b,i):ed.connect_material_expressions(a,o,b,i)
 base=ed.get_material_instance_texture_parameter_value(old,'BaseColorTexture')
 if base:
  uv=node(unreal.MaterialExpressionTextureCoordinate);uv.coordinate_index=int(ed.get_material_instance_scalar_parameter_value(old,'BaseColorTexture_TexCoord'))
  n=node(unreal.MaterialExpressionTextureSample);n.texture=base;wire(uv,'',n,'UVs');prop(n,unreal.MaterialProperty.MP_BASE_COLOR,'')
 else:
  color=ed.get_material_instance_vector_parameter_value(old,'BaseColorFactor');n=node(unreal.MaterialExpressionConstant3Vector);n.constant=color;prop(n,unreal.MaterialProperty.MP_BASE_COLOR)
 prop(const(ed.get_material_instance_scalar_parameter_value(old,'RoughnessFactor')),unreal.MaterialProperty.MP_ROUGHNESS)
 prop(const(ed.get_material_instance_scalar_parameter_value(old,'MetallicFactor')),unreal.MaterialProperty.MP_METALLIC)
 prop(const(.35),unreal.MaterialProperty.MP_SPECULAR)
 # Start clean: keep brick relief in color, isolate imported normal-map artifacts.
 ed.recompile_material(m);ed.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_NANITE);unreal.EditorAssetLibrary.save_loaded_asset(m);replacements[name]=m;report.append({'old':name,'new':dest,'base_texture':base.get_path_name() if base else None})
for path in unreal.EditorAssetLibrary.list_assets('/Game/Campus/Imported',recursive=True):
 mesh=unreal.load_asset(path)
 if not isinstance(mesh,unreal.StaticMesh):continue
 changed=False
 for i,slot in enumerate(mesh.static_materials):
  if slot.material_interface and slot.material_interface.get_name() in replacements:mesh.set_material(i,replacements[slot.material_interface.get_name()]);changed=True
 if changed:unreal.EditorAssetLibrary.save_loaded_asset(mesh)
for path in unreal.EditorAssetLibrary.list_assets('/Game/Campus/PolishV02',recursive=True)+unreal.EditorAssetLibrary.list_assets('/Game/Campus/PolishV03',recursive=True):
 m=unreal.load_asset(path)
 if isinstance(m,unreal.Material):ed.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_NANITE);unreal.EditorAssetLibrary.save_loaded_asset(m)
(root/'native_surfaces_v03.json').write_text(json.dumps(report,indent=2))


