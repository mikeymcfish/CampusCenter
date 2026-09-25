"""Explicit native display finishes and unobstructed trophy mounting."""
import unreal,json,pathlib
R=pathlib.Path(__file__).parent
E=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;T=unreal.AssetToolsHelpers.get_asset_tools()
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert L.load_level('/Game/Campus/Maps/CampusCenter_ArchitectDecals_v04')
D='/Game/Campus/DisplayDecalsV02/Materials'
def material(name,code,rough=.8,wood=False):
 p=D+'/'+name;m=unreal.load_asset(p) if E.does_asset_exist(p) else T.create_asset(name,D,unreal.Material,unreal.MaterialFactoryNew())
 M.delete_all_material_expressions(m)
 def node(c):return M.create_material_expression(m,c)
 n=node(unreal.MaterialExpressionCustom);n.set_editor_property('code',code);n.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3)
 ci=unreal.CustomInput();ci.set_editor_property('input_name','P');n.set_editor_property('inputs',[ci])
 pos=node(unreal.MaterialExpressionWorldPosition);M.connect_material_expressions(pos,'',n,'P')
 if wood:
  uv=node(unreal.MaterialExpressionCustom);uv.set_editor_property('code','return float2(P.z/180.,(P.x>-2000?P.x:P.y)/42.);');uv.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT2);uv.set_editor_property('inputs',[ci])
  M.connect_material_expressions(pos,'',uv,'P')
  sample=node(unreal.MaterialExpressionTextureSample);sample.texture=unreal.load_asset('/Game/Campus/PolishV03/Textures/Wood049_2K-JPG_Color');M.connect_material_expressions(uv,'',sample,'UVs')
  ci2=unreal.CustomInput();ci2.set_editor_property('input_name','C');n.set_editor_property('inputs',[ci,ci2]);M.connect_material_expressions(pos,'',n,'P');M.connect_material_expressions(sample,'RGB',n,'C')
 M.connect_material_property(n,'',unreal.MaterialProperty.MP_BASE_COLOR)
 r=node(unreal.MaterialExpressionConstant);r.r=rough;M.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS)
 M.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_NANITE);M.recompile_material(m);E.save_loaded_asset(m);return m
oak=material('M_Display_Oak','float g=dot(C,float3(.3,.59,.11)); return lerp(float3(.38,.25,.14),float3(.68,.51,.31),saturate(g*2.1));',.63,True)
cork=material('M_Display_Cork','float g=frac(sin(dot(floor(P.xz*5),float2(12.9898,78.233)))*43758.5453); return float3(.23,.15,.085)*(.78+g*.4);',.95)
taupe=material('M_Display_Taupe','return float3(.12,.10,.078);',.9)
dark=material('M_Display_Bronze','return float3(.045,.033,.022);',.56)
report={'shelf_top_cm':180.5,'case_top_cm':167.5,'clearance_cm':13,'actors':[]}
for a in A.get_all_level_actors():
 name=a.get_actor_label()
 if isinstance(a,unreal.StaticMeshActor) and name.startswith('DD_'):
  c=a.static_mesh_component
  if name.startswith('DD_Trophy_') or name.startswith('DD_Shelf_Bracket'):
   x=-1.2 if name[-2:].isdigit() and name.startswith('DD_Trophy_') else 0
   a.set_actor_location(unreal.Vector(x,0,56.5),False,False)
  mat=None
  if name=='DD_Gallery_Cork':mat=cork
  elif name=='DD_Trophy_Backboard':mat=taupe
  elif 'ShadowReveal' in name or 'Bracket' in name:mat=dark
  elif name in ['DD_Gallery_Dado','DD_Trophy_Shelf'] or 'Gallery_Rail' in name:mat=oak
  if mat:c.set_material(0,mat)
  report['actors'].append(name)
 if isinstance(a,unreal.RectLight) and name.startswith('DD_'):
  c=a.light_component;c.set_intensity(220 if 'Gallery' in name else 180);c.set_cast_shadows(False)
  if 'Trophy' in name:
   p=a.get_actor_location();p.z=345;a.set_actor_location(p,False,False)
 if isinstance(a,unreal.PostProcessVolume):
  s=a.settings;s.set_editor_property('override_auto_exposure_bias',True);s.set_editor_property('auto_exposure_bias',.15);a.settings=s
L.save_current_level();(R/'round2_changes.json').write_text(json.dumps(report,indent=2));unreal.log('DISPLAY_REFINEMENT_COMPLETE')
