# Campus additions V08 — 2026-09-27

Saved in the existing map `/Game/Campus/Maps/CampusCenter_StandardAssets_v07`. The normal `Edit_Commons_Dusk.cmd` launcher opens this map.

- Added six complete three-part MacBooks using the user's imported model: desks 104 and 111, group tables 112 and 113, study desk 209, and visitor table 202.
- Added six matching imported coffee cups, one on each of those surfaces. Existing props are retained.
- Enlarged all ten `DD_Trophy_05` through `DD_Trophy_14` images by 45% in width and height. Their bases stay at shelf-top height (180.5 cm). They remain flat image cards, so enlargement does not give them three-dimensional silhouettes from oblique angles.
- Added two three-row bleacher banks along the gym's east wall, with 72 nominal seating positions, navy seats, aluminum decks, outer/back rails, and a 180 cm central aisle with four 15 cm steps. Central row entries are open. New geometry uses BlockAll collision; no player walking test was performed.

Find new actors in `V08 additions/Tabletop props` and `V08 additions/Gym bleachers`. Trophy actors retain their original labels/folder.

## Verification

Every added prop's full bounding box fits its assigned tabletop with at least 2 cm of edge clearance and a 0.1 cm surface offset. Native lit screenshots were inspected for all six placements and the gym/trophies. The upper rooms are dark under existing lighting; separate unlit diagnostic screenshots check their placement without changing lighting.

The preservation comparison checks actor count, labels, classes, positions, rotations, scales, mesh references and material assignments. All 1,259 original actors outside the ten intentionally resized trophies pass unchanged. Editor-only camera helper meshes are excluded from the comparison because commandlet and GUI editors instantiate them differently. The saved map has 1,491 actors: original 1,269 plus 24 prop parts and 198 bleacher parts. No landscape, student animation, furniture, or existing asset material was edited.

See `props_report.json`, `trophies_report.json`, `preservation.json`, `saved.json`, and the visual gallery `review.html`. Original map backup: `backup/CampusCenter_StandardAssets_v07.umap`, with its SHA-256 in `backup/map_hash.json`.

The scripts are a record of this one-time edit, not an idempotent installer; do not rerun placement scripts on the finished map.
