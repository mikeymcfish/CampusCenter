# Ground-floor acrylic print and projection package — v06

## Start here

1. **Print pieces:** `Ground_Acrylic_Print_Package.zip`, or `print/print_tiles/`. Six supported STL/3MF pieces, a solid STEP, a fit coupon, 40-pane cut list, 1:1 SVG cut sheet, placement map and assembly notes. Print the coupon first. Nominal **1/16-inch acrylic** fits the **1.85 mm** channels; no extra ground plane was added.
2. **Room references:** open `rooms/index.html` or `rooms/Room_Contact_Sheet.jpg`. **31** ground-floor rooms/areas have masked **1024-square orthographic renders**, transparent and black-background PNGs, exact masks, and an individual **12-second H3 loop prompt and a numbered 2–9-image reference pack**. No H3 generation has been run. Each also has a **1280 x 960 oblique cutaway** for inspection; the gym display now uses cinematic ImageGen photographs.
3. **Projection examples:** run `Start_Projection.cmd`, or `python serve.py`. The local player includes keyboard exploration, the ink map, alignment, and three depth/edge effects. See `projection/README.md`. The `projection/examples` folder includes four 8-second loops and an automatic exploration demo, plus still previews. `projection/review` shows the artwork on the 3D print.

## Geometry and validation

The final print and all six pieces are connected, watertight meshes with no elevated downward-facing surfaces in the mesh support check. All eight 3MFs were independently reopened. The STEP reopens as one valid closed faceted solid and matches the STL volume. Forty acrylic insertion envelopes were checked for collision. These digital checks do not replace a slicer preview and physical fit coupon.

Projection masks were regenerated from the final print. Height/normal/edge data come from that same final STL, rather than an older height grid. RGB video masters were decoded frame by frame; every frame matches its source and is black outside receiving surfaces, with identical first/last frames. The browser uses BT.709 compatibility copies and reapplies the mask after video decoding.

Interactive browser checks covered keyboard movement, blocked wall steps, a doorway route from the entrance to the iLab, room highlights and gym images, all 31 room image assignments, fullscreen, animation colors and receiver blackout. Thirty areas are connected in the modeled door graph. Mechanical/electrical room 120 has no connecting door in the current model and is excluded from walking routes; its room images are still included.

The architectural scene was preserved. Cutaway rendering operates on copies, clips walls at 3.4 m for visibility and removes foreground partitions as an illustration convention. These oblique pictures are not calibrated projection images. The exact overhead references use no perspective or depth of field. Open-space masks are display zones, not new walls or certified room-area measurements.

## Sources and editing

Source scene: `cycles_studio_v05/Campus_Center_Cycles_Studio.blend` in the main workspace (also delivered previously as the Cycles Studio v05 package). Source plan geometry: `output_3d_v4/model_geometry.json`. Existing attribution/source records still apply. Source file hashes are in `delivery_validation.json` and `scene_inventory.json`.

Build/render scripts are included for traceability. They use the project's existing Python mesh/CAD dependency folders and installed Blender 5.0; they are not a standalone CAD application. The interactive player itself needs only Python 3's standard library and a modern browser.

Actual acrylic tolerances, printer fit, projector alignment, glare and optical shadowing have not been tested physically. Transparent panes and vertical walls are deliberately excluded from receiving masks. Start with the coupon and alignment image before a full print or projection session.

## r07 update

Walking defaults to 2× original speed with a 1×–4× selector. The gym displays five ImageGen photographs; shared related-area images are labeled clearly. Every room has References.html / References.md with H3 upload order and appearance-only roles. The iLab pack uses nine images including two Bambu H2D printers with AMS 2 Pro units. Occupied-room prompts include students walking in clear aisles; service rooms remain unoccupied. Print geometry and source Blender scene were not changed.

For regeneration, the r07 update script applies after original room/player generation and before package_delivery.py. Do not run it twice on an already updated player; restore its player/index backup first.

## r08 print correction

The innovation-lab patio is open at its free edges. Its platform and adjacent building walls are preserved. Both three-row gym bleacher banks are removed. All six print tiles remain single connected, watertight solids, with no elevated downward-facing faces. The scale, assembly registration, 40 acrylic pane dimensions and 1.85 mm slots remain unchanged. Updated masks, previews and projection videos match this geometry. The full architectural Blender source remains unchanged.

## CGlide packages and text encoding

Revision 11 - overhead first-frame image-to-video
Import with H3 Studio > Project > Open. Reopen the downloaded project to
replace previously loaded shots; opening the web page does not update them.
CGlide mode: FL2VA with FIRST populated and LAST empty (image-to-video).
Required installed diffusion model: minimax_h3_fl2va_pruned_int8_convrot.safetensors
Video VAE: minimax_h3_video_vae_fp16.safetensors
Audio VAE: minimax_h3_audio_vae_fp32.safetensors
Select the FL2VA diffusion model in the ComfyUI workflow yourself; project
imports do not change the external model loader. Do not use the Ref2VA model.
Only the exact overhead opening image is embedded. Appearance/product
references have been removed from conditioning; their details are in prose.
768 x 768, 24 fps, 294 frames / 12.25 seconds. Do not enable Carry/Chain.
Static camera requested; first-frame conditioning does not guarantee a fixed
camera throughout or a seamless loop. No generation was submitted or tested.
Existing people in the opening image provide the best motion starting point;
additional requested people may emerge gradually if absent in the image.
Masks are post-generation files, not conditioning inputs. Masking does not
correct internal camera drift. Inspect results before using for projection.
Prompt source: manual official-format rewrite.


## Revision 12: tested room video loops

[Five-room playback and comparison](experiments_r12/index.html), [delivery notes](experiments_r12/DELIVERY_README.md), and [complete ZIP](experiments_r12/Campus_Projection_R12.zip). Includes iLab, commons, both locker rooms and gym; matching first/last images, actual Blender depth tests, masked lossless masters and CGlide projects.
