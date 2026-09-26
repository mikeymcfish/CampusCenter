# Campus Center — Unreal prototype

## Ground-floor review — September 25, 2026

The current launchers open `/Game/Campus/Maps/CampusCenter_GroundFloorReview_v05` in Unreal Engine 5.8.2. This is the current editable walkthrough revision; sections below describe historical revisions.

**Four new independent critic rounds covered 31 ground-floor rooms/zones and 304 base screenshots**, plus camera-repair evidence. Scores: **4.2 → 6.1 → 6.4 → 6.6/10**. The requested 8.5/10 and zero-visible-errors gate was **not met**. See the final critic report for remaining defects and scope limitations.

[Offline review gallery](ground_floor_review_v03/review_gallery.html) | [Final critic report](ground_floor_review_v03/critic_round_4/review.md) | [Scope and changes](ground_floor_review_v03/README.md) | [Saved-map validation](ground_floor_review_v03/delivery_validation.json)

The passes improved ground-floor lighting, floor continuity, architectural material scale and grout, and removed an exterior tree intrusion from the gym. Existing furniture, the K-wall geometry, all nine artwork decals and ten trophy decals are preserved. The prior maps and Blender master are unchanged. The gym finish is inferred; exact architect-pattern matching throughout the building is not established.

Saved-map validation found zero structural preservation/dependency errors across 1,013 existing mesh actors. This does **not** mean the visual zero-error gate passed. `GROUND_FLOOR_ASSET_MANIFEST.json` records delivery hashes. Higher shadow quality is enabled; performance was not remeasured. The legacy standalone executable was not rebuilt.

Run `git lfs pull` after cloning, then `Launch_Unreal.cmd` to walk or `Edit_Commons_Dusk.cmd` to edit. Open the gallery locally after pulling LFS assets.

---

## Artwork and trophy update — September 25, 2026

This prior revision used `/Game/Campus/Maps/CampusCenter_ArchitectDecals_v04` in **Unreal Engine 5.8.2**. Added **9 supplied artworks opposite the Innovation Lab** and **10 trophy decals on an oak shelf opposite the locker rooms**. Existing furniture is preserved. The shelf clears the existing case by 13 cm.

[Scope and verification](decal_update_v02/README.md) | [Final independent review](decal_update_v02/critic_round_4/review.md) | [Artwork view](decal_update_v02/critic_round_4/01_art_gallery_wide.png) | [Trophy view](decal_update_v02/critic_round_4/04_trophy_shelf_wide.png)

**Final critic score: 8.0/10 after four rounds (6.2, 6.8, 7.6, 8.0). The requested 8.5 and zero-visible-errors gate was not met.** Decal placement, orientation, transparency and shelf contact were verified. Remaining issues are abrupt floor transitions, uneven lighting and simplified material response. Exact architect-pattern matching is not established.

Saved-map validation reports zero errors, 974 unchanged existing mesh actors, all 19 supplied decals and exact trophy-to-shelf contact. Only the existing architectural finish actor was replaced, preserving all vertex positions while correcting normals and applying material overrides. Originals are preserved. `DECAL_ASSET_MANIFEST.json` records the current map dependency files and hashes.

Run `git lfs pull` after cloning. Use `Launch_Unreal.cmd` to walk or `Edit_Commons_Dusk.cmd` to edit. The legacy standalone executable and its older performance claims do not apply to this update.

---

## Previous architect finish revision — September 25, 2026

Run `Launch_Unreal.cmd` or open `Edit_Commons_Dusk.cmd`. These use the installed **Unreal Engine 5.8.2 editor** and `/Game/Campus/Maps/CampusCenter_Dusk_ArchitectFinishes_v03`. The map is derived from the current furnished Dusk scene, with the September 22 architect references guiding wall, ceiling and floor changes. Existing furniture is preserved. The launch filename retains “Dusk” for compatibility, although the finish review uses brighter neutral lighting.

See [finish scope, critic scores and screenshots](architect_finishes_v01/README.md). Assets use Git LFS; run `git lfs pull` after cloning. The required project-local `CampusCrowdFix` runtime plugin includes source and an editor binary for the installed engine build. Current asset attribution is in [common-area credits](asset_provenance/common_area/CREDITS.md).

