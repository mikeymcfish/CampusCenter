import unreal,json,pathlib
R=pathlib.Path(__file__).parent;E=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;T=unreal.AssetToolsHelpers.get_asset_tools()
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
source='/Game/Campus/Maps/CampusCenter_Dusk_ArchitectFinishes_v03';target='/Game/Campus/Maps/CampusCenter_ArchitectDecals_v04';D='/Game/Campus/DisplayDecalsV02'
if not E.does_asset_exist(target):assert E.duplicate_asset(source,target)
assert L.load_level(target)
for a in list(A.get_all_level_actors()):
 if a.get_actor_label().startswith('DD_'):A.destroy_actor(a)
geometry=D+'/GeometryV03'
if not E.does_directory_exist(geometry+'/Decal_Display_Layer'):
 t=unreal.AssetImportTask();t.filename=str(R/'Decal_Display_Layer.glb');t.destination_path=geometry;t.automated=True;t.save=True;T.import_asset_tasks([t])
materials={};report={'map':target,'decals':[],'meshes':[],'lights':[]}
for item in json.loads((R/'asset_inventory.json').read_text()):
 name='T_Decal_%02d'%item['id'];path=D+'/Textures/'+name
 if not E.does_asset_exist(path):
  t=unreal.AssetImportTask();t.filename=str(R/item['file']);t.destination_path=D+'/Textures';t.destination_name=name;t.automated=True;t.save=True;T.import_asset_tasks([t])
 tex=unreal.load_asset(path);assert tex
 tex.set_editor_property('srgb',True);tex.set_editor_property('max_texture_size',2048);E.save_loaded_asset(tex)
 name='M_Decal_%02d'%item['id'];path=D+'/Materials/'+name
 m=unreal.load_asset(path) if E.does_asset_exist(path) else T.create_asset(name,D+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
 m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_MASKED);m.set_editor_property('two_sided',True);m.set_editor_property('opacity_mask_clip_value',.22)
 M.delete_all_material_expressions(m)
 def node(c):return M.create_material_expression(m,c)
 uv=node(unreal.MaterialExpressionTextureCoordinate);u,v,w,h=item['crop_uv'];uv.u_tiling=w;uv.v_tiling=h
 offset=node(unreal.MaterialExpressionConstant2Vector);offset.r=u;offset.g=v
 add=node(unreal.MaterialExpressionAdd);M.connect_material_expressions(uv,'',add,'A');M.connect_material_expressions(offset,'',add,'B')
 sample=node(unreal.MaterialExpressionTextureSample);sample.texture=tex;M.connect_material_expressions(add,'',sample,'UVs')
 M.connect_material_property(sample,'RGB',unreal.MaterialProperty.MP_BASE_COLOR);M.connect_material_property(sample,'A',unreal.MaterialProperty.MP_OPACITY_MASK)
 rough=node(unreal.MaterialExpressionConstant);rough.r=.68 if item['category']=='artwork' else .42;M.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
 M.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_NANITE);M.recompile_material(m);E.save_loaded_asset(m);materials[item['id']]=m
for p in E.list_assets(geometry+'/Decal_Display_Layer',True):
 mesh=unreal.load_asset(p)
 if not isinstance(mesh,unreal.StaticMesh):continue
 label=mesh.get_name();a=A.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0));a.set_actor_label(label);a.set_folder_path('Architecture/Artwork and trophies')
 c=a.static_mesh_component;c.set_static_mesh(mesh);c.set_collision_profile_name('NoCollision');c.set_editor_property('disallow_nanite',True)
 if label.startswith('DD_Artwork_') or label.startswith('DD_Trophy_') and label[-2:].isdigit():
  idx=int(label[-2:]);c.set_material(0,materials[idx]);c.set_cast_shadow(False)
  if label.startswith('DD_Trophy_'):a.set_actor_location(unreal.Vector(-1.2,0,0),False,False)
  report['decals'].append({'label':label,'id':idx,'material':materials[idx].get_path_name()})
 report['meshes'].append(label)
def light(label,loc,rot,intensity,width,height):
 a=A.spawn_actor_from_class(unreal.RectLight,unreal.Vector(*loc),unreal.Rotator(pitch=rot[0],yaw=rot[1],roll=0));a.set_actor_label(label)
 c=a.light_component;c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_intensity(intensity);c.set_editor_property('source_width',width);c.set_editor_property('source_height',height);c.set_editor_property('attenuation_radius',650.0);c.set_editor_property('use_temperature',True);c.set_editor_property('temperature',5000.0);c.set_editor_property('samples_per_pixel',8);report['lights'].append(label)
for i,x in enumerate([-990,-590,-190]):light('DD_Gallery_Wash_%d'%i,(x,-1350,310),(-20,-90),850,210,75)
for i,y in enumerate([-1880,-2290,-2700]):light('DD_Trophy_Wash_%d'%i,(-2870,y,300),(-20,0),700,210,65)
assert len(report['decals'])==19,report
L.save_current_level();(R/'installation.json').write_text(json.dumps(report,indent=2));unreal.log('DISPLAY_DECALS_INSTALLED')
