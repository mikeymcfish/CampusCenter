# Artwork and trophy displays

**Final review: 8.0/10 after four rounds; the requested 8.5 and zero-visible-errors gate was not met.** All decal placement requirements were visually verified. Remaining issues include floor transitions, lighting continuity and material realism. See [final critic report](critic_round_4/review.md).

Current Unreal map: `/Game/Campus/Maps/CampusCenter_ArchitectDecals_v04`.

## Requested additions

- **Nine supplied artworks** on the gym's south wall, facing the Innovation Lab's north glass frontage. Artwork is upright, proportionally sized, and mounted on a cork field over an oak dado.
- **Ten supplied trophies** on the gym's west wall opposite the locker rooms. The mesh decals share a shelf baseline of **180.5 cm**, 13 cm above the existing display case. A wood shelf, brackets and a warm taupe backing provide the mounting context.
- All 19 original PNGs are preserved in `source/Decals`. `asset_inventory.json` records source hashes, dimensions and alpha bounds. Material UV cropping removes transparent margins without modifying the images. Both supplied bell images are included.

Use `../Launch_Unreal.cmd` to walk or `../Edit_Commons_Dusk.cmd` to edit, with Unreal Engine 5.8.2 installed. Run `git lfs pull` after cloning. The older standalone packaged executable has not been rebuilt.

## Preservation and implementation

The original Dusk map, prior architect-finish map and Blender master are retained. Furniture is preserved. Additive display geometry has no collision, so the existing walkable surfaces remain in use. This update does not establish a new performance benchmark.

`delivery_validation.json` compares the saved maps, checks source PNG hashes and records the dependency closure. The only permitted change to an existing mesh actor is the architectural finish layer: corrected outward normals and map-local material overrides. Its replacement mesh is in `/Game/Campus/ArchitectFinishesV06`; the earlier mesh is retained.

The finish correction repaired 1,550 inward-facing closed boxes in the isolated architectural layer. `geometry_preservation.json` confirms the same 51,284 vertex positions and multiplicities before and after the normal correction. The corrected mesh retains a full-triangle Nanite fallback. Additional changes include nonperiodic ceramic variation, photographic oak grain with restrained normal detail, a stacked-stone pier treatment and a plaster band above the artwork. The final pass adds physically scaled 108 x 18 cm oak planks in the two display corridors and softens Commons lighting.

## Independent visual review

Each round uses a separate art critic that writes no implementation code and launches its own saved-map captures. Reviews cover front, oblique and close views of both displays, plus Commons, K wall, ceiling and floor. The requested gate is at least **8.5/10 with zero visible errors**.

See `review_summary.json` and the `critic_round_*` folders for final scores, evidence and remaining issues. Round 1 has nine actual images and a missing close-up despite its original capture manifest; its review records that limitation. Subsequent capture scheduling waits for each actual image before advancing.

These are screenshots of the actual Unreal scene. Exact architect-pattern matching remains a visual review criterion, not a claim established by successful asset import.

## Authoring records

`build_decal_layer.py` builds an isolated display GLB/Blend. `correct_finish_normals.py` loads only the finish collection from an isolated authoring copy. `apply_round3.py` records the ordered installation and refinement operations. Stage scripts are construction history and should not be rerun blindly over later edits. The saved map is the delivery artifact.

`sync_delivery.py` copies the validated dependency closure, supplied images, authoring scripts and review evidence into the existing Git repository. It verifies copied binary hashes and removes the local Android file-server token from published configuration.