**Review status: 6.3/10 after four rounds; the requested 8.5 and zero-visible-errors gate was not met.** Exact reference-pattern matching remains incomplete. `ARCHITECT_ASSET_MANIFEST.json` is the current saved-map asset verification; the older `HANDOFF_MANIFEST.json` describes the historical prototype handoff.

The legacy standalone executable has **not** been rebuilt for this revision. The performance measurements and validation below apply to the earlier V03 prototype, not this current finish pass.

---

## Current material pass: V03

The editable project and standalone build now include native physically scaled oak, masonry, paving and metal shaders, corrected fabric/plaster detail, warmer interior lighting, controlled exposure, Lumen reflections and subtle postprocessing. Current screenshots: `unreal_project/ReviewV03/Cinematic_Review.jpg` and nine full-resolution room PNGs.

The RTX 4090 averaged **105–116 fps at native 1920×1080** in three packaged stationary-view tests; 1% lows were 74–88 fps. Normal exploration is capped at **60 fps**. See `polish_v03/README.md` and `polish_v03/performance.json` for settings, methodology, source licensing and limits. Earlier Review/V02 images are historical.

This pass preserves the building layout, props, static mannequins and Blender master. The existing simplified geometry and sparse exterior scenery remain visible.

## Open and explore

Double-click `Launch_Unreal.cmd`. It uses the standalone Windows build when present, otherwise the installed Unreal 5.8 editor. Keep the entire `unreal_delivery/Windows` folder together.

- **E**: entrance, free exploration
- **I / L / B / F / U**: Innovation Lab, lockers, student bathroom, fitness, upper commons
- **G**: automatic guided tour (loops)
- **N**: free exploration with students hidden

Use **WASD** to walk, **mouse** to look, **Space** to jump, **Alt+Enter** for fullscreen and **Alt+F4** to exit. Room selection and student visibility are launcher choices; there are no custom in-game tour/toggle hotkeys in this version.

## Editable project

Open `unreal_project/CampusCenter.uproject` in Unreal Engine **5.8.2**. Main map: `/Game/Campus/Maps/CampusCenter`. The project uses the supplied first-person Blueprint and requires no project C++ compilation. The attempted optional C++ controls were not included because the installed compiler was incompatible.

The building is organized into 233 spatial mesh groups with Architecture, Furniture, Equipment, Students, Doors, Roof and Screen folders/tags. Students are baked static mannequins. The projector screen starts hidden. The full guided camera route is retained in `/Game/Campus/Tours/Campus_Guided_Tour`; the accelerated preview sequence is `Campus_Preview_20s`.

The Blender master remains unchanged. `unreal_transfer/exports/transfer_manifest.json` maps the grouped Unreal assets back to original Blender object names, records the source hash, and retains the camera samples. Export coordinates are centimeters, converted from Blender meters.

## Review and validation

See `unreal_project/Review` for nine room images and the short continuous preview. The preview accelerates the complete route; use free exploration or the full tour for normal viewing speed.

Verified: saved map reopens with 233 mesh groups and no missing mesh/material slots; all nine room starts find their expected floor; the actual first-person character traverses all 86 route legs without getting stuck; the automatic tour takes camera control and moves; the packaged executable boots the campus map with the first-person game mode. The preview is 240 frames, 640 x 360, 12 fps, exactly 20 seconds, and passes full video decode. Evidence is in the project validation JSON files and `packaged_smoke.log`.

V03 is the current material and lighting pass. Remaining limits and measured performance are documented in polish_v03/README.md.

## Rebuilding

The source/export and Unreal Python scripts are included for maintenance. Run staged scripts deliberately: the initial import/tour creation scripts are setup scripts and should not be rerun blindly over an edited project. Use the existing saved project for normal work.

Use `Build_Unreal.ps1` to rebuild with the installed engine. The standalone build uses UE's `RunUAT.bat BuildCookRun`, Win64 Development, cook/stage/pak/archive, `-nocompile -nocompileeditor -installed`. Packaging uses file-based cooking (`bUseZenStore=False`). Avoid starting another editor with a conflicting Zen cache configuration during cooking.

Generated caches, temporary imports and abandoned optional C++ sources are excluded from this handoff. The standalone package is stored locally in this directory but ignored by Git; source Unreal assets use Git LFS. No remote commit or push was performed.

