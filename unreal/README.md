# Campus Center — Unreal prototype

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

