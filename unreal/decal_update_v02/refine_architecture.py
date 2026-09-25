"""Map-local finish overrides: varied ceramic, photographic oak, coursed stone pier."""
import unreal,pathlib,json
R=pathlib.Path(__file__).parent;E=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;T=unreal.AssetToolsHelpers.get_asset_tools()
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert L.load_level('/Game/Campus/Maps/CampusCenter_ArchitectDecals_v04')
D='/Game/Campus/DisplayDecalsV02/ArchitectureMaterials'
def base(name):
 p=D+'/'+name;m=unreal.load_asset(p) if E.does_asset_exist(p) else T.create_asset(name,D,unreal.Material,unreal.MaterialFactoryNew());M.delete_all_material_expressions(m);return m
def node(m,c):return M.create_material_expression(m,c)
def custom(m,code,inputs,typ=unreal.CustomMaterialOutputType.CMOT_FLOAT3):
 n=node(m,unreal.MaterialExpressionCustom);n.set_editor_property('code',code);n.set_editor_property('output_type',typ)
 ins=[]
 for name in inputs:
  ci=unreal.CustomInput();ci.set_editor_property('input_name',name);ins.append(ci)
 n.set_editor_property('inputs',ins)
 for name,src in inputs.items():M.connect_material_expressions(src,'RGB' if isinstance(src,unreal.MaterialExpressionTextureSample) else '',n,name)
 return n
def scalar(m,v,prop):
 s=node(m,unreal.MaterialExpressionConstant);s.r=v;M.connect_material_property(s,'',prop)
def finish(m):
 M.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_NANITE);M.recompile_material(m);E.save_loaded_asset(m);return m
overrides={}
for k in range(4):
 name='M_AF_BlueTile_%02d'%k;m=base(name);p=node(m,unreal.MaterialExpressionWorldPosition)
 code='''float row=floor((-P.y-70)/23.5);float col=floor((P.x-18+fmod(abs(row),2)*23.5)/47.0);
 float h=frac(sin(dot(float2(row,col),float2(12.9898,78.233)))*43758.5453);
 float2 q=P.xy*.035+float2(h*41,h*73);float2 i=floor(q);float2 f=frac(q);f=f*f*(3-2*f);
 float a=frac(sin(dot(i,float2(127.1,311.7)))*43758.5453);float b=frac(sin(dot(i+float2(1,0),float2(127.1,311.7)))*43758.5453);
 float c=frac(sin(dot(i+float2(0,1),float2(127.1,311.7)))*43758.5453);float d=frac(sin(dot(i+1,float2(127.1,311.7)))*43758.5453);
 float n=lerp(lerp(a,b,f.x),lerp(c,d,f.x),f.y);return float3(.029,.078,.17)*(.86+h*.25+(n-.5)*.07);'''
 M.connect_material_property(custom(m,code,{'P':p}),'',unreal.MaterialProperty.MP_BASE_COLOR)
 scalar(m,.26+k*.018,unreal.MaterialProperty.MP_ROUGHNESS);scalar(m,.4,unreal.MaterialProperty.MP_SPECULAR);overrides[name]=finish(m)
for k in range(5):
 name='M_AF_LightOak_%02d'%k;m=base(name);p=node(m,unreal.MaterialExpressionWorldPosition);normal=node(m,unreal.MaterialExpressionVertexNormalWS);uv=node(m,unreal.MaterialExpressionTextureCoordinate)
 coords=custom(m,'return abs(N.z)>.5 && P.z<10 ? UV+float2('+str(k*.137)+','+str(k*.091)+') : (P.z>700 && abs(N.z)>.5 ? P.xy : (abs(N.x)>.5 ? P.zy : P.zx))/float2(170,45);',{'P':p,'N':normal,'UV':uv},unreal.CustomMaterialOutputType.CMOT_FLOAT2)
 sample=node(m,unreal.MaterialExpressionTextureSample);sample.texture=unreal.load_asset('/Game/Campus/PolishV03/Textures/Wood049_2K-JPG_Color');M.connect_material_expressions(coords,'',sample,'UVs')
 tint=custom(m,'float g=saturate(dot(C,float3(.3,.59,.11))*1.55);return lerp(float3(.19,.10,.041),float3(.48,.30,.145),g)*'+str(.94+k*.026)+';',{'C':sample})
 M.connect_material_property(tint,'',unreal.MaterialProperty.MP_BASE_COLOR)
 nr=node(m,unreal.MaterialExpressionTextureSample);nr.texture=unreal.load_asset('/Game/Campus/PolishV03/Textures/Wood049_2K-JPG_NormalDX');nr.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL);M.connect_material_expressions(coords,'',nr,'UVs')
 flat=custom(m,'return normalize(float3(C.xy*.18,C.z));',{'C':nr});M.connect_material_property(flat,'',unreal.MaterialProperty.MP_NORMAL)
 scalar(m,.52,unreal.MaterialProperty.MP_ROUGHNESS);scalar(m,.28,unreal.MaterialProperty.MP_SPECULAR);overrides[name]=finish(m)
for a in A.get_all_level_actors():
 if a.get_actor_label()=='Architect_Finishes_v02':
  c=a.static_mesh_component
  for i in range(c.get_num_materials()):
   old=c.get_material(i)
   if old and old.get_name() in overrides:c.set_material(i,overrides[old.get_name()])
# Stacked narrow warm-gray stone, layered over the existing architectural pier.
m=base('M_StackedStone');p=node(m,unreal.MaterialExpressionWorldPosition)
code='''float row=floor(P.z/5.8);float shift=frac(sin(row*14.71)*413.13)*50;float x=abs(P.y+3024)<2?P.x:P.y;
 float col=floor((x+shift)/34);float h=frac(sin(row*47.3+col*117.1)*43758.5453);
 float2 f=float2(frac((x+shift)/34)*34,frac(P.z/5.8)*5.8);float edge=min(min(f.x,34-f.x),min(f.y,5.8-f.y));
 float joint=smoothstep(.12,.32,edge);float grain=sin(P.z*15+sin(x*.43)*2)*.024;
 return lerp(float3(.055,.048,.036),lerp(float3(.13,.112,.077),float3(.29,.265,.21),h)+grain,joint);'''
M.connect_material_property(custom(m,code,{'P':p}),'',unreal.MaterialProperty.MP_BASE_COLOR);scalar(m,.86,unreal.MaterialProperty.MP_ROUGHNESS);finish(m)
cube=unreal.load_asset('/Engine/BasicShapes/Cube')
for name,pos,scale in [('DD_StonePier_Front',(611.73,-3023.4,420),(2.786,.012,8.4)),('DD_StonePier_Left',(472.8,-3069,420),(.012,.91,8.4)),('DD_StonePier_Right',(750.65,-3069,420),(.012,.91,8.4))]:
 a=next((a for a in A.get_all_level_actors() if a.get_actor_label()==name),None)
 if not a:a=A.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*pos));a.set_actor_label(name)
 a.set_actor_location(unreal.Vector(*pos),False,False);a.set_actor_scale3d(unreal.Vector(*scale));a.static_mesh_component.set_static_mesh(cube);a.static_mesh_component.set_material(0,m);a.static_mesh_component.set_collision_profile_name('NoCollision')
L.save_current_level();(R/'round3_changes.json').write_text(json.dumps({'finish_material_overrides':list(overrides),'stone_pier':True},indent=2));unreal.log('ARCHITECTURE_REFINEMENT_COMPLETE')
