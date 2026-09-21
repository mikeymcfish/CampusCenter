# Campus ground floor R13 - ImageGen endpoints

31 rooms; 62 endpoint files. Start and End are intentionally byte-identical for closed loops. Generated with the built-in ImageGen tool, using each Blender overhead image and a separately rendered orthographic scale guide. Human shoulder width target is 0.44 m, head width 0.18 m, guide chair seat 0.45 m. These are visual calibration references, not claims that generated pixels have engineering accuracy. Small silhouette or fixture differences can remain; the Blender model and original mask remain authoritative for projection alignment.

The Innovation Lab generation also used existing real Bambu Lab H2D/AMS, Formlabs and WAZER product photographs for appearance. Other rooms use the modeled footprints and descriptions of real materials and objects. No extra product photos are assigned to the video model, avoiding reference takeover.

Bathrooms and janitor room have no people and use subtle faucet water. Storage and service rooms remain unoccupied. Locker rooms contain clothed students. Shower trays outside the existing room crop were not invented or relocated inside it.

Import Campus_Ground_Floor_R13.h3proj.zip with CGlide Project > Open. Uses FL2VA, 768 square, 294 frames (12.25 seconds at 24 fps), matching first/last image, all semantic slots empty. Use the existing H3 FL2VA checkpoint. Endpoint equality does not guarantee the camera stays fixed in generated intermediate frames; inspect output and reapply the original room mask after generation. No new videos were generated for this revision.

Each room contains ImageGen_Prompt.txt, H3_Loop_Prompt.txt, both endpoint files, the original Blender overhead, scale guide and original 1024 mask. Original Blender files and r12 videos are preserved. generation_log.json records selected source image provenance and prompts. The three product photos in product_references are appearance evidence, not an additional CGlide input.
