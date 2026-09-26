"""Native map-local material helpers. Never edit source/shared materials."""
import unreal
E=unreal.EditorAssetLibrary
M=unreal.MaterialEditingLibrary
T=unreal.AssetToolsHelpers.get_asset_tools()
D='/Game/Campus/GroundFloorV03'
F1=unreal.CustomMaterialOutputType.CMOT_FLOAT1
F2=unreal.CustomMaterialOutputType.CMOT_FLOAT2
F3=unreal.CustomMaterialOutputType.CMOT_FLOAT3
def material(name):
    m=unreal.load_asset(D+'/Materials/'+name) or T.create_asset(name,D+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
    M.delete_all_material_expressions(m)
    return m
def node(m,cls):return M.create_material_expression(m,cls)
def custom(m,code,inputs,typ=F3):
    n=node(m,unreal.MaterialExpressionCustom)
    n.set_editor_property('code',code);n.set_editor_property('output_type',typ)
    ins=[]
    for name in inputs:
        i=unreal.CustomInput();i.set_editor_property('input_name',name);ins.append(i)
    n.set_editor_property('inputs',ins)
    for name,src in inputs.items():
        assert M.connect_material_expressions(src,'RGB' if isinstance(src,unreal.MaterialExpressionTextureSample) else '',n,name),name
    return n
def scalar(m,value,prop):
    n=node(m,unreal.MaterialExpressionConstant);n.r=value;M.connect_material_property(n,'',prop)
def color(m,value,prop):
    n=node(m,unreal.MaterialExpressionConstant3Vector);n.constant=unreal.LinearColor(*value,1);M.connect_material_property(n,'',prop)
def finish(m):
    M.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_NANITE);M.recompile_material(m);E.save_loaded_asset(m);return m
def texture(root,asset,kind):
    name=asset+'_'+kind
    t=unreal.load_asset(D+'/Textures/'+name)
    if not t:
        source=root/'realism_assets/prepared/materials'/asset/(kind+'.png')
        if not source.exists():source=root/'ground_floor_review_v03/source_materials'/asset/(kind+'.png')
        task=unreal.AssetImportTask();task.filename=str(source)
        task.destination_path=D+'/Textures';task.destination_name=name;task.automated=True;task.save=True
        T.import_asset_tasks([task]);assert task.imported_object_paths
        t=unreal.load_asset(task.imported_object_paths[0])
    if kind=='NormalDX':t.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_NORMALMAP);t.set_editor_property('srgb',False)
    if kind=='ORM':t.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_MASKS);t.set_editor_property('srgb',False)
    E.save_loaded_asset(t);return t
def sample(m,t,uv,normal=False):
    n=node(m,unreal.MaterialExpressionTextureSample);n.texture=t
    if normal:n.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    # Empty input explicitly selects TextureSample input0 (coordinates); UE's
    # scripting API shortens the displayed name to UVs, unlike the C++ property.
    assert M.connect_material_expressions(uv,'',n,''),'Texture coordinate connection failed'
    return n
