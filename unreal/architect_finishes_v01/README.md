# Architect finish revision for the current Unreal walkthrough

## Open the current scene

Run `../Launch_Unreal.cmd` to walk, or `../Edit_Commons_Dusk.cmd` to edit in **Unreal Engine 5.8.2**. Current map: `/Game/Campus/Maps/CampusCenter_Dusk_ArchitectFinishes_v03`. The launcher retains its Dusk name for compatibility; the revised map has brighter, more neutral lighting. The older packaged executable has not been rebuilt.

## Scope and preservation

The September 22 Commons and CRI architect images guided the new cobalt staggered tile, warm herringbone timber floor, pale wood dado, cork display field, white upper wall, vertical wood/blue fin field with the K motif, perforated wood soffit material and open slat canopy. Furniture was retained. Three old full-height King banners were removed from the copied map because they covered the new wall pattern.

`delivery_validation.json` compares saved maps: **974 existing mesh actors retain their mesh, material slots and transforms**. Only the three named banners were removed and one finish mesh actor added. Lighting was adjusted for finish visibility. The new floor overlay has no collision; the original walkable floor remains in use. This is not a new traversal or performance certification.

The original Dusk map and Blender master remain byte-identical to their preflight hashes:

- Dusk map: `6859ce249fa867ef9f139e3f0568ee72bd74e6355c10c5011aa8b7288bf51255`
- Blender master: `df9a8c1c453a1e4b2885c9e017a2bee4bbd4b811b1078172fa146e161ec09308`

## Final assets and reference accuracy

The final mesh is `/Game/Campus/ArchitectFinishesV05/Architect_Finishes_v05/StaticMeshes/Architect_Finishes_v05`, using native materials under `/Game/Campus/ArchitectFinishesV04/NativeMaterials`. `Architect_Finishes_v05.glb` is the interchange construction layer. Existing actor label `Architect_Finishes_v02` is retained so the upgrade remains idempotent at map level.

`reference_batten_measurements.json` records visible wall segments measured from a perspective-rectified region of the Commons reference. The K endpoints were smoothed across highlights/occlusion. Hidden geometry, exact architect dimensions and finish product specifications cannot be recovered from these two images alone. The ceiling layout is a modeled interpretation. **An exact pattern match has not been established.** Existing building geometry also differs from the architect renders.

## Independent art director reviews

A separate no-code critic launched its own six-view capture set in each round: Commons wide, K close, CRI wide, tile close, ceiling close and upper Commons. Each folder contains screenshots and a review. Scores use the user's 8.5 pass threshold with zero visible errors.

| Round | Overall | Result |
|---|---:|---|
| [1](critic_round_1/review.md) | 5.5 | Fail |
| [2](critic_round_2/review.md) | 6.2 | Fail |
| [3](critic_round_3/review.md) | 6.0 | Fail |
| [4 final](critic_round_4_final/review.md) | 6.3 | Fail |

**Final status: the requested 8.5/10 and zero-visible-errors threshold was not achieved after four rounds.** The exact wall/ceiling pattern, CRI display treatment, material depth and lighting remain unresolved. The latest revision is delivered with this failed review explicitly documented. The final result is recorded in `critic_round_4_final/review.md` and `review_summary.json`.

The final save/dependency commandlet completed with zero errors. It emitted an existing RecastNavMesh warning and an API deprecation warning; this does not establish the visual zero-error gate. Review screenshots show the actual saved Unreal scene, not a generated image. Final captures explicitly use Lit viewport mode to match the walkthrough renderer. The first round-4 set exposed incomplete fallback geometry; that superseded diagnostic set is retained separately. The full editor rebuilt the final finish mesh with a 100% triangle ray-tracing fallback; see `fallback_repair.json`.

## Maintenance and attribution

The Git delivery includes the current map's recursive asset dependency closure, source scripts, runtime plugin, and review evidence. Run `git lfs pull` after cloning. Use the saved map for normal work; stage scripts are historical construction operations and should not be rerun blindly. The Blender construction scripts require the isolated source copy in the authoring workspace.

Current common-area attribution is in `../asset_provenance/common_area/CREDITS.md`. Wood049 texture provenance is retained in the earlier `../polish_v03` material package. No furniture assets were altered in this finish pass.
