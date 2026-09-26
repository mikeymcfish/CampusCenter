"""Map-local physically scaled wall paint and lab floor, furniture untouched."""
import unreal,pathlib,json
R=pathlib.Path(__file__).parent;ROOT=R.parent
exec(compile((R/'material_helpers.py').read_text(),str(R/'material_helpers.py'),'exec'))
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert L.load_level('/Game/Campus/Maps/CampusCenter_GroundFloorReview_v05')
report={'overrides':[]}
# Restrained fine plaster response at a consistent world scale.
m=material('M_GroundWarmPlaster');p=node(m,unreal.MaterialExpressionWorldPosition);n=node(m,unreal.MaterialExpressionVertexNormalWS)
uv=custom(m,'return (abs(N.z)>.5?P.xy:(abs(N.x)>.5?P.yz:P.xz))/100.;',{'P':p,'N':n},F2)
s=sample(m,texture(ROOT,'painted_plaster_wall','BaseColor'),uv)
M.connect_material_property(custom(m,'float value=dot(C,float3(.3,.59,.11));return float3(.63,.625,.60)*(.96+.08*value);',{'C':s}),'',unreal.MaterialProperty.MP_BASE_COLOR)
scalar(m,.79,unreal.MaterialProperty.MP_ROUGHNESS);scalar(m,.22,unreal.MaterialProperty.MP_SPECULAR);finish(m)

epoxy=material('M_LabEpoxy');p=node(epoxy,unreal.MaterialExpressionWorldPosition)
uv=custom(epoxy,'return P.xy/240.;',{'P':p},F2)
s=sample(epoxy,texture(ROOT,'concrete_floor_02','BaseColor'),uv)
M.connect_material_property(custom(epoxy,'float value=dot(C,float3(.3,.59,.11));return float3(.19,.215,.225)*(.87+.26*value);',{'C':s}),'',unreal.MaterialProperty.MP_BASE_COLOR)
scalar(epoxy,.43,unreal.MaterialProperty.MP_ROUGHNESS);scalar(epoxy,.28,unreal.MaterialProperty.MP_SPECULAR);finish(epoxy)
for a in A.get_all_level_actors():
    if not isinstance(a,unreal.StaticMeshActor):continue
    label=a.get_actor_label();c=a.static_mesh_component
    for i in range(c.get_num_materials()):
        old=c.get_material(i)
        if not old:continue
        replacement=None
        if label.startswith('Architecture_Ground') and old.get_name()=='M_Warm_Painted_Plaster':replacement=m
        if label=='ILab_Designed_Details' and old.get_name()=='ILab_EpoxyFloor':replacement=epoxy
        if replacement:
            c.set_material(i,replacement);report['overrides'].append({'actor':label,'slot':i,'old':old.get_path_name(),'new':replacement.get_path_name()})
# Carry the CRI staggered ceramic pattern to the actual east/south wall lines.
tile=material('M_CRI_PerimeterTile');p=node(tile,unreal.MaterialExpressionWorldPosition)
code='''float row=floor((-P.y-70)/23.5);float shift=fmod(abs(row),2)*23.5;
float col=floor((P.x-18+shift)/47);float2 f=float2(frac((P.x-18+shift)/47),frac((-P.y-70)/23.5));
float h=frac(sin(dot(float2(row,col),float2(12.9898,78.233)))*43758.5453);
float2 e=min(f,1-f)*float2(47,23.5);float edge=min(e.x,e.y);float aa=max(fwidth(edge),.02);
float joint=smoothstep(.25-aa,.25+aa,edge);return lerp(float3(.21,.19,.16),float3(.029,.078,.17)*(.86+h*.25),joint);'''
M.connect_material_property(custom(tile,code,{'P':p}),'',unreal.MaterialProperty.MP_BASE_COLOR)
scalar(tile,.3,unreal.MaterialProperty.MP_ROUGHNESS);scalar(tile,.4,unreal.MaterialProperty.MP_SPECULAR);finish(tile)
cube=unreal.load_asset('/Engine/BasicShapes/Cube');actors={a.get_actor_label():a for a in A.get_all_level_actors()}
for label,x0,x1,y0,y1 in [('GF_CRI_EastPerimeter',1614,1644,35,1468),('GF_CRI_SouthPerimeter',18,1614,35,70)]:
    a=actors.get(label)
    if not a:a=A.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());a.set_actor_label(label)
    a.set_actor_location(unreal.Vector((x0+x1)/2,-(y0+y1)/2,1.4),False,False);a.set_actor_scale3d(unreal.Vector((x1-x0)/100,(y1-y0)/100,.008))
    c=a.static_mesh_component;c.set_static_mesh(cube);c.set_material(0,tile);c.set_collision_profile_name('NoCollision')
    report.setdefault('perimeter_extensions',[]).append(label)
L.save_current_level();(R/'surface_changes.json').write_text(json.dumps(report,indent=2));unreal.log('GROUND_SURFACES_SAVED')
