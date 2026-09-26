"""Round-two ground-floor lighting, floor scale and finish continuity."""
import unreal,pathlib,json
R=pathlib.Path(__file__).parent
ROOT=R.parent
exec(compile((R/'material_helpers.py').read_text(),str(R/'material_helpers.py'),'exec'))
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert L.load_level('/Game/Campus/Maps/CampusCenter_GroundFloorReview_v05')
report={'materials':[],'lights':[],'geometry':[],'hidden_shadows':[],'settings':[]}
actors={a.get_actor_label():a for a in A.get_all_level_actors()}
cube=unreal.load_asset('/Engine/BasicShapes/Cube')
def box(name,pos,dimensions,mat):
    a=actors.get(name)
    if not a:
        a=A.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*pos));a.set_actor_label(name);actors[name]=a
    a.set_actor_location(unreal.Vector(*pos),False,False);a.set_actor_scale3d(unreal.Vector(*(v/100 for v in dimensions)))
    c=a.static_mesh_component;c.set_static_mesh(cube);c.set_material(0,mat);c.set_collision_profile_name('NoCollision')
    report['geometry'].append(name);return a

# Travertine009 is 120cm square. Cut into 120x60cm slabs with 2mm joints.
m=material('M_HonedTravertine120x60');p=node(m,unreal.MaterialExpressionWorldPosition)
prefix='float2 q=P.xy;float2 cell=floor(q/float2(120,60));float h=frac(sin(dot(cell,float2(127.1,311.7)))*43758.5453);float2 f=frac(q/float2(120,60));'
uv=custom(m,prefix+'float2 local=f*float2(1,.5);if(h>.5)local=1-local;return local+float2(frac(h*7),frac(h*13));',{'P':p},F2)
s=sample(m,texture(ROOT,'Travertine009','BaseColor'),uv)
c=custom(m,prefix+'float2 edge=min(f,1-f)*float2(120,60);float e=min(edge.x,edge.y);float aa=max(fwidth(e),.035);float joint=smoothstep(.10-aa,.10+aa,e);float value=dot(C,float3(.3,.59,.11));float3 stone=lerp(float3(value,value,value),C,.65)*(.94+h*.12);return lerp(float3(.23,.215,.19),stone,joint);',{'P':p,'C':s})
M.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR)
n=sample(m,texture(ROOT,'Travertine009','NormalDX'),uv,True)
M.connect_material_property(custom(m,'return normalize(float3(C.xy*.10,C.z));',{'C':n}),'',unreal.MaterialProperty.MP_NORMAL)
scalar(m,.57,unreal.MaterialProperty.MP_ROUGHNESS);scalar(m,.25,unreal.MaterialProperty.MP_SPECULAR);finish(m)
actors['Commons_Honed_Floor'].static_mesh_component.set_material(0,m);report['materials'].append(m.get_path_name())

# Connect existing oak gallery and trophy corridor at the same elevation.
oak=unreal.load_asset('/Game/Campus/DisplayDecalsV02/ArchitectureMaterials/M_CorridorOakPlanks')
for name,x0,x1,y0,y1 in [('GF_CorridorOakConnector',-3017,-1145,1366,1622),('GF_TrophyOakConnector',-3017,-2585,1622,1655),('GF_GalleryOakEdge',-10,18,1002,1468)]:
    box(name,((x0+x1)/2,-(y0+y1)/2,1.6),(x1-x0,y1-y0,.8),oak)
trim=material('M_FloorTransitionBronze');color(trim,(.23,.19,.13),unreal.MaterialProperty.MP_BASE_COLOR);scalar(trim,.65,unreal.MaterialProperty.MP_METALLIC);scalar(trim,.36,unreal.MaterialProperty.MP_ROUGHNESS);finish(trim)
box('GF_GalleryBlueThreshold',(17,-1235,2.05),(2,466,.12),trim)
box('GF_TrophyNorthThreshold',(-2801,-2990,2.05),(432,2,.12),trim)

