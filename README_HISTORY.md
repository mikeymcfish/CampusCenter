# Preserved earlier CampusCenter index

This is the former README, retained with every link for reference. Older versions and test packages are superseded for the current quickstart; nothing was deleted. Use [current downloads](PROJECT_DELIVERABLES.md) and the [current README](README.md) first. Historical statements below describe their own versions, not the latest release.

# Current deliverables

[Pac-Man R02 UV02 raw atlas test](projection/production-r02/pacman-atlas/README.md) includes checksum-verified reassembly of the unchanged lossless movie.

[Pac-Man R02 compact single-actor camera preview](projection/production-r02/pacman-viewing/README.md) is available with printed-model route exclusions and proof.

[Matched UV02 R02 Commons/Ripple atlas tests](projection/production-r02/atlas-tests/README.md) are available with their limited scope and import instructions.

[Two compact R02 viewing previews](projection/production-r02/viewing-previews/README.md) are available for immediate review. Camera views are not projection atlas inputs.

[Corrected B3 fireplace tile, P03](print/r29-p03-b3-fireplace/README.md) replaces only P02 B3 at 1:100. [Matched UV02 receiver](projection/p02-p03b3-uv02-receiver/README.md) is available; full revised media and physical calibration remain pending.

[Optional Pac-Man-style P01 reference kit](projection/production-p01/pacman-test-prototype/README.md) is available; the whole-space single-main-character chase remains pending.

[Ripple Rooms P01 loop downloads](projection/production-p01/ripple-rooms/README.md) are now available for the1:100 UV01 model.

[Infinite Floor P01 loop downloads](projection/production-p01/infinite-floor/README.md) are now available for the1:100 UV01 model.

[Tour static texture test packages](projection/production-p01/tour-statics/README.md) are available now for both physical scales.

[Approved H02 thirteen-stop masks and copy](projection/p02-uv01-h02-approved/README.md) supersede H01 selections: all three offices124–126, halls106/123 excluding physical corridors110/130. No animation/cue/project is supplied.

[Canonical versions, downloads, opening instructions and pending inputs](PROJECT_DELIVERABLES.md). **Quest PC-VR R01 and ground-floor Print P02** join the preserved R29 desktop/Vive releases. Final MadMapper P02 UV01 model/atlas packages are published; room ownership review remains. All eight final admissions concepts are published with AI/fictional-person labels and combined manifests, as detailed in the index.

## Current R29 Vive with integrated grip patch

Fetch and pull main, then run **Start_CampusCenter_Vive.cmd**. The normal launcher now applies and retains the verified grip-turn update in a separate managed cache, with recoverable rollback. Desktop and default rendering settings remain unchanged. [Opening, optional 3050 profile, verification and rollback instructions](README_CONSOLIDATED_VIVE.md). Hardware/performance/initial-facing issues remain unverified.

# King School Campus Center

## Historical R28 instructions

[Preserved R28 release and opening instructions](README_R28.md). Current root automatic launchers select R29; existing R28 caches and assets remain available.

## Historical R27 R13 Windows walkthrough

If you use GitHub Desktop, select **main**, choose **Fetch origin**, then **Pull origin**. Choose **Repository > Show in Explorer** and double-click **Start_CampusCenter_Vive.cmd** for Vive, or **Start_CampusCenter_Desktop.cmd** for desktop. On first use the launcher downloads the matching public release parts automatically, checks their pinned SHA-256 hashes, joins/extracts the ZIP, verifies every game file, then starts the tested build. Wait for setup to finish. Subsequent starts reuse the verified runtime. A failed/interrupted transfer can be retried by running the launcher again; incomplete/corrupted content will not launch. Internet access and roughly **10 GB free for Vive** or **20 GB for desktop** are needed for parts, joined ZIP and extracted files.

