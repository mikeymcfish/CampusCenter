"""Final ranked finish refinements; preserve all existing furniture and decals."""
import pathlib,json,unreal
R=pathlib.Path(__file__).parent;ROOT=R.parent
exec(compile((R/'material_helpers.py').read_text(),str(R/'material_helpers.py'),'exec'))
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert L.load_level('/Game/Campus/Maps/CampusCenter_GroundFloorReview_v05')
report={'door_slots':[],'materials':[],'lighting':[],'grout_slots':[],'project_quality_settings':{'r.Shadow.Virtual.SMRT.RayCountLocal':64,'r.Shadow.Virtual.SMRT.AdaptiveRayCount':0,'r.Lumen.ScreenProbeGather.ShortRangeAO.DownsampleFactor':1}}
grout=material('M_BlueFloorGrout');color(grout,(.10,.087,.065),unreal.MaterialProperty.MP_BASE_COLOR)
scalar(grout,.86,unreal.MaterialProperty.MP_ROUGHNESS);scalar(grout,.18,unreal.MaterialProperty.MP_SPECULAR);finish(grout)
for a in A.get_all_level_actors():
    if a.get_actor_label()=='Architect_Finishes_v02':
        c=a.static_mesh_component
        for i in range(c.get_num_materials()):
            if c.get_material(i).get_name()=='M_AF_BlueTileGrout':c.set_material(i,grout);report['grout_slots'].append(i)
# Match the narrow new perimeter infill to the same muted grout.
perimeter=material('M_CRI_PerimeterTile');p=node(perimeter,unreal.MaterialExpressionWorldPosition)
code='''float row=floor((-P.y-70)/23.5);float shift=fmod(abs(row),2)*23.5;
float col=floor((P.x-18+shift)/47);float2 f=float2(frac((P.x-18+shift)/47),frac((-P.y-70)/23.5));
float h=frac(sin(dot(float2(row,col),float2(12.9898,78.233)))*43758.5453);
float2 e=min(f,1-f)*float2(47,23.5);float edge=min(e.x,e.y);float aa=max(fwidth(edge),.02);
return lerp(float3(.10,.087,.065),float3(.029,.078,.17)*(.86+h*.25),smoothstep(.25-aa,.25+aa,edge));'''
M.connect_material_property(custom(perimeter,code,{'P':p}),'',unreal.MaterialProperty.MP_BASE_COLOR)
scalar(perimeter,.3,unreal.MaterialProperty.MP_ROUGHNESS);scalar(perimeter,.4,unreal.MaterialProperty.MP_SPECULAR);finish(perimeter)
# Architectural door veneer: vertical, restrained grain, world dimensions in cm.
oak=material('M_GroundDoorOak');p=node(oak,unreal.MaterialExpressionWorldPosition);n=node(oak,unreal.MaterialExpressionVertexNormalWS)
uv=custom(oak,'return float2(P.z,abs(N.x)>.5?P.y:P.x)/float2(210,55);',{'P':p,'N':n},F2)
s=sample(oak,unreal.load_asset('/Game/Campus/PolishV03/Textures/Wood049_2K-JPG_Color'),uv)
M.connect_material_property(custom(oak,'float g=saturate(dot(C,float3(.3,.59,.11))*1.5);return lerp(float3(.29,.20,.115),float3(.43,.32,.20),g);',{'C':s}),'',unreal.MaterialProperty.MP_BASE_COLOR)
scalar(oak,.53,unreal.MaterialProperty.MP_ROUGHNESS);scalar(oak,.25,unreal.MaterialProperty.MP_SPECULAR);finish(oak)
for a in A.get_all_level_actors():
    if isinstance(a,unreal.StaticMeshActor) and a.get_actor_label().startswith('Doors_Ground_'):
        c=a.static_mesh_component
        for i in range(c.get_num_materials()):
            if c.get_material(i).get_name()=='M_Natural_Oak_PBR':c.set_material(i,oak);report['door_slots'].append({'actor':a.get_actor_label(),'slot':i})
# Keep 120x60cm slab layout, soften exaggerated veins and decorrelate each slab.
m=material('M_HonedTravertine120x60');p=node(m,unreal.MaterialExpressionWorldPosition)
prefix='float2 cell=floor(P.xy/float2(120,60));float h=frac(sin(dot(cell,float2(127.1,311.7)))*43758.5453);float2 f=frac(P.xy/float2(120,60));'
uv=custom(m,prefix+'float2 local=f*float2(1,.5);if(h>.5)local=1-local;return local+float2(frac(h*7),frac(h*13));',{'P':p},F2)
s=sample(m,texture(ROOT,'Travertine009','BaseColor'),uv)
code=prefix+'float2 edge=min(f,1-f)*float2(120,60);float e=min(edge.x,edge.y);float aa=max(fwidth(e),.035);float joint=smoothstep(.1-aa,.1+aa,e);float v=dot(C,float3(.3,.59,.11));float3 stone=lerp(float3(.43,.415,.38),lerp(v.xxx,C,.45),.28)*(.94+h*.12);return lerp(float3(.29,.28,.25),stone,joint);'
M.connect_material_property(custom(m,code,{'P':p,'C':s}),'',unreal.MaterialProperty.MP_BASE_COLOR)
scalar(m,.60,unreal.MaterialProperty.MP_ROUGHNESS);scalar(m,.24,unreal.MaterialProperty.MP_SPECULAR);finish(m)
report['materials']=[oak.get_path_name(),m.get_path_name(),grout.get_path_name(),perimeter.get_path_name()]
# Narrow the largest artificial sources to reduce excessively broad noisy penumbrae.
for a in A.get_all_level_actors():
    if isinstance(a,unreal.RectLight) and a.get_actor_label().startswith('GF_Light_'):
        c=a.light_component
        c.set_editor_property('source_width',min(float(c.get_editor_property('source_width')),60.))
        c.set_editor_property('source_height',min(float(c.get_editor_property('source_height')),30.))
        report['lighting'].append(a.get_actor_label())
L.save_current_level();(R/'round4_changes.json').write_text(json.dumps(report,indent=2));unreal.log('GROUND_FLOOR_ROUND4_SAVED')
