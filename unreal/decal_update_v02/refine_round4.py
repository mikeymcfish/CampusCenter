"""Replace oversized corridor grain with physically scaled oak plank finishes."""
import unreal,pathlib,json
R=pathlib.Path(__file__).parent;E=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;T=unreal.AssetToolsHelpers.get_asset_tools()
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert L.load_level('/Game/Campus/Maps/CampusCenter_ArchitectDecals_v04')
D='/Game/Campus/DisplayDecalsV02/ArchitectureMaterials';name='M_CorridorOakPlanks'
m=unreal.load_asset(D+'/'+name) if E.does_asset_exist(D+'/'+name) else T.create_asset(name,D,unreal.Material,unreal.MaterialFactoryNew());M.delete_all_material_expressions(m)
def node(c):return M.create_material_expression(m,c)
def custom(code,inputs,typ):
 n=node(unreal.MaterialExpressionCustom);n.set_editor_property('code',code);n.set_editor_property('output_type',typ);ins=[]
 for key in inputs:
  ci=unreal.CustomInput();ci.set_editor_property('input_name',key);ins.append(ci)
 n.set_editor_property('inputs',ins)
 for key,src in inputs.items():M.connect_material_expressions(src,'RGB' if isinstance(src,unreal.MaterialExpressionTextureSample) else '',n,key)
 return n
F1=unreal.CustomMaterialOutputType.CMOT_FLOAT1;F2=unreal.CustomMaterialOutputType.CMOT_FLOAT2;F3=unreal.CustomMaterialOutputType.CMOT_FLOAT3
p=node(unreal.MaterialExpressionWorldPosition)
prefix='float2 q=P.x>-2000?P.xy:float2(-P.y,P.x);float row=floor(q.y/18);float off=frac(sin(row*12.9898)*43758.5453)*108;float col=floor((q.x+off)/108);float h=frac(sin(row*78.233+col*41.37)*43758.5453);float2 f=float2(frac((q.x+off)/108),frac(q.y/18));'
uv=custom(prefix+'return f*float2(1,.18)+float2(h,frac(h*7.1));',{'P':p},F2)
s=node(unreal.MaterialExpressionTextureSample);s.texture=unreal.load_asset('/Game/Campus/PolishV03/Textures/Wood049_2K-JPG_Color');M.connect_material_expressions(uv,'',s,'UVs')
color=custom(prefix+'float edge=min(min(f.x,1-f.x)*108,min(f.y,1-f.y)*18);float joint=smoothstep(.025,.10,edge);float g=saturate(dot(C,float3(.3,.59,.11))*1.75);float3 wood=lerp(float3(.23,.125,.059),float3(.53,.365,.205),g)*(.91+h*.16);return lerp(wood*.38,wood,joint);',{'P':p,'C':s},F3)
M.connect_material_property(color,'',unreal.MaterialProperty.MP_BASE_COLOR)
rough=custom(prefix+'return .46+h*.07;',{'P':p},F1);M.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
nr=node(unreal.MaterialExpressionTextureSample);nr.texture=unreal.load_asset('/Game/Campus/PolishV03/Textures/Wood049_2K-JPG_NormalDX');nr.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL);M.connect_material_expressions(uv,'',nr,'UVs')
normal=custom('return normalize(float3(C.xy*.13,C.z));',{'C':nr},F3);M.connect_material_property(normal,'',unreal.MaterialProperty.MP_NORMAL)
M.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_NANITE);M.recompile_material(m);E.save_loaded_asset(m)
cube=unreal.load_asset('/Engine/BasicShapes/Cube');report=[]
for name,x0,x1,y0,y1 in [('DD_GalleryFloor_Oak',-1145,-10,1002,1622),('DD_TrophyFloor_Oak',-3017,-2585,1655,2990)]:
 a=next((a for a in A.get_all_level_actors() if a.get_actor_label()==name),None)
 if not a:a=A.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());a.set_actor_label(name)
 a.set_actor_location(unreal.Vector((x0+x1)/2,-(y0+y1)/2,1.6),False,False);a.set_actor_scale3d(unreal.Vector((x1-x0)/100,(y1-y0)/100,.008))
 c=a.static_mesh_component;c.set_static_mesh(cube);c.set_material(0,m);c.set_collision_profile_name('NoCollision');report.append(name)
L.save_current_level();(R/'round4_changes.json').write_text(json.dumps({'additive_corridor_finish':report,'plank_dimensions_cm':[108,18],'furniture_unchanged':True},indent=2));unreal.log('ROUND4_COMPLETE')