GitHub Desktop downloads **editable source and these setup launchers**; it does not put the packaged game EXE beside the source CMD files. The launchers obtain that EXE from the immutable [R27 R13 release](https://github.com/mikeymcfish/CampusCenter/releases/tag/campuscenter-r27-r13-review-20261002). No GitHub token or Unreal editor is needed to run the packaged build. Runtime files live under the short, gitignored `.cc` directory inside this checkout. Paths with spaces work; keep the root CMDs with the repository's `tools` folder. Avoid very deep checkout paths: Unreal's DLL loader still has a path-length limit, and the launcher gives a clear error if the path is too long. In that case move the whole checkout to a shorter folder such as `C:\GitHub\CampusCenter`; no Windows setting change is required. Verified downloads from the initial `.campuscenter-runtime` bootstrap are reused. To download/verify without launching, run `Start_CampusCenter_Vive.cmd -PrepareOnly`; `-VerifyOnly` checks an existing runtime without network downloads.

For Vive, install/start SteamVR and select it as the active OpenXR runtime yourself, then connect your headset/controllers. The launcher uses the exact tested R13 map, VR/plugin flags, 50% screen percentage and FPS display; it does not change OS/runtime/security settings. Hold either trigger to move forward in the headset's horizontal facing direction. Physical Vive/controller/stereo/comfort/performance acceptance remains untested. Inherited Research113 doorway and Fitness aisle diagnostic limitations remain; physical print slicing/fit is untested. The six integrated event graphics are retained with disclosed, **unverified redistribution rights**; user approval is not licensing evidence. Read [R27 R13 versions, source overlays, provenance and limitations](README_R27_R13.md).

The combined editable R27 overlay is under `r27-r13/desktop` and `r27-r13/vive`; baseline editing instructions and licensed dependency requirements are in that release README. The separate `release/vive-r27-r13-20261002` branch preserves the Vive project lineage. Existing source, prior release branches and release assets remain available below.


**Current Unreal walkthrough (September 27, 2026):** [latest editable scene and screenshots](unreal/README.md). Updated landscape, imported assets, animated students, tabletop props, larger trophy decals, and gym bleachers. Unreal Engine 5.8.2; run `git lfs pull` before opening.

**Latest ground-floor print and projection package:** [Acrylic slots, 31 room references, and interactive Projection Studio v06](printing/acrylic_projection_v06/README.md). Includes six print pieces, 1/16-inch acrylic templates, H3 prompts, alignment and geometry-based animation examples.

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

Ground floor 4x print: [six H2D-sized tiles and assembly map](printing/ground_4x_projection_v01/README.md).

Previous floor-only projection: [v03 - 93 students, detailed court and furnishings, 24 fps loop and 24 reference images](printing/ground_4x_projection_v03/README.md). Black walls and exterior; static lighting.


## Furnished ground-floor print and informational mapping

Current ground-floor projection model: [v04 — furniture integrated into the support-free print](printing/ground_furnished_projection_v04/README.md). Six STL/3MF tiles, a complete furnished STEP, unchanged 1:87.5 footprint, and no extra ground plane. [Print package](printing/ground_furnished_projection_v04/Campus_Center_Furnished_Print_Package.zip).

The matching [42-second informational tour](printing/ground_furnished_projection_v04/information/Campus_Center_Information_Preview.mp4) highlights commons/cafe, iLab, learning/gallery and athletics, with room captions and checked circulation routes. [Player and alignment modes](printing/ground_furnished_projection_v04/information/index.html). Wall tops and exterior pixels remain black in the RGB masters. Digital geometry and decoded-frame checks passed; physical printing and projector calibration remain to be done.


## Standalone enclosed projection prints v05

[Ground and upper print sets](printing/enclosed_furnished_v05/README.md): six furnished, solid-wall printable parts per level, STEP/STL/3MF exports and separate 42-second informational projection loops. Shared new 830 mm canvas; use the matching v05 masks and videos. Originals and the stackable models remain available.


[Ripple R04 viewing, lossless atlas and QA](projection/production-r04/ripple-black-thin-staggered/README.md) provides black-background, thinner staggered waves. [Viewing download](https://github.com/mikeymcfish/CampusCenter/releases/tag/campuscenter-ripple-r04-black-thin-staggered-viewing-20261006); [actual lossless atlas and mapped reference](https://github.com/mikeymcfish/CampusCenter/releases/tag/campuscenter-ripple-r04-black-thin-staggered-atlas-20261006). H03 remains historical, superseded by current H04 brighter same-hue colors and Commons-only fireplace. Physical projector/MadMapper validation remains untested.


[Optional projector tracker and live R29 sender R01](targets/projector-tracker-sender-r01/README.md) combines the separately installed companion with a guarded small native patch. [Combined downloads and install/calibrate/rollback guide](https://github.com/mikeymcfish/CampusCenter/releases/tag/campuscenter-projector-tracker-sender-r01-20261006). Actual packaged-game software reception passed; P02 sample1:250 only. Hardware HMD/projector/DPI/performance untested. Root launchers/defaults remain unchanged.

[H04 early Commons/Cafe viewing tests](projection/p02-p03b3-h04-early-viewing/README.md) brighten room colors, dim furniture in the same hue and light the fireplace only with Commons. [Two small camera clips](https://github.com/mikeymcfish/CampusCenter/releases/tag/campuscenter-h04-commons-cafe-early-viewing-20261006); current all13 H04 tour published separately. [Small R04 mobile viewing copy](https://github.com/mikeymcfish/CampusCenter/releases/tag/campuscenter-ripple-r04-mobile-viewing-20261006) is viewing only with lossy black noise disclosed.


[Current H04 all13-stop/30-page atlas tour](projection/p02-p03b3-h04-all13-final/README.md): [small full-tour viewing overview](https://github.com/mikeymcfish/CampusCenter/releases/tag/campuscenter-h04-all13-30pages-viewing-20261006), [actual30-page8192 atlas kit and source QA](https://github.com/mikeymcfish/CampusCenter/releases/tag/campuscenter-h04-all13-30pages-bright-samehue-tour-20261006). Brighter room colors, dimmer same-hue furniture and fireplace only during Commons; exact official gym captions and unchanged UV02. H03 and early H04 tests remain preserved. Physical playback/calibration untested.


[Verified release download sizes/SHA256 and immutable tag/source references](FINAL_MEDIA_RELEASE_RECEIPTS.json).

[Source formatting, exact archive hashes and tested scope](FINAL_SOURCE_PUBLICATION_NOTES.md).


## Preserved additional index links

- [Original reference](https://github.com/mikeymcfish/CampusCenter/releases/download/campuscenter-project-update-20261005/CampusCenter_Quest3_PC_VR_R01_Install_Package.zip)
- [Original reference](https://github.com/mikeymcfish/CampusCenter/releases/tag/campuscenter-r29-review-20261004)
- [Original reference](https://github.com/mikeymcfish/CampusCenter/releases/tag/campuscenter-tron-wallcaps-t01-atlas-20261006)
- [Original reference](print/r29-p02)
