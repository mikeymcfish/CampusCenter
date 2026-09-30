"""Run inside UE 5.8 Editor via Apply_Student_Art.cmd, never ordinary Python."""
import hashlib
import json
import pathlib
import traceback
import unreal

ROOT = pathlib.Path(__file__).resolve().parent
CONFIG = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
REPORT = ROOT / 'apply_report.json'
ED = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
LEVELS = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ACTORS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
TAG = 'CampusStudentArtV01'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def make_material(item):
    name = 'T_' + item['id']
    task = unreal.AssetImportTask()
    task.set_editor_property('filename', str(ROOT / item['texture']))
    task.set_editor_property('destination_path', CONFIG['asset_root'])
    task.set_editor_property('destination_name', name)
    task.set_editor_property('automated', True)
    task.set_editor_property('replace_existing', True)
    task.set_editor_property('save', True)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    texture = unreal.load_asset(CONFIG['asset_root'] + '/' + name)
    require(isinstance(texture, unreal.Texture2D), 'Texture import failed: ' + name)
    texture.set_editor_property('srgb', True)
    texture.set_editor_property('address_x', unreal.TextureAddress.TA_CLAMP)
    texture.set_editor_property('address_y', unreal.TextureAddress.TA_CLAMP)
    require(ED.save_loaded_asset(texture), 'Could not save texture')
    name = 'M_' + item['id']
    material = unreal.load_asset(CONFIG['asset_root'] + '/' + name)
    if material is None:
        material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            name, CONFIG['asset_root'], unreal.Material, unreal.MaterialFactoryNew())
    require(isinstance(material, unreal.Material), 'Material creation failed: ' + name)
    MEL.delete_all_material_expressions(material)
    material.set_editor_property('material_domain', unreal.MaterialDomain.MD_DEFERRED_DECAL)
    material.set_editor_property('blend_mode', unreal.BlendMode.BLEND_TRANSLUCENT)
    uv = MEL.create_material_expression(material, unreal.MaterialExpressionTextureCoordinate, -700, 0)
    sample = MEL.create_material_expression(material, unreal.MaterialExpressionTextureSample, -450, -150)
    sample.set_editor_property('texture', texture)
    require(MEL.connect_material_expressions(uv, '', sample, 'UVs'), 'UV connection failed')
    require(MEL.connect_material_property(sample, 'RGB', unreal.MaterialProperty.MP_BASE_COLOR), 'Color connection failed')
    # Explicit rectangular opacity removes generated halos/background without modifying artwork pixels.
    # Generated alpha is deliberately not used: it contains ragged edges and one opaque backdrop.
    mask = MEL.create_material_expression(material, unreal.MaterialExpressionCustom, -400, 200)
    custom_input = unreal.CustomInput()
    custom_input.set_editor_property('input_name', 'UV')
    mask.set_editor_property('inputs', [custom_input])
    mask.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    mask.set_editor_property('description', 'Artwork and white label only; transparent elsewhere')
    width, height = item['size_px']
    terms = []
    for rect in (item['art_rect_px'], item['label_rect_px']):
        x0, y0, x1, y1 = rect
        terms.append('(step(%.9f,UV.x)*step(UV.x,%.9f)*step(%.9f,UV.y)*step(UV.y,%.9f))' %
                     (x0/width, x1/width, y0/height, y1/height))
    mask.set_editor_property('code', 'return saturate(' + '+'.join(terms) + ');')
    require(MEL.connect_material_expressions(uv, '', mask, 'UV'), 'Mask UV connection failed')
    require(MEL.connect_material_property(mask, '', unreal.MaterialProperty.MP_OPACITY), 'Opacity connection failed')
    rough = MEL.create_material_expression(material, unreal.MaterialExpressionConstant, -200, 400)
    rough.set_editor_property('r', 0.9)
    require(MEL.connect_material_property(rough, '', unreal.MaterialProperty.MP_ROUGHNESS), 'Roughness connection failed')
    MEL.recompile_material(material)
    require(ED.save_loaded_asset(material), 'Could not save material')
    return material


def locate_wall(world, x, center_z):
    """Check actual wall collision at center/corners; refuse furniture and door gaps."""
    points = []
    receiver_components = []
    for dx, dz in [(0, 0), (-48, -52), (48, -52), (-48, 52), (48, 52)]:
        hit = unreal.SystemLibrary.line_trace_single(
            world, unreal.Vector(x+dx, -1480, center_z+dz),
            unreal.Vector(x+dx, -1660, center_z+dz),
            unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE)
        require(hit is not None, 'No hallway wall at x=%s z=%s. No map saved.' % (x+dx, center_z+dz))
        fields = hit.to_tuple()
        point, normal = fields[5], fields[7]
        require(-1640 < point.y < -1580 and normal.y > 0.9,
                'Unexpected surface instead of gym hallway wall: ' + str(point))
        component = fields[10]
        require(component is not None, 'Wall trace has no receiver component')
        points.append(point.y)
        receiver_components.append(component)
    require(max(points)-min(points) < 3, 'Wall not flat across artwork footprint')
    return sum(points)/len(points), receiver_components


