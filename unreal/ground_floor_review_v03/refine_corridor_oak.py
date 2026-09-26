"""Continuous corridor plank direction with filtered seams."""
import unreal,pathlib,json
R=pathlib.Path(__file__).parent
exec(compile((R/'material_helpers.py').read_text(),str(R/'material_helpers.py'),'exec'))
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert L.load_level('/Game/Campus/Maps/CampusCenter_GroundFloorReview_v05')
m=material('M_ContinuousCorridorOak');p=node(m,unreal.MaterialExpressionWorldPosition)
prefix='float2 q=(P.x<-2500 && P.y<-1622)?float2(-P.y,P.x):P.xy;float row=floor(q.y/18);float off=frac(sin(row*12.9898)*43758.5453)*108;float col=floor((q.x+off)/108);float h=frac(sin(row*78.233+col*41.37)*43758.5453);float2 f=float2(frac((q.x+off)/108),frac(q.y/18));'
uv=custom(m,prefix+'return f*float2(1,.18)+float2(h,frac(h*7.1));',{'P':p},F2)
s=sample(m,unreal.load_asset('/Game/Campus/PolishV03/Textures/Wood049_2K-JPG_Color'),uv)
code=prefix+'float edge=min(min(f.x,1-f.x)*108,min(f.y,1-f.y)*18);float aa=max(fwidth(edge),.025);float joint=smoothstep(.06-aa,.06+aa,edge);float g=saturate(dot(C,float3(.3,.59,.11))*1.75);float3 wood=lerp(float3(.23,.125,.059),float3(.53,.365,.205),g)*(.91+h*.16);return lerp(wood*.58,wood,joint);'
M.connect_material_property(custom(m,code,{'P':p,'C':s}),'',unreal.MaterialProperty.MP_BASE_COLOR)
M.connect_material_property(custom(m,prefix+'return .49+h*.06;',{'P':p},F1),'',unreal.MaterialProperty.MP_ROUGHNESS)
scalar(m,.28,unreal.MaterialProperty.MP_SPECULAR)
nr=sample(m,unreal.load_asset('/Game/Campus/PolishV03/Textures/Wood049_2K-JPG_NormalDX'),uv,True)
M.connect_material_property(custom(m,'return normalize(float3(C.xy*.07,C.z));',{'C':nr}),'',unreal.MaterialProperty.MP_NORMAL);finish(m)
changed=[]
for a in A.get_all_level_actors():
    if a.get_actor_label() in ['DD_GalleryFloor_Oak','DD_TrophyFloor_Oak','GF_CorridorOakConnector','GF_TrophyOakConnector','GF_GalleryOakEdge']:
        a.static_mesh_component.set_material(0,m);changed.append(a.get_actor_label())
L.save_current_level();(R/'corridor_changes.json').write_text(json.dumps({'actors':changed,'plank_cm':[108,18],'direction_change_only_at_trophy_corner':True},indent=2));unreal.log('CORRIDOR_OAK_SAVED')
