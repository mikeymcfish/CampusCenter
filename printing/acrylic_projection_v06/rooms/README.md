# Ground-floor H3 room references  -  r07

Open index.html, select a room's reference pack, upload its images in numbered order, then paste its H3 prompt. Each room has 2-9 image references and a 12-second prompt. The iLab uses all nine slots: overhead, cinematic iLab, Bambu H2D + AMS 2 Pro, Formlabs, BigRep, WAZER, Epson garment printer, UV flatbed printer, spray booth.

Picture 1 is the exact orthographic geometry and mask authority. Photographic and object references control appearance only: never camera, room location, object placement, dimensions or furniture counts. Some cinematic references depict related campus spaces and are explicitly identified. Original architectural render references guide furniture and banner appearance. Fixture-plan excerpts guide equipment identity, not projected drawing labels. Product pictures are existing project references; exact installation variants are not inferred where undocumented. No Prusa reference is included.

Walking is included in circulation and occupied rooms, with fully clothed students, safe clear paths, natural stride and loop closure. Private stalls and showers have no activity; utility/storage rooms stay unoccupied. All shots are fixed top-down, sharply focused, with fixed lighting and black outside the room mask. Reapply Room_Mask_1024.png after generation and review anatomy, collisions, object counts and the seam; H3 does not guarantee precise registration or seamless motion. No H3 videos have been generated.

Topdown_Alpha.png and Topdown_Black.png are 1024-square overhead references. Room_3D.png is a separate Blender cutaway available for inspection; it is NOT displayed on the gym floor. Gym display photographs are in ../projection/cinematic. The original geometric files remain unchanged.

Prompt source: manual official-format rewrite. Suggested handoff: semantic ref2va/r2va, 12 seconds, 24 fps, 1:1 framing, 768-pixel short edge (hosted 768P where supported). No generation was submitted.

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
