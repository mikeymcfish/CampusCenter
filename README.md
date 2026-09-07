# King School Campus Center

Current architectural scene, fabrication models and source references, compiled September 7, 2026.

| Start here | Contents |
|---|---|
| [Full Blender scene](scene/Campus_Center_Current.blend) | Current untextured building, furniture and equipment; 112 blank mannequins; extended walking camera |
| [GLB](scene/Campus_Center_Current.glb) | Static interchange model; animated camera is in the Blender file |
| [Two-color keychain](printing/keychain/Campus_Center_Two_Color.3mf) | Black structure and solid white glazing; assign the two parts to your filaments |
| [Three-layer printing](printing/three_layer/README.md) | Matched ground, upper and roof prints, without extra rectangular ground planes |
| [Laser-cut kit](laser/README.md) | Two floors and stairs, two 12 x 24 sheets of 1/8 inch wood; cut the fit coupon first |
| [LEGO guide](lego/Campus_Center_LEGO_Build_Guide.pdf) | 35-page ground-floor guide, 662 parts, stud maps and editable LDraw model |
| [Structural STEP](cad/Campus_Center_Structure.step) | Generic architectural solids; detailed furniture and mannequins remain in Blender/GLB |

## Furniture revision 15

The current scene includes the E-102/P-100 furniture and fixture update: commons seating, cafe equipment with two POS tablets, detailed locker banks/showers, corrected restroom fixtures and recessed fountains. See [revision notes and collection controls](scene/FURNITURE_REVISION.md). The projector hardware and lowered screen have separate collection toggles. Review images are from this revision.

## Blender and walkthrough

Open `scene/Campus_Center_Current.blend`. Units are metres. Disable the entire **STUDENTS - toggle entire collection** collection to hide the mannequins. They share one low-poly mesh and have no facial, clothing or gender details.

The iLab sink now faces east into the room. The spray booth sits in the southwest corner, faces into the room, and has a representative rear duct through the west wall toward the patio. The duct is a visual planning detail rather than an engineered ventilation design.

The active camera follows the supplied purple route sketches: entrance, commons, iLab loop, west corridor, west stair, upper art/classroom corridor, bridge and balcony. It runs **5,517 frames at 24 fps (3 minutes 50 seconds)**, including brief stops to look at points of interest. Travel peaks at approximately 0.95 m/s and slows on stairs. The horizon stays level; eye height follows the stair elevation. Route doors are held open for passage. `scene/walkthrough_route.json` contains the route and sampled camera positions. A complete new walkthrough video has not been rendered; the included review images are checks of the current scene.

## Fabrication

Each fabrication folder has its own instructions and digital validation. The two-color 3MF contains a single assembly with two aligned solids. Confirm black/white filament assignments in your slicer. Do not print or independently arrange the white glazing part by itself. The larger three-layer print set includes the matched upper floor required by its roof.

The laser kit uses 3.175 mm wood, nominal 0.15 mm kerf compensation and 0.05 mm clearance. Do not double-compensate its cut paths. Test the included coupon before the full sheets.

The LEGO model is a stud-aligned interpretation, approximately 1:125 in plan, on six 32 x 32 baseplates. It has four wall courses, white blocks representing glazing and simple interior markers. `lego/brick_placements.csv` gives every brick's coordinate. `lego/Campus_Center_Ground_Floor.ldr` uses standard parts from your installed LDraw library. Use a supporting board beneath the six baseplates. Digital checks do not replace physical test builds or prints.

## References and source priority

The architectural plans govern building geometry. The revised iLab PDF governs equipment layout, subject to the user's subsequent changes: two Bambu Lab H2D printers with AMS 2 Pro units, room-facing sink and corner spray booth. Interior appearance images guide visual details; they do not override the floor plans. The two camera sketches guide circulation, adjusted to clear real walls, doors, railings and furniture.

The current equipment library and retained manufacturer/open-source CAD are under `equipment/`; source images are under `references/equipment/`. Attribution and source limitations are recorded in [THIRD_PARTY_SOURCES.md](THIRD_PARTY_SOURCES.md).

`ASSET_MANIFEST.json` records copied source paths and hashes. Earlier scene versions, outdated walkthrough videos and H3 packages, Prusa experiments, texture experiments, backups and temporary logs are omitted. The structural STEP is still the latest generic structural model, even though the Blender scene has advanced further.

## Editing and Git

The Blender file is self-contained and texture-free. `laser/editable_source` includes its parametric source and instructions. `tools/` contains the portable LEGO generator, Blender preview renderer and PDF guide generator; run these from the repository using Python or Blender as appropriate.

Large model formats are configured for Git LFS in `.gitattributes`. Git LFS must be enabled in your Git client before committing them. This compilation places files in the local repository; it does not publish them or create a commit.
