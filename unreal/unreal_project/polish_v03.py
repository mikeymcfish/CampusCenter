import unreal,pathlib,json
root=pathlib.Path(unreal.Paths.project_dir()); edit=unreal.MaterialEditingLibrary
at=unreal.AssetToolsHelpers.get_asset_tools(); dest='/Game/Campus/PolishV03'
report={'materials':[],'slots':0,'maps':[],'unsupported':[]}
def tex(kind):
 name='Wood049_2K-JPG_'+kind
 t=unreal.load_asset(dest+'/Textures/'+name)
 if not t:
  task=unreal.AssetImportTask(); task.filename=str(root.parent/'polish_v03/assets/Wood049'/(name+'.jpg'));task.destination_path=dest+'/Textures';task.automated=True;task.save=True
  at.import_asset_tasks([task]);t=unreal.load_asset(task.imported_object_paths[0])
 if kind=='NormalDX':t.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_NORMALMAP);t.set_editor_property('srgb',False)
 if kind=='Roughness':t.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_MASKS);t.set_editor_property('srgb',False)
 unreal.EditorAssetLibrary.save_loaded_asset(t);return t
maps={k:tex(k) for k in ['Color','NormalDX','Roughness']}
def wood(name,roughlow,roughhigh,strength):
 m=unreal.load_asset(dest+'/Materials/'+name) or at.create_asset(name,dest+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
 edit.delete_all_material_expressions(m)
 def node(c):return edit.create_material_expression(m,c)
 def scalar(v):n=node(unreal.MaterialExpressionConstant);n.r=v;return n
 def wire(a,o,b,i):edit.connect_material_expressions(a,o,b,i)
 def prop(a,o,p):edit.connect_material_property(a,o,p)
 uv=node(unreal.MaterialExpressionTextureCoordinate);uv.u_tiling=3;uv.v_tiling=1.5
 samples={}
 for k,t in maps.items():
  n=node(unreal.MaterialExpressionTextureSample);n.texture=t
  if k=='NormalDX':n.sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL
  if k=='Roughness':n.sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_MASKS
  wire(uv,'',n,'UVs');samples[k]=n
 prop(samples['Color'],'',unreal.MaterialProperty.MP_BASE_COLOR)
 rough=node(unreal.MaterialExpressionLinearInterpolate);wire(scalar(roughlow),'',rough,'A');wire(scalar(roughhigh),'',rough,'B');wire(samples['Roughness'],'R',rough,'Alpha');prop(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
 flat=node(unreal.MaterialExpressionConstant3Vector);flat.constant=unreal.LinearColor(0,0,1,1)
 norm=node(unreal.MaterialExpressionLinearInterpolate);wire(flat,'',norm,'A');wire(samples['NormalDX'],'',norm,'B');wire(scalar(strength),'',norm,'Alpha');prop(norm,'',unreal.MaterialProperty.MP_NORMAL)
 prop(scalar(.35),'',unreal.MaterialProperty.MP_SPECULAR)
 edit.recompile_material(m);unreal.EditorAssetLibrary.save_loaded_asset(m);report['materials'].append(m.get_path_name());return m
oak=wood('M_Natural_Oak_PBR',.32,.58,.2)
ceiling=wood('M_Ceiling_Oak_PBR',.52,.76,.12)
for p in unreal.EditorAssetLibrary.list_assets('/Game/Campus/Imported',recursive=True):
 mesh=unreal.load_asset(p)
 if not isinstance(mesh,unreal.StaticMesh):continue
 changed=False
 for i,slot in enumerate(mesh.static_materials):
  name=slot.material_interface.get_name() if slot.material_interface else ''
  replacement=oak if name in ['Natural_oak','M_Natural_Oak_PBR'] else ceiling if name in ['Acoustic_panel_neutral','M_Ceiling_Oak_PBR'] else None
  if replacement:mesh.set_material(i,replacement);report['slots']+=1;changed=True
 if changed:unreal.EditorAssetLibrary.save_loaded_asset(mesh)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for path in unreal.EditorAssetLibrary.list_assets('/Game/Campus/Maps',recursive=True):
 if not path.endswith('.'+path.split('/')[-1].split('.')[0]):continue
 if not levels.load_level(path.split('.')[0]):continue
 count=0
 for a in actors.get_all_level_actors():
  if isinstance(a,unreal.RectLight):
   c=a.light_component;c.set_editor_property('temperature',4200.0);c.set_editor_property('attenuation_radius',850.0);count+=1
  if isinstance(a,unreal.PostProcessVolume):
   s=a.settings
   values={'auto_exposure_min_brightness':6.0,'auto_exposure_max_brightness':10.0,'auto_exposure_bias':.2,'auto_exposure_speed_up':2.,'auto_exposure_speed_down':1.,'bloom_intensity':.08,'bloom_threshold':2.,'vignette_intensity':.12,'motion_blur_amount':0.,'scene_fringe_intensity':0.,'film_grain_intensity':0.,'lumen_scene_lighting_quality':1.5,'lumen_final_gather_quality':1.5,'lumen_reflection_quality':1.5,'local_exposure_highlight_contrast_scale':.8,'local_exposure_shadow_contrast_scale':.9}
   for key,v in values.items():
    try:s.set_editor_property('override_'+key,True);s.set_editor_property(key,v)
    except Exception as e:report['unsupported'].append({'property':key,'error':str(e)})
   a.set_editor_property('settings',s)
 levels.save_current_level();report['maps'].append({'map':path,'rect_lights':count})
(root/'polish_v03_report.json').write_text(json.dumps(report,indent=2))
unreal.log('POLISH_V03_SAVED')



