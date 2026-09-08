# Campus Center — Cycles Studio v01

Open `Campus_Center_Cycles_Studio.blend`. This is a separate rendering copy of the current campus model, with all 15 file textures packed. The original master and Unreal project are unchanged.

## Finished views

- `stills/01_Entrance.png`: entrance and sightline into the building.
- `stills/02_Commons.png`: main room, fireplace pier, glazing, lounge seating and upper-level connection.
- `stills/03_iLab.png`: wider view across the Innovation Lab workstations and equipment.

Each finished PNG is 1920×1080, 16-bit RGB, displayed through AgX. Matching multilayer EXRs contain scene-linear color and 14 render-pass parts, including combined, denoising data, depth, normals, diffuse, glossy and emission. JPEG previews are convenient viewing copies; the PNG/EXR files are the originals. `stills/Three_Views.jpg` is the contact sheet.

## Scene preparation

Physically scaled wood, masonry, paving, sage fabric and warm plaster; subtle metal/porcelain edge shading; softer glass reflections with a shadow-ray transmission approximation; atmospheric daylight, warm interior fixtures and restrained architectural depth of field at f/8. Large presentation fill lights are hidden in this copy. Mannequins are hidden through their original collection, which can be re-enabled.

The building retains all 3,422 meshes and the original animated `Walkthrough_Camera`. No technology props were replaced. Their existing simplified geometry is still apparent in the iLab close-up. The three new still cameras are in `CYCLES - architectural still cameras`; `02_Commons` is the saved active camera.

## Rendering and measured speed

Use `Render_Stills.ps1` to reproduce the final batch. In Blender's GUI, set Preferences → System → Cycles Render Devices to **CUDA**, enable the RTX 4090, and keep Render Properties → Device on GPU Compute. The render script selects the same device explicitly without changing your global preferences.

**CUDA was used for the delivered results.** OptiX initialization did not finish within the test window on this setup; CUDA immediately rendered the same scene successfully. No CPU-render substitution or sample reduction was used for the final images.

Settings: Cycles, adaptive sampling with a 256-sample maximum and 0.01 noise threshold, OpenImageDenoise, 12 total bounces, 4 diffuse/glossy bounces, 12 transmission bounces, persistent data, 1080p at 100% scale. Color grading uses AgX Medium High Contrast with +0.2 exposure.

| View | Measured seconds |
|---|---:|
| Entrance | 26.09 |
| Commons | 15.43 |
| iLab | 17.41 |

Timings include scene synchronization, rendering, denoising and EXR writing; the first view has initial setup overhead. PNG export follows each timed render. The three views finished in about one minute, excluding the earlier OptiX investigation.

At the measured 15–26 seconds per frame, a 20-second video at 24 fps would take roughly **2–3.5 hours** at these settings. This is an estimate from three still views, not an animation benchmark. A short sequential motion test should check temporal denoising, glass noise and depth-of-field continuity before the full walkthrough.

## Validation and reproducibility

`scene_validation.json` verifies a reopened scene, camera retention, unchanged mesh count, packed textures and the source-copy hash. `image_validation.json` verifies all three 1080p/16-bit PNGs and the multipart EXR passes. The final images were also visually inspected.

`Source_Copy.blend` is the preserved input. `build_studio.py` rebuilds the isolated rendering scene; `render_stills.py` produces the final files and records timings. Use `--preview` after the Blender script separator for explicitly labeled 960×540, 32-sample lighting previews. Source textures and licensing are in `assets`. Rebuilding overwrites only this folder's generated studio file; retain a new version before making further artistic edits.

Master SHA-256: `df9a8c1c453a1e4b2885c9e017a2bee4bbd4b811b1078172fa146e161ec09308`.
