# King School Campus Center

Current architectural scene, fabrication models and source references, compiled September 7, 2026.

| Start here | Contents |
|---|---|
| [Full Blender scene](scene/Campus_Center_Current.blend) | Current textured building, furniture and equipment; 112 blank mannequins; extended walking camera |
| [GLB](scene/Campus_Center_Current.glb) | Static interchange model; animated camera is in the Blender file |
| [Two-color keychain](printing/keychain/Campus_Center_Two_Color.3mf) | Black structure and solid white glazing; assign the two parts to your filaments |
| [Three-layer printing](printing/three_layer/README.md) | Matched ground, upper and roof prints, without extra rectangular ground planes |
| [Laser-cut kit](laser/README.md) | Two floors and stairs, two 12 x 24 sheets of 1/8 inch wood; cut the fit coupon first |
| [LEGO guide](lego/Campus_Center_LEGO_Build_Guide.pdf) | 35-page ground-floor guide, 662 parts, stud maps and editable LDraw model |
| [Structural STEP](cad/Campus_Center_Structure.step) | Generic architectural solids; detailed furniture and mannequins remain in Blender/GLB |


## 20-second walkthrough preview

[Play the continuous 20-second walkthrough](scene/walkthrough_20s/Campus_Center_20s_Walkthrough.mp4). Low resolution: 480 x 270 at 12 fps, uniformly sampled over the full revision-18 camera route. Includes locker room, student bathroom and fitness room. No cuts or audio. The full-length camera animation remains in Blender.

## Current revision 18

Audit repairs, packed textures and the expanded locker/bathroom/fitness camera route are complete. See [revision notes](scene/REVISION18.md) and [current texture previews](scene/review_v18/Commons.png).

## Mannequin revision 16

All temporary students have been replaced with lightweight posed mannequins. The reusable [pose library](scene/mannequins/Mannequin_Pose_Library.blend) and [preview](scene/mannequins/pose_library_preview.png) are included. Revision-18 review images show these figures with the new materials.

## Furniture revision 15

The current scene includes the E-102/P-100 furniture and fixture update: commons seating, cafe equipment with two POS tablets, detailed locker banks/showers, corrected restroom fixtures and recessed fountains. See [revision notes and collection controls](scene/FURNITURE_REVISION.md). The projector hardware and lowered screen have separate collection toggles. Furniture has the revision-18 audit corrections; use the revision-18 previews for current materials.

## Blender and walkthrough

Open `scene/Campus_Center_Current.blend`. Units are metres. Disable the entire **STUDENTS - toggle entire collection** collection to hide the mannequins. The 112 students now use 26 shared baked pose meshes, with two teen-proportioned bases and no facial details, clothing or textures. Thirty-six are seated. There are no armatures or live student modifiers. See [mannequin library and editing notes](scene/mannequins/README.md).

The iLab sink now faces east into the room. The spray booth sits in the southwest corner, faces into the room, and has a representative rear duct through the west wall toward the patio. The duct is a visual planning detail rather than an engineered ventilation design.

The active camera follows the supplied route with new visits to locker room 122, student bathroom 117 and fitness room 218. It runs **8,994 frames at 24 fps (6 minutes 15 seconds)**. The route includes short viewing pauses, opened passage doors and checked eye/torso clearance. `scene/walkthrough_route.json` contains the route. A 20-second frame-skipped preview is available above; no real-time full-length video has been rendered. Current texture previews are in `scene/review_v18/`.

## Fabrication

Each fabrication folder has its own instructions and digital validation. The two-color 3MF contains a single assembly with two aligned solids. Confirm black/white filament assignments in your slicer. Do not print or independently arrange the white glazing part by itself. The larger three-layer print set includes the matched upper floor required by its roof.

The laser kit uses 3.175 mm wood, nominal 0.15 mm kerf compensation and 0.05 mm clearance. Do not double-compensate its cut paths. Test the included coupon before the full sheets.

The LEGO model is a stud-aligned interpretation, approximately 1:125 in plan, on six 32 x 32 baseplates. It has four wall courses, white blocks representing glazing and simple interior markers. `lego/brick_placements.csv` gives every brick's coordinate. `lego/Campus_Center_Ground_Floor.ldr` uses standard parts from your installed LDraw library. Use a supporting board beneath the six baseplates. Digital checks do not replace physical test builds or prints.

## References and source priority

The architectural plans govern building geometry. The revised iLab PDF governs equipment layout, subject to the user's subsequent changes: two Bambu Lab H2D printers with AMS 2 Pro units, room-facing sink and corner spray booth. Interior appearance images guide visual details; they do not override the floor plans. The two camera sketches guide circulation, adjusted to clear real walls, doors, railings and furniture.

The current equipment library and retained manufacturer/open-source CAD are under `equipment/`; source images are under `references/equipment/`. Attribution and source limitations are recorded in [THIRD_PARTY_SOURCES.md](THIRD_PARTY_SOURCES.md).

`ASSET_MANIFEST.json` records copied source paths and hashes. Earlier scene versions, outdated walkthrough videos and H3 packages, Prusa experiments, texture experiments, backups and temporary logs are omitted. The structural STEP is still the latest generic structural model, even though the Blender scene has advanced further.

## Editing and Git

The Blender file is self-contained with packed textures; mannequins remain blank. `laser/editable_source` includes its parametric source and instructions. `tools/` contains the portable LEGO generator, Blender preview renderer and PDF guide generator; run these from the repository using Python or Blender as appropriate.

Large model formats are configured for Git LFS in `.gitattributes`. Git LFS must be enabled in your Git client before committing them. This compilation places files in the local repository; it does not publish them or create a commit.

## Unreal interactive prototype

See [Unreal handoff](unreal/README.md) for the editable project, standalone exploration launcher, guided tour, review images and validation.

## Blender Cycles studio

See [Cycles Studio v01](blender_cycles/v01/README.md) for the packed rendering scene, three 1080p stills, EXR passes and measured render times.

Previous Blender finish revision: [Cycles Studio v02 - blue walls and commons carpet](blender_cycles/v02/README.md).

Previous Blender detail revision: [Cycles Studio v03 - graphics, planting, furniture and printer details](blender_cycles/v03/README.md).

Latest Blender environment revision: [Cycles Studio v04 - planting, grass/concrete, fire, larger banners and photographic sky](blender_cycles/v04/README.md).

Latest Blender revision: [Cycles Studio v05 - student artwork, larger banners and modern fireplace](blender_cycles/v05/README.md).
