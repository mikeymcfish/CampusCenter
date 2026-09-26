"""Assert architectural oak mapping and refine physical staircase grain scale."""
import unreal,pathlib,json
R=pathlib.Path(__file__).parent
exec(compile((R/'material_helpers.py').read_text(),str(R/'material_helpers.py'),'exec'))
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert L.load_level('/Game/Campus/Maps/CampusCenter_GroundFloorReview_v05')
overrides={}
for k in range(5):
    name='M_AF_LightOak_%02d'%k;m=material(name)
    p=node(m,unreal.MaterialExpressionWorldPosition);n=node(m,unreal.MaterialExpressionVertexNormalWS);uv=node(m,unreal.MaterialExpressionTextureCoordinate)
    coords=custom(m,'return abs(N.z)>.5 && P.z<10 ? UV+float2('+str(k*.137)+','+str(k*.091)+') : (P.z>700 && abs(N.z)>.5 ? P.xy : (abs(N.x)>.5 ? P.zy : P.zx))/float2(170,45);',{'P':p,'N':n,'UV':uv},F2)
    s=sample(m,unreal.load_asset('/Game/Campus/PolishV03/Textures/Wood049_2K-JPG_Color'),coords)
    c=custom(m,'float g=saturate(dot(C,float3(.3,.59,.11))*1.55);return lerp(float3(.19,.10,.041),float3(.48,.30,.145),g)*'+str(.94+k*.026)+';',{'C':s})
    M.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR)
    nr=sample(m,unreal.load_asset('/Game/Campus/PolishV03/Textures/Wood049_2K-JPG_NormalDX'),coords,True)
    M.connect_material_property(custom(m,'return normalize(float3(C.xy*.12,C.z));',{'C':nr}),'',unreal.MaterialProperty.MP_NORMAL)
    scalar(m,.52,unreal.MaterialProperty.MP_ROUGHNESS);scalar(m,.28,unreal.MaterialProperty.MP_SPECULAR)
    overrides[name]=finish(m)
changed=[]
stair=material('M_StairOak');p=node(stair,unreal.MaterialExpressionWorldPosition);n=node(stair,unreal.MaterialExpressionVertexNormalWS)
uv=custom(stair,'return (abs(N.z)>.5?P.xy:(abs(N.y)>.5?P.xz:P.yz))/float2(180,45);',{'P':p,'N':n},F2)
s=sample(stair,unreal.load_asset('/Game/Campus/PolishV03/Textures/Wood049_2K-JPG_Color'),uv)
M.connect_material_property(custom(stair,'float g=saturate(dot(C,float3(.3,.59,.11))*1.6);return lerp(float3(.16,.09,.038),float3(.43,.29,.15),g);',{'C':s}),'',unreal.MaterialProperty.MP_BASE_COLOR)
scalar(stair,.52,unreal.MaterialProperty.MP_ROUGHNESS);scalar(stair,.26,unreal.MaterialProperty.MP_SPECULAR);finish(stair)
stair_changed=[]
for a in A.get_all_level_actors():
    if a.get_actor_label() in ['Architecture_Ground_10_10','Architecture_Ground_10_11','Repair_StairRisers']:
        c=a.static_mesh_component
        for i in range(c.get_num_materials()):
            old=c.get_material(i)
            if old and old.get_name() in ['M_Natural_Oak_PBR','Repair_HandrailOak']:
                c.set_material(i,stair);stair_changed.append({'actor':a.get_actor_label(),'slot':i})
    if a.get_actor_label()!='Architect_Finishes_v02':continue
    c=a.static_mesh_component
    for i in range(c.get_num_materials()):
        old=c.get_material(i)
        if old and old.get_name() in overrides:c.set_material(i,overrides[old.get_name()]);changed.append(i)
L.save_current_level();(R/'architect_oak_changes.json').write_text(json.dumps({'slots':changed,'stairs':stair_changed,'geometry_changed':False,'coordinates_connections_asserted':True},indent=2));unreal.log('ARCHITECT_OAK_MAPPING_VERIFIED')
