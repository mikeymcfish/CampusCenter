## Artwork and trophy update — September 25, 2026

The current launchers open `/Game/Campus/Maps/CampusCenter_ArchitectDecals_v04` in **Unreal Engine 5.8.2**. Added **9 supplied artworks opposite the Innovation Lab** and **10 trophy decals on an oak shelf opposite the locker rooms**. Existing furniture is preserved. The shelf clears the existing case by 13 cm.

[Scope and verification](decal_update_v02/README.md) | [Final independent review](decal_update_v02/critic_round_4/review.md) | [Artwork view](decal_update_v02/critic_round_4/01_art_gallery_wide.png) | [Trophy view](decal_update_v02/critic_round_4/04_trophy_shelf_wide.png)

**Final critic score: 8.0/10 after four rounds (6.2, 6.8, 7.6, 8.0). The requested 8.5 and zero-visible-errors gate was not met.** Decal placement, orientation, transparency and shelf contact were verified. Remaining issues are abrupt floor transitions, uneven lighting and simplified material response. Exact architect-pattern matching is not established.

Saved-map validation reports zero errors, 974 unchanged existing mesh actors, all 19 supplied decals and exact trophy-to-shelf contact. Only the existing architectural finish actor was replaced, preserving all vertex positions while correcting normals and applying material overrides. Originals are preserved. `DECAL_ASSET_MANIFEST.json` records the current map dependency files and hashes.

Run `git lfs pull` after cloning. Use `Launch_Unreal.cmd` to walk or `Edit_Commons_Dusk.cmd` to edit. The legacy standalone executable and its older performance claims do not apply to this update.

---
