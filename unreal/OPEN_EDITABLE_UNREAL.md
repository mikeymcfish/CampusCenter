## Latest: additional props, larger trophies, and gym bleachers (2026-09-27)

The current map is `/Game/Campus/Maps/CampusCenter_StandardAssets_v07`, matching `Edit_Commons_Dusk.cmd`. Added six laptops and six cups on tables/desks, enlarged ten trophy image cards by 45%, and added two three-row gym bleacher banks. Your latest landscape and students are preserved. Details, native screenshots, and backup information: [prop_seating_v08/README.md](prop_seating_v08/README.md). Visual gallery: [prop_seating_v08/review.html](prop_seating_v08/review.html).

## Latest: V08 keyboards, seating, tool boards and decals

Four keyboards, 23 iLab seats, five physical tool boards and 100 new distinct decal designs are installed in the editable map. Preview and per-design catalog: http://127.0.0.1:8937/ilab_v08/. Sources and editing notes: `realism_assets/ilab_v08/README.md`.

## Latest: V07 desk details and nature backdrop

The current editable map includes 12 stationery arrangements and a curved generated nature background. Move them in Outliner folders `iLab / V07 desk details` and `Site / V07 distant nature`. The desk details are flat transparent cards; the background is photographic distant scenery. Source textures and prompts are in `realism_assets/ilab_v07/`. Preview: http://127.0.0.1:8937/ilab_v07/.

# Editable common area — dusk

## Latest revision: furniture and tool walls V06

The iLab has 14 molded chairs, 9 drafting stools, 3 oak worktables, and 5 framed metal pegboards. Hanging tools are texture-only; frames and panels are geometry. Four new photo-based TRELLIS equipment types were selected for installation after visual review. The new BigRep generation was rejected; its cleaner V05 approximation remains.

Gallery and evidence: `http://127.0.0.1:8937/ilab_v06/`. Editable furniture is under `iLab / V06 Furniture and tools`; generated equipment is under `iLab / V06 TRELLIS equipment`. Sources and limitations are recorded in `realism_assets/ilab_v06/README.md`. Restart the walkthrough to load this saved revision.

## Latest revision: iLab and controls V05

Walking is now 720 cm/s (20% above the previous 600); hold either Shift key to run at 1,100 cm/s. The saved `Campus_Walk_Settings` actor exposes both speeds. A Play automation test verified press, run, release, and return to walking.

The crowd is reduced to six people and four appearances. First visible high-resolution characters took about 50 seconds in the measured Play session; loading and assembling MetaHuman assets remains a startup cost.

The iLab now includes seven refreshed Formlabs planning models, four detailed computer workstations, corrected bench tools, task lamps, workbench finishes, and nine ceiling lights. Other machine exteriors are cleaner approximations; they are not exact manufacturer meshes. Review the native Play gallery at `http://127.0.0.1:8937/ilab_v05/`.

See [Edit the walkable area](EDIT_WALKABLE_AREA.md) for crowd navigation, physical player boundaries, movement settings, and crowd count. Historical verification below describes earlier checkpoints.

Run `Edit_Commons_Dusk.cmd` to edit, or `Walk_Commons_Dusk.cmd` to walk through the updated level. Both require Unreal Engine 5.8.

Project: `unreal_project/CampusCenter.uproject`  
Current level: `/Game/Campus/Maps/CampusCenter_Dusk`

`Launch_Unreal.cmd` and `Launch_Unreal.ps1` now launch this current editable-project walkthrough too. The older packaged executable is preserved but has not been rebuilt. The original CampusCenter map is preserved.

## Editing

Furniture is organized under numbered folders in `Commons`. Select all actors in a fixture folder when moving a multipart asset. Banners, dusk lighting, navigation, and review cameras have separate folders.

One lounge group was moved 1.5 metres west to open circulation. A redundant group remains available under `Commons / Optional seating (inactive)`, hidden in game with collision disabled.

Physical collision on walls, floors, and furniture controls where the player can move. `Commons_Walkable_Bounds` controls AI navigation coverage; expanding this volume does not remove physical obstacles. Navigation is dynamic. After layout edits, let assets finish loading, rebuild navigation, and test in Play mode.

## Verification

The updated common area passed six actual character walking routes: cafe queue, main aisle, lounge approach, fireplace seating approach, east dining aisle, and return to entrance. Player capsule sweeps were blocked by exterior glazing and a sofa. The navigation report contains 606 walkable samples on a 50 cm grid. These checks cover the tested common-area routes, not every room or possible clearance.

Native Unreal screenshots and the test report are at `realism_assets/common_area/unreal_integration/`, also served at http://127.0.0.1:8937/common_area/unreal_integration/ while the dashboard server is running.

## Crowd status

