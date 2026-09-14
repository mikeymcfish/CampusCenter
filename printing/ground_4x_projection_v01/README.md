# Ground floor 4x print and projection package

## Print and assemble

The v12 ground-floor STL was enlarged uniformly by exactly 4, from 1:350 to 1:87.5. Assembled extents are 743 x 562 x 53.568 mm. There is no added ground plane and no roof or upper-floor print. Existing print-only solid stair abutments and thickened walls are retained.

Six STLs are in `print_tiles/`. Import each separately in millimetres at 100%, with the flat underside on the bed. The largest envelope is approximately 247.67 x 281 x 53.57 mm, below the selected conservative 290 x 300 mm envelope. This leaves space for a modest brim within the H2D's 300 x 320 mm dual-nozzle area (single-nozzle area is 325 x 320 mm). Check the slicer's selected nozzle profile and bed exclusions before printing.

Use matte white PLA for projection. Start with 0.20 mm layers, three walls and ordinary sparse infill; these are suggested settings, not pre-sliced machine instructions. The geometry remains supported continuously from a flat underside; no suspended stairs or new overhangs were introduced. A physical print has not been tested.

Arrange A1-A2-A3 in the south row, B1-B2-B3 in the north row, keeping every piece in its supplied XY orientation. Some footprints do not fill their entire rectangular cell. Use `Assembly_Map.png`, not the bounding rectangles alone. Dry-fit planar seams on a flat surface, then glue if desired. No protruding pins or extra base were added. The following offsets are for exact digital assembly, measured from the original shared print datum; every tile STL itself starts at local XY zero.

| Tile | Dimensions mm | Assembly offset X,Y mm |
|---|---|---|
| Ground_A1 | 247.67 x 197.00 x 48.77 | 13.000, 92.000 |
| Ground_A2 | 247.67 x 270.00 x 48.77 | 260.667, 19.000 |
| Ground_A3 | 247.67 x 281.00 x 53.57 | 508.333, 8.000 |
| Ground_B1 | 247.67 x 281.00 x 48.77 | 13.000, 289.000 |
| Ground_B2 | 247.67 x 281.00 x 48.77 | 260.667, 289.000 |
| Ground_B3 | 219.67 x 281.00 x 53.57 | 508.333, 289.000 |

## Projection setup

`Campus_Center_Projection.blend` is an isolated furnished ground-floor projection scene. The physical shell is imported from the six exact print tiles. The furniture and props come from Cycles Studio v05. Roofs, upper-floor contents and ceiling fixtures are disabled for this view. The architectural source is unchanged.

The camera represents the PROJECTOR, not the viewer. Default setup: 60 degrees down from horizontal, south of the model looking north, 1.2 throw ratio, 1024 x 786 pixels. Actual camera position and target in assembled-print millimetres are recorded in `projection_manifest.json`. `projector_config.json` controls angle, azimuth, lens throw ratio, resolution and margin. Change it and rerun the build/render scripts once the physical projector's position and lens are known. Different throw ratios or optical lens shift require rerendering; a flat corner warp alone cannot accurately realign tall walls.

Use `projection/calibration_25mm.png` first. Match the outer model silhouette and checker intersections to the physical model. Each checker square is 25 mm in physical-model units. Disable digital keystone initially and use the projector's actual native resolution; 1024 x 786 was retained literally from the request, not silently changed to standard 1024 x 768. If the device is 1024 x 768, update configuration and rerender at that size.

The black-background loop is intended for fullscreen, unscaled playback. Black outside the receiver mask avoids projecting onto the surrounding table. Side walls can occlude the floor at 60 degrees; a single projector cannot illuminate hidden surfaces. The furnished image is a viewpoint-dependent illusion on a simplified physical shell, so large viewpoints away from the projector will show perspective distortion. Calibration can only be finalized with the actual projector and assembled print.

The 12-second loop uses periodic moving daylight shadows, fire-emission flicker and two stylized baked-pose moving occupants. The occupants move without an articulated walking gait. Lighting and positions return mathematically to their start after 144 frames; the duplicated endpoint is omitted. The source walkthrough was not changed.

## Rebuild and evidence

Python scripts: `split_ground.py` uses project-local trimesh/manifold3d; `build_projection.py` and `render_projection.py` run with Blender 5.0; `make_guide.py` produces the assembly map. Run Blender with `--factory-startup -b Source_Copy.blend --python build_projection.py`, then open the saved projection file for rendering. Sources and checks are recorded in manifests. All six STL files were reopened as closed, consistently wound, single-component meshes; summed volume matches the scaled source. The rendered image checks are separate from physical projection calibration.

Bambu dimensions source: https://uk.store.bambulab.com/collections/3d-printer/products/h2d


For this provisional fit, the projector lens is 1068.8 mm above the print underside/table, 333.3 mm south of the model's minimum-Y edge, centered across its width. The aim point is the model's XY center at the 4.8 mm floor surface; lens-to-aim distance is 1228.6 mm. These figures assume no lens shift. They are setup estimates, not measured hardware values.

Play `projection/Campus_Center_Ground_Loop_1024x786.mp4` in a player with repeat enabled (for example VLC), full-screen on the projector. `projection/Projection_Preview.jpg` is the first frame. `receiver_mask_black.png` and `calibration_25mm_black.png` are ready-to-display calibration images with black outside the model. Avoid a player that adds crop, overscan, or a stretched aspect ratio.

To rebuild from a copied delivery folder, copy the existing `blender_cycles/v05/Campus_Center_Cycles_Studio.blend` to `Source_Copy.blend` in this folder before running `build_projection.py`. The split script's source is the original v12 ground STL; update its source path if rebuilding away from the authoring workspace. The supplied output STLs and packed projection Blender file need no rebuild to use.
