# Campus Center: lively floor projection v03

A direct, vertical top-down projection for the existing enlarged ground-floor print. The building stays registered to the original print mask. Walls, raised stairs and the exterior receive black pixels. Lighting is fixed throughout the loop.

## What changed

- **93 students:** 53 seated in study/social groups, 10 in face-to-face conversations, 18 basketball players/spectators, and 12 walking around the building. Generated overhead photographs supply their appearance and activity poses.
- Maple gym flooring with board variation, basketball markings, navy keys, center and baseline KING lettering, hoops, nets, sideline benches and a passing basketball.
- Varied terrazzo, ceramic tile, workshop flooring and blue commons carpeting, with softer reflections and local surface detail.
- 15 laptops, 25 notebooks, 10 cups, maker project parts, locker details, changing benches, bags and 12 leafy plants. Existing furniture and equipment positions are retained.
- **144 rendered frames at 24 fps**, making a six-second loop. The 24 reference images sample this animation every quarter second; the video no longer holds each image for six frames.

The court graphics and added dressing are representative design details, not a verified survey of the existing gym's painted markings. Students use repeated source poses and small looping motions; this is a photographic projection composition, not a simulated basketball game or a rigged crowd.

## Files to use

| File | Purpose |
|---|---|
| `Projection_Loop_Lossless_RGB.mp4` | **Projector master**, 1024 x 786, 24 fps, six seconds. Exact RGB preservation keeps black areas black. |
| `Projection_Loop_Preview.mp4` | Ordinary H.264 viewing copy. Compression can soften the black edges; use the master or PNGs for projection. |
| `Projection_Hero_3x.png` | Detailed 3072 x 2358 still of the populated scene. |
| `Projection_24_Images.zip` | Exactly 24 finished reference frames, plus the base, mask, calibration image and this guide. |
| `frames/0001.png` through `0024.png` | Reference images in chronological order, at 0.00, 0.25, 0.50 ... 5.75 seconds. |
| `video_frames/0001.png` through `0144.png` | Full 24 fps image sequence. |
| `Projection_Base_Playback.png` | Exact native playback base with people and ball hidden. |
| `Projection_Base_Detailed_3x.png` | High-resolution furnished base without people. |
| `floor_only_mask.png` | Exact v02 binary receiver mask, including its one-pixel inset. |
| `Calibration_25mm_Floor_Only.png` | Unchanged 25 mm calibration squares clipped to the floors. |

Use repeat playback with controls and overlays hidden. Keep the original aspect ratio and show the whole image. Do not crop or stretch the canvas.

## Editable scenes

`Campus_Center_Lively_Projection.blend` is the lightweight final composition. It has a fixed base and these independent collections:

- **STUDENTS - Seated study and social groups**
- **STUDENTS - Standing conversations**
- **STUDENTS - Gym players and spectators**
- **STUDENTS - Walking students**
- **COURT - looping ball**

Disable collections to reduce the crowd or show the empty furnished base. Keep the neighboring `imagegen_raw` folder with the blend file: the walking poses use its relative image sequence. All other image assets in this scene are packed.

`Campus_Center_Detailed_Projection.blend` contains the actual furnished 3D source, overhead camera and fixed lighting. New court, plants and props are in **V03 PROJECTED DETAIL - floor content only**. `Fixed_Base_Compositor.blend` applies the existing floor mask to the source render.

The photographic people in the final projection are flat overhead image planes. They have not been added as 3D characters to the full architectural walkthrough model. The original model and print files are unchanged.

## Physical alignment

The six existing ground-floor print tiles remain unchanged in the v01 print package. The assembled footprint is **743 x 562 mm**, architectural scale **1:87.5**, with no added ground plane.

The image canvas maps to **790.426 x 606.713 mm**, centered at assembly coordinates **X 384.5, Y 289 mm**. The model's assembly bounds are X 13 to 756 mm, Y 8 to 570 mm. Its main floor slab top is Z 4.8 mm. North stays toward the image top.

1. Mount the projector directly above the print, pointing straight down.
2. Display the calibration image and fit its floor edges to the physical model. Several checker squares should measure 25 mm.
3. Fit physical wall lines into the black channels. Check the outer rooms and central gym together; adjust lens correction or mapping software if needed.
4. Use that same mapping for every frame and video. There are no camera moves or changing sun shadows.

Alignment is verified digitally against the existing mask. It has not been calibrated on the physical print/projector; lens distortion, projector black level and print tolerances still depend on the hardware setup.

## Provenance and checks

`assets/` contains three unmodified Imagegen sheets: seated students, conversations and basketball poses. `new_imagegen_prompts.json` records their prompts. `imagegen_raw/` contains the 24 unchanged walking-pose sheets from v02; `walking_imagegen_prompts.json` preserves their generation records. Magenta backgrounds are keyed in Blender. The image-generation tool did not expose a model-version selector.

The Blender source and fixed floor mask determine all building geometry and alignment. Imagegen did not redraw the building. All furnishing, material and lighting detail is baked once, so the surroundings cannot drift between frames.

`validation.json` records image counts, exact blackout checks, source preservation, loop checks, and bit-exact decoding of the lossless master. `scene_validation.json` records reopening the saved blend file and rendering it again. `DELIVERY_MANIFEST.json` records copied-file sizes and SHA-256 hashes.