MetaHuman Crowd and its free sample content are installed and enabled. The level uses a 12-person Mass spawner with sample MetaHuman appearances and NavMesh wandering. Original static student groups are hidden and have collision disabled. The spawn query is local to the project, limited to the common-area floor. Movement has been observed in rendered Play mode; these are sample characters rather than custom King School uniforms.

## Assets and preservation

Imported native assets are under `/Game/CommonsPrep` and `/Game/Campus/CommonsIntegration`. The source Blender scene remains preserved at `realism_assets/common_area/render_v03/Commons_With_New_Assets.blend`; Unreal contains the subsequent aisle adjustments. Credits are in `realism_assets/common_area/CREDITS.md`.

Lighting combines a dusk sky, warm interior pools, banner washes, cafe task lighting, and cool window fill. Glass now uses a clear translucent material instead of dithered transparency. Play uses fixed 100% resolution, TSR flicker rejection, and increased Lumen/shadow temporal sampling. Some fine rendering noise remains; the exterior is illustrative rather than a matched school-site background.

## Play corrections � 2026-09-20

- Player collision: 24 cm radius, 88 cm runtime half-height (176 cm total). Step height: 32 cm.
- The gallery and lab leaves now open away from their shared junction. A short overlapping gallery wall stub that bisected the lab doorway was removed from the replacement mesh.
- The misplaced `V5_Interior_column_3.0_10.5` was removed only from the replacement main-stair mesh. Source Blender remains unchanged.
- Fireplace: native Niagara 3D gas fire, with a project-local volume material and a 96-cell maximum-axis simulation. The older emissive flame card is hidden.
- Geometry and materials are under `/Game/Campus/PlayFixes`; the crowd configuration and query are under `/Game/Campus/Crowd`.
- Current test evidence is in `play_validation_final.json`, `lab_clearance_final.json`, and `navigation_validation.json`. Six common-area routes, the main-stair ascent, and the turning approach into the lab were verified with the actual player. Entrance and gallery capsule sweeps pass. The raw lab sweep stops at its threshold, but the actual character steps over it and completes the route. These checks do not certify every room or possible clearance.

## Stair and exterior revision V02

- Removed the overlapping decorative riser shell and floating bridge guard runs above the main stairs. Added separate risers and a guard on the supported landing edge, leaving the stair exit open.
- Restored crowd automatic startup; diagnostic scripts now preserve that setting. The 12-person spawner uses a small project-local ground-floor query.
- Added front paving, ground, planted beds, wood benches, trees, and an editable white-and-wood school facade on the corrected opposite side specified during review.
- Exterior placement and facade dimensions are estimated from supplied images, not survey measurements. Exterior assets use existing free Poly Haven meshes and materials.
- Replacement geometry, site materials, and the fireplace volume material are under /Game/Campus/RepairV02. Site actors are organized in Site folders.
- Latest captures and runtime evidence: realism_assets/common_area/unreal_repair_v02/index.html. Live gallery: http://127.0.0.1:8937/common_area/unreal_repair_v02/.
- Pre-revision map and launcher backups are in realism_assets/common_area/unreal_repair_v02/backup/.


The reference-building placement was corrected during review: the white-school facade and apron are rotated 180 degrees around the site center, with the facade facing back toward the campus center. See reference_building_relocation.json for the saved transforms.


## Main stair surface revision V03

Removed four concealed metal stringers whose eight side planes coincided with the oak fascia. Only Architecture_Ground_10_11 uses the replacement /Game/Campus/StairRepairV03 mesh. Tread locations and oak covers are unchanged. Render settings were not changed. Thirty camera positions per version and a successful lower-flight ascent are recorded in realism_assets/common_area/stair_repair_v03/. Fine temporal lighting grain remains visible. Reload the map or restart the walkthrough to see this revision.



## Floor contact and ring lighting V04

Restart the editor or `Walk_Commons_Dusk.cmd` to load the saved map and the project-local CampusCrowdFix plugin. It corrects initial capsule positioning and synchronizes Mover after deferred pooled-actor teleports. The Play test recorded zero below-floor observations across 1,029 visible actor observations; the prior test recorded 75. These are observations over the tested startup and camera sequence, not a guarantee for every future path.

Four seating sets were repositioned, including the chair crossing the west wall. Sixty-three floor-standing furniture groups have lower bounds at floor level; tabletop accessories move with their support tables. Three entrance-to-seating navigation paths remain connected.

Four ring downlights (6,500 lumens, 3,000 K each) and four softer ceiling bounce lights now illuminate the room. Edit them under `Commons / Ring lighting`; diffuser material is `/Game/Campus/PlacementV04/M_RingLED`. Existing generic warm pools were reduced to balance the new sources.

Evidence and native on/off comparison: http://127.0.0.1:8937/common_area/placement_v04/ . Map, crowd-config and project-file backups are in `realism_assets/common_area/placement_v04/backup/`. The old packaged executable remains unchanged; the launchers use the current editor-based game.