# Small, plausible ceiling luminaires. Each room light casts shadows; no wall leakage.
diffuser=material('M_LuminaireDiffuser');color(diffuser,(.8,.86,.9),unreal.MaterialProperty.MP_BASE_COLOR);color(diffuser,(4,4.15,4.3),unreal.MaterialProperty.MP_EMISSIVE_COLOR);scalar(diffuser,.6,unreal.MaterialProperty.MP_ROUGHNESS);finish(diffuser)
housing=material('M_LuminaireHousing');color(housing,(.12,.14,.16),unreal.MaterialProperty.MP_BASE_COLOR);scalar(housing,.65,unreal.MaterialProperty.MP_METALLIC);scalar(housing,.4,unreal.MaterialProperty.MP_ROUGHNESS);finish(housing)
def luminaire(name,x,y,z,lumens,width=60,height=60,radius=700):
    label='GF_Light_'+name;a=actors.get(label)
    if not a:
        a=A.spawn_actor_from_class(unreal.RectLight,unreal.Vector(x,y,z-4),unreal.Rotator(pitch=-90,yaw=0,roll=0));a.set_actor_label(label);actors[label]=a
    c=a.light_component;c.set_mobility(unreal.ComponentMobility.MOVABLE)
    c.set_editor_property('intensity_units',unreal.LightUnits.LUMENS);c.set_intensity(lumens);c.set_cast_shadows(True)
    for k,v in {'source_width':float(width-4),'source_height':float(height-4),'attenuation_radius':float(radius),'use_temperature':True,'temperature':4200.,'samples_per_pixel':16}.items():c.set_editor_property(k,v)
    box(label+'_Housing',(x,y,z),(width+4,height+4,3),housing)
    box(label+'_Diffuser',(x,y,z-1.8),(width,height,.5),diffuser)
    report['lights'].append({'name':label,'lumens':lumens,'position':[x,y,z]})

rooms=json.loads((R/'room_schedule.json').read_text())
levels={'100':(377,4500),'103':(398,4200),'104':(398,4200),'109':(398,3000),'111':(398,3500),'112':(398,5000),'118':(398,2500),'119':(398,4000),'120':(398,4500),'124':(423,4000),'125':(423,5000),'126':(423,4000),'127':(423,4000),'128':(423,3500),'129':(423,6000),'114':(398,3000)}
for r in rooms:
    if r['floor']=='GROUND' and r['number'] in levels:
        z,lm=levels[r['number']];x,y,_=r['center_mm'];luminaire(r['number'],x/10,-y/10,z,lm)
for i,(x,y) in enumerate([(-4260,-3060),(-3740,-3060),(-3200,-3060)]):luminaire('130_'+str(i),x,y,423,3500,120,30)
for i,(x,y) in enumerate([(1390,-1600),(1550,-1980)]):luminaire('Cafe_'+str(i),x,y,397,5000,120,30)
for i,(x,y) in enumerate([(-3480,-1900),(-3850,-2050)]):luminaire('Locker121_'+str(i),x,y,398,5000,120,30)
for row,y in enumerate([-2000,-2750,-3500,-4250]):
    for col,x in enumerate([-2200,-1300,-400]):luminaire('Gym_%s_%s'%(row,col),x,y,830,25000,120,60,1550)

