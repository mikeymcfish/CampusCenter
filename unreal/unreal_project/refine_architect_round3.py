"""Scoped finish materials, canopy mesh, and reference viewing light on the copied map."""
import unreal, pathlib, json
root=pathlib.Path(unreal.Paths.project_dir())
ed=unreal.EditorAssetLibrary; me=unreal.MaterialEditingLibrary
at=unreal.AssetToolsHelpers.get_asset_tools()
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level('/Game/Campus/Maps/CampusCenter_Dusk_ArchitectFinishes_v03')
dest='/Game/Campus/ArchitectFinishesV04'
if not ed.does_directory_exist(dest+'/Architect_Finishes_v04'):
 task=unreal.AssetImportTask();task.filename=str(root.parent/'architect_finishes_v01/Architect_Finishes_v04.glb');task.destination_path=dest;task.automated=True;task.save=True
 at.import_asset_tasks([task])
meshes=[unreal.load_asset(p) for p in ed.list_assets(dest,recursive=True)]
mesh=next(a for a in meshes if isinstance(a,unreal.StaticMesh))
report={'materials':[], 'lights':[], 'nanite_fixes':[]}
for index,slot in enumerate(mesh.static_materials):
 name=slot.material_interface.get_name()
 m=unreal.load_asset(dest+'/NativeMaterials/M_'+name) if ed.does_asset_exist(dest+'/NativeMaterials/M_'+name) else at.create_asset('M_'+name,dest+'/NativeMaterials',unreal.Material,unreal.MaterialFactoryNew())
 me.delete_all_material_expressions(m)
 def node(c):return me.create_material_expression(m,c)
 def scalar(v):n=node(unreal.MaterialExpressionConstant);n.r=v;return n
 def wire(a,b,p):me.connect_material_expressions(a,'',b,p)
 def custom(code,typ=unreal.CustomMaterialOutputType.CMOT_FLOAT3):
  n=node(unreal.MaterialExpressionCustom);n.set_editor_property('code',code);n.set_editor_property('output_type',typ)
  inputs=[]
  for label in ['P','N']:
   ci=unreal.CustomInput();ci.set_editor_property('input_name',label);inputs.append(ci)
  n.set_editor_property('inputs',inputs)
  wire(node(unreal.MaterialExpressionWorldPosition),n,'P');wire(node(unreal.MaterialExpressionVertexNormalWS),n,'N');return n
 # World coordinates are centimeters: finish scale stays constant across all surfaces.
 prefix='float2 uv=abs(N.z)>.5?P.xy:P.yz; '
 rough=.62
 if 'LightOak' in name:
  code=prefix+'float g=sin(uv.y*2.1+sin(uv.x*.075)*2.0)*.018+sin(uv.y*12.0+sin(uv.x*.13))*.009; return float3(.56,.405,.25)+g;'
 elif 'PerforatedWalnut' in name:
  code=prefix+'float2 q=frac(uv/0.9)-.5; float d=length(q); float aa=max(fwidth(d),.02); float hole=1-smoothstep(.19-aa,.19+aa,d); float grain=sin(uv.y*8+sin(uv.x*.1))*.015; return lerp(float3(.32,.205,.115)+grain,float3(.035,.026,.018),hole);'
 elif 'BlueTile_' in name:
  k=int(name[-2:]); code=prefix+f'float v=sin(uv.x*.14)*sin(uv.y*.19)*.006; return float3({.052+k*.004},{.125+k*.005},{.255+k*.007})+v;';rough=.38
 elif 'KingBlue' in name:code='return float3(.025,.16,.48);';rough=.48
 elif 'WarmWhite' in name:code='return float3(.83,.82,.78);';rough=.85
 elif 'Cork' in name:code=prefix+'float g=frac(sin(dot(floor(uv*7),float2(12.9898,78.233)))*43758.5453);return float3(.39,.29,.18)*(0.85+g*.3);';rough=.95
 elif 'Grout' in name:code='return float3(.28,.255,.205);';rough=.9
 else:code='return float3(.065,.054,.038);';rough=.9
 if 'LightOak' in name:
  coords=custom('return abs(N.z)>.5 && P.z<10 ? P.xy/float2(108,18) : P.zy/float2(150,45);',unreal.CustomMaterialOutputType.CMOT_FLOAT2)
  # The parquet carries per-plank UVs, preserving the alternating grain direction.
  uv=node(unreal.MaterialExpressionTextureCoordinate)
  ci=unreal.CustomInput();ci.set_editor_property('input_name','UV')
  ins=list(coords.get_editor_property('inputs'));ins.append(ci);coords.set_editor_property('inputs',ins)
  coords.set_editor_property('code','return abs(N.z)>.5 && P.z<10 ? UV : P.zy/float2(150,45);');wire(uv,coords,'UV')
  sample=node(unreal.MaterialExpressionTextureSample);sample.texture=unreal.load_asset('/Game/Campus/PolishV03/Textures/Wood049_2K-JPG_Color');wire(coords,sample,'UVs')
  color=custom('float g=saturate(dot(C,float3(.3,.59,.11))*2.0);return lerp(float3(.34,.225,.12),float3(.56,.40,.235),g);')
  ci=unreal.CustomInput();ci.set_editor_property('input_name','C');ins=list(color.get_editor_property('inputs'));ins.append(ci);color.set_editor_property('inputs',ins);wire(sample,color,'C')
  me.connect_material_property(color,'',unreal.MaterialProperty.MP_BASE_COLOR)
 else:me.connect_material_property(custom(code),'',unreal.MaterialProperty.MP_BASE_COLOR)
 me.connect_material_property(scalar(rough),'',unreal.MaterialProperty.MP_ROUGHNESS)
 me.connect_material_property(scalar(.3),'',unreal.MaterialProperty.MP_SPECULAR)
 me.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_NANITE)
 me.recompile_material(m);ed.save_loaded_asset(m);mesh.set_material(index,m);report['materials'].append(m.get_path_name())
