import unreal,pathlib,json
root=pathlib.Path(unreal.Paths.project_dir());tools=unreal.AssetToolsHelpers.get_asset_tools();edit=unreal.MaterialEditingLibrary
mat=unreal.load_asset('/Game/Campus/Materials/M_ArchitecturalGlass')
if not mat:mat=tools.create_asset('M_ArchitecturalGlass','/Game/Campus/Materials',unreal.Material,unreal.MaterialFactoryNew())
edit.delete_all_material_expressions(mat)
mat.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT);mat.set_editor_property('two_sided',True)
color=edit.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector);color.set_editor_property('constant',unreal.LinearColor(.72,.85,.88,1));edit.connect_material_property(color,'',unreal.MaterialProperty.MP_BASE_COLOR)
for prop,val in [(unreal.MaterialProperty.MP_OPACITY,.07),(unreal.MaterialProperty.MP_ROUGHNESS,.12),(unreal.MaterialProperty.MP_SPECULAR,.25),(unreal.MaterialProperty.MP_METALLIC,0)]:
 n=edit.create_material_expression(mat,unreal.MaterialExpressionConstant);n.set_editor_property('r',val);edit.connect_material_property(n,'',prop)
edit.recompile_material(mat);unreal.EditorAssetLibrary.save_loaded_asset(mat)
count=0
for path in unreal.EditorAssetLibrary.list_assets('/Game/Campus/Imported',recursive=True):
 mesh=unreal.load_asset(path)
 if not isinstance(mesh,unreal.StaticMesh):continue
 for i,slot in enumerate(mesh.static_materials):
  m=slot.material_interface
  if m and 'glazing' in m.get_name().lower():mesh.set_material(i,mat);count+=1
 unreal.EditorAssetLibrary.save_loaded_asset(mesh)
(root/'glass_refinement.json').write_text(json.dumps({'material':mat.get_path_name(),'replaced_slots':count,'opacity':.07,'roughness':.12},indent=2))