def main():
    for item in CONFIG['artworks']:
        path = ROOT / item['texture']
        require(path.is_file(), 'Missing texture: ' + str(path))
        require(hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256'], 'Texture checksum mismatch: '+str(path))
    source = CONFIG['source_map']
    target = CONFIG['target_map']
    require(ED.does_asset_exist(source), 'Source map missing. Run git lfs pull first.')
    exists = ED.does_asset_exist(target)
    require(LEVELS.load_level(target if exists else source), 'Cannot load map')
    all_actors = list(ACTORS.get_all_level_actors())
    if exists:
        require(any(TAG in [str(t) for t in a.tags] for a in all_actors),
                'Target map exists without our tag; refusing to overwrite it.')
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    placements = []
    receivers = []
    for item, x in zip(CONFIG['artworks'], CONFIG['hallway_x_cm']):
        y, components = locate_wall(world, x, CONFIG['center_z_cm'])
        placements.append((item, x, y))
        receivers.extend(components)
    # Keep edits in memory until validation passes, then save to the separate target.
    before_meshes = sum(isinstance(a, unreal.StaticMeshActor) for a in ACTORS.get_all_level_actors())
    for actor in list(ACTORS.get_all_level_actors()):
        if TAG in [str(t) for t in actor.tags]:
            require(ACTORS.destroy_actor(actor), 'Could not replace previous generated decal')
    for component in receivers:
        component.set_editor_property('receives_decals', True)
    placed = []
    for item, x, wall_y in placements:
        material = make_material(item)
        width, height = item['size_px']
        # Entire texture box height 110 cm; artwork centers near eye level and labels below.
        box_height = CONFIG['canvas_height_cm']
        box_width = box_height * width / height
        # Decals project along local +X into the wall (world -Y); local Z stays up.
        actor = ACTORS.spawn_actor_from_class(
            unreal.DecalActor, unreal.Vector(x, wall_y+0.5, CONFIG['center_z_cm']),
            unreal.Rotator(pitch=0, yaw=-90, roll=0))
        require(actor is not None, 'Failed to create decal')
        actor.set_actor_label('StudentArt_' + item['id'])
        actor.set_folder_path('Hallway / Student Art V01')
        actor.tags = [TAG]
        component = actor.get_component_by_class(unreal.DecalComponent)
        require(component is not None, 'Decal component missing')
        component.set_decal_material(material)
        # UE decal_size is a half extent. Shallow depth avoids the opposite side of the wall.
        component.set_editor_property('decal_size', unreal.Vector(3, box_width/2, box_height/2))
        component.set_editor_property('sort_order', 20)
        component.set_editor_property('fade_screen_size', 0.001)
        placed.append({'student': item['student'], 'actor': actor.get_actor_label(),
                       'location_cm': list(actor.get_actor_location().to_tuple()),
                       'material': material.get_path_name(), 'canvas_cm': [box_width, box_height]})
    final = list(ACTORS.get_all_level_actors())
    owned = [a for a in final if TAG in [str(t) for t in a.tags]]
    require(len(owned) == len(CONFIG['artworks']), 'Incorrect decal count')
    require(all(isinstance(a, unreal.DecalActor) for a in owned), 'Artwork must be true decals')
    require(sum(isinstance(a, unreal.StaticMeshActor) for a in final) == before_meshes,
            'Unexpected mesh geometry change')
    require(unreal.EditorLoadingAndSavingUtils.save_map(world, target), 'Could not save gallery map')
    # Place editor camera in the corridor for the required human visual check.
    try:
        unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(
            unreal.Vector(-825, -1310, 175), unreal.Rotator(pitch=0, yaw=-90, roll=0))
    except Exception as error:
        unreal.log_warning('Map saved; set corridor review camera manually: ' + str(error))
    REPORT.write_text(json.dumps({'status': 'saved_pending_visual_review', 'map': target,
        'source_map_unchanged': source, 'added_meshes': 0, 'decal_count': len(owned),
        'placed': placed, 'visual_review': 'Check orientation, wall coverage, labels and materials in editor.'}, indent=2), encoding='utf-8')
    unreal.log('STUDENT_ART_SAVED: ' + target)


try:
    main()
except Exception:
    REPORT.write_text(json.dumps({'status': 'failed', 'error': traceback.format_exc()}, indent=2), encoding='utf-8')
    unreal.log_error(traceback.format_exc())
    raise