# The existing gym slab receives a sports timber finish; no room/furniture geometry changes.
gym=material('M_GymSportsOak');p=node(gym,unreal.MaterialExpressionWorldPosition)
prefix='float2 q=float2(-P.y,P.x);float row=floor(q.y/7.5);float off=frac(sin(row*12.9898)*43758.5453)*120;float col=floor((q.x+off)/120);float h=frac(sin(row*78.233+col*41.37)*43758.5453);float2 f=float2(frac((q.x+off)/120),frac(q.y/7.5));'
uv=custom(gym,prefix+'return float2(f.x*.8+h,f.y*.08+frac(h*7));',{'P':p},F2)
s=sample(gym,unreal.load_asset('/Game/Campus/PolishV03/Textures/Wood049_2K-JPG_Color'),uv)
code=prefix+'''float g=saturate(dot(C,float3(.3,.59,.11))*1.7);float3 wood=lerp(float3(.24,.15,.07),float3(.61,.44,.24),g)*(.94+h*.12);
float edge=min(min(f.x,1-f.x)*120,min(f.y,1-f.y)*7.5);wood*=lerp(.7,1,smoothstep(0,.06,edge));
float2 a=abs(P.xy-float2(-1292.6,-3181));float courtMark=0;float aa=max(max(length(ddx(P.xy)),length(ddy(P.xy)))*.6,.4);
courtMark=max(courtMark,(1-smoothstep(max(0,2.5-aa),2.5+aa,abs(a.x-750)))*step(a.y,1402));
courtMark=max(courtMark,(1-smoothstep(max(0,2.5-aa),2.5+aa,abs(a.y-1400)))*step(a.x,752));
courtMark=max(courtMark,(1-smoothstep(max(0,2.5-aa),2.5+aa,a.y))*step(a.x,750));
courtMark=max(courtMark,1-smoothstep(max(0,2.5-aa),2.5+aa,abs(length(a)-180)));
courtMark=max(courtMark,(1-smoothstep(max(0,2.5-aa),2.5+aa,abs(a.x-245)))*step(820,a.y)*step(a.y,1400));
courtMark=max(courtMark,(1-smoothstep(max(0,2.5-aa),2.5+aa,abs(a.y-820)))*step(a.x,245));
return lerp(wood,float3(.035,.08,.15),courtMark);'''
M.connect_material_property(custom(gym,code,{'P':p,'C':s}),'',unreal.MaterialProperty.MP_BASE_COLOR)
scalar(gym,.4,unreal.MaterialProperty.MP_ROUGHNESS);scalar(gym,.3,unreal.MaterialProperty.MP_SPECULAR);finish(gym)
actors['Architecture_Ground_08_13'].static_mesh_component.set_material(0,gym);report['materials'].append(gym.get_path_name())

# Hidden entourage must not leave disembodied ground-floor silhouettes.
for a in A.get_all_level_actors():
    if a.get_actor_label()=='V8_Locker_area':a.light_component.set_intensity(4300)
    if isinstance(a,unreal.RectLight) and (a.get_actor_label()=='V8_Classroom_area' or a.get_actor_label().startswith('Wet_room_')):
        c=a.light_component
        original=c.intensity
        c.set_intensity(3400 if a.get_actor_label()=='V8_Classroom_area' else 1500)
        c.set_light_color(unreal.LinearColor(1,1,1,1));c.set_editor_property('temperature',5000.)
        report['lights'].append({'name':a.get_actor_label(),'original_intensity':original,'new_intensity':c.intensity})
    if isinstance(a,unreal.StaticMeshActor) and a.get_actor_label().startswith('Students_Ground'):
        c=a.static_mesh_component
        hidden=bool(a.get_editor_property('hidden')) or not c.get_editor_property('visible') or c.get_editor_property('hidden_in_game')
        report['hidden_shadows'].append({'actor':a.get_actor_label(),'hidden':hidden,'cast_hidden_shadow':c.get_editor_property('cast_hidden_shadow')})
        if hidden:c.set_cast_shadow(False);c.set_editor_property('cast_hidden_shadow',False)
    if isinstance(a,unreal.PostProcessVolume):
        s=a.settings
        for k,v in {'lumen_scene_lighting_quality':6.,'lumen_final_gather_quality':6.,'lumen_reflection_quality':4.,'local_exposure_shadow_contrast_scale':.8}.items():
            s.set_editor_property('override_'+k,True);s.set_editor_property(k,v)
        a.set_editor_property('settings',s)
        report['settings'].append({'actor':a.get_actor_label(),'min_exposure':s.get_editor_property('auto_exposure_min_brightness'),'max_exposure':s.get_editor_property('auto_exposure_max_brightness'),'bias':s.get_editor_property('auto_exposure_bias')})
L.save_current_level()
(R/'round2_changes.json').write_text(json.dumps(report,indent=2))
unreal.log('GROUND_FLOOR_ROUND2_SAVED')