ed.save_loaded_asset(mesh)
for a in actors.get_all_level_actors():
 if a.get_actor_label()=='Architect_Finishes_v02':a.static_mesh_component.set_static_mesh(mesh)
 if isinstance(a,unreal.DirectionalLight):
  c=a.light_component;c.set_light_color(unreal.LinearColor(1,.96,.89,1));c.set_intensity(5.0);c.set_editor_property('use_temperature',False)
  a.set_actor_rotation(unreal.Rotator(pitch=-38,yaw=-35,roll=0),False);report['lights'].append(a.get_actor_label())
 if isinstance(a,unreal.SkyLight):
  a.light_component.set_intensity(2.0);a.light_component.set_light_color(unreal.LinearColor(.84,.91,1,1))
 if isinstance(a,unreal.RectLight):
  a.light_component.set_editor_property('temperature',5600.0); a.light_component.set_intensity(a.light_component.intensity*.55)
 if isinstance(a,unreal.PostProcessVolume):
  s=a.settings
  for k,v in {'auto_exposure_bias':.35,'white_temp':6500.0,'vignette_intensity':0.0}.items():
   s.set_editor_property('override_'+k,True);s.set_editor_property(k,v)
  a.set_editor_property('settings',s)
 if isinstance(a,unreal.StaticMeshActor):
  c=a.static_mesh_component
  if any(c.get_material(i) and 'Glass' in c.get_material(i).get_name() for i in range(c.get_num_materials())):
   c.set_editor_property('disallow_nanite',True);report['nanite_fixes'].append(a.get_actor_label())
fill=next((a for a in actors.get_all_level_actors() if a.get_actor_label()=='Architect_CRI_SoftFill'),None)
if fill is None:
 fill=actors.spawn_actor_from_class(unreal.RectLight,unreal.Vector(820,-720,360),unreal.Rotator(pitch=-90,yaw=0,roll=0));fill.set_actor_label('Architect_CRI_SoftFill')
c=fill.light_component;c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_intensity(3500);c.set_editor_property('source_width',1100.0);c.set_editor_property('source_height',950.0);c.set_editor_property('attenuation_radius',2200.0);c.set_editor_property('temperature',5600.0)
levels.save_current_level()
(root.parent/'architect_finishes_v01/round3_changes.json').write_text(json.dumps(report,indent=2))
unreal.log('ARCHITECT_ROUND3_COMPLETE')
