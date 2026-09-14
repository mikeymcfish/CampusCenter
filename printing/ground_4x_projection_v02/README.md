# Campus Center: direct overhead projection v02

This is projector content for the existing four-times enlarged ground-floor print. It is a flat, vertical top-down map: the physical walls, stairs, raised surfaces and exterior remain black. The furniture is an image projected onto the room floors. It is not a perspective photograph of a model.

## Files to use

- `Projection_Loop_Lossless_RGB.mp4`: projector master, 1024 x 786, six seconds, exact RGB preservation. Use a player that supports lossless H.264 RGB, such as VLC, with repeat enabled.
- `Projection_Loop_Preview.mp4`: ordinary H.264 viewing copy. Its lossy compression can soften black edges; use the lossless master or PNGs for actual projection.
- `Projection_24_Images.zip` / `frames/0001.png` through `0024.png`: exactly 24 finished projection images in loop order. Each image lasts 0.25 seconds. The videos repeat each keyframe six times at 24 fps; there are still 24 unique images and motion has a four-frames-per-second cadence.
- `Projection_Base_Top_Down.png`: the fixed furnished projection with no people.
- `floor_only_mask.png`: binary floor validity mask. White receives imagery; black receives no image light. Includes a conservative one-output-pixel inset around the printed wall boundaries.
- `Calibration_25mm_Floor_Only.png`: 25 mm checker squares at the intended physical scale, clipped to the floors.
- `Projection_24_Frame_Loop.blend`: editable projection composition. Disable **IMAGEGEN PEOPLE - disable to show base only** to hide people. Keep the neighboring `imagegen_raw` folder and PNGs with this file.
- `Campus_Center_Top_Down_Projection.blend`: isolated furnished source scene with the exact printed receiving shell, orthographic overhead camera, static soft illumination and black wall materials. Images packed.
- `imagegen_raw/people_0001.png` through `people_0024.png`: 24 original Imagegen character-frame assets. Each contains the four students; magenta is a keying background and is removed by Blender. These raw assets are not projector playback frames.
- `imagegen_prompts.json` and `prompts/`: complete generation prompts, references and source provenance. Generated with the built-in image generation tool, which exposes no explicit model-version selector.
- `validation.json`, `scene_validation.json` and `DELIVERY_MANIFEST.json`: output, source-integrity and delivered-file checks.

## Alignment

The existing six ground-floor print tiles are unchanged and remain in `../ground_4x_projection_v01/`. Assemble them as previously documented: total footprint **743 x 562 mm**, architectural scale **1:87.5**, no additional ground plane.

Mount the projector directly overhead, pointing straight down. Keep north toward the image top. The full projected image canvas is **790.426 x 606.713 mm**, centered at assembly coordinates **X 384.5, Y 289 mm**. The printed model occupies about 94% of the image width. The model's assembly coordinates run X 13 to 756 mm and Y 8 to 570 mm. The top of its floor slab is Z 4.8 mm in print coordinates.

1. Display the floor-only checker pattern. Set playback to fit the entire image without cropping or stretching its aspect ratio.
2. Adjust projector position, image size and rotation until the floor edges fit the print, and check several squares measure 25 mm. Fit the physical wall lines to the black channels between rooms.
3. Check the outer rooms and the central gym at the same time. Correct lens distortion or residual alignment with the projector/mapping software if needed. Keep the same transform for the base and all 24 frames.
4. Play the lossless loop, with controls and overlays hidden. Nothing in the output animates the lighting or sunlight.

This alignment is derived digitally from the printed floor geometry. It has not been tested with the physical print and projector. Direct overhead placement is assumed; actual lens distortion, print tolerances and projector black level still require setup on site.

## Motion and source preservation

The four generated students move around small closed paths in the commons, west corridor and iLab central aisle. Their positions and headings return to the starting state at the next cycle. Generated limb poses are approximate and can vary slightly between images; this is a 24-image concept loop, not motion-captured animation.

The furnished base is identical in every image. There is no moving sun, wall lighting, fire flicker, camera movement, or AI regeneration of the building. Imagegen created only the people artwork; Blender placed, keyed and masked it onto the fixed base. Each finished PNG and each decoded lossless video frame is verified black outside the valid floor mask. Source Blender and print files were preserved.

Authoring files are included for reproducibility. The projection source uses Blender 5.0. The floor-only mask excludes all printed faces above the main floor elevation, including stair tops, rather than trying to project an incorrectly aligned image on them.
