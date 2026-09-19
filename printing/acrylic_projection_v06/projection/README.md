# Projection Studio — ground floor v06

Run `../Start_Projection.cmd` (Python 3 required), or `python ../serve.py`. Open http://127.0.0.1:8769/projection/. The server binds only to your own computer. Close its terminal to stop it. No Internet service or external library is used by the player.

## Modes

- **Explore:** WASD/arrows move a small top-down person at **2× the original speed by default (40 map pixels/second)**; the Walking speed menu offers 1×–4×. Walls and furniture block movement. Entering a room highlights its receiving surfaces and displays a cinematic ImageGen photograph on the gym floor. Optional destination selection walks a calculated route through the same open doorways; it does not teleport. R resets. Space pauses. Thirty rooms/areas are reachable. Mechanical/electrical room 120 has no connecting doorway in the current modeled door schedule; its reference images are included, but it is intentionally not reachable in the game. No doorway was invented.
- **Ink map:** original geometry-derived drawing with irregular grid, hatched edge bands and furniture contours. The animated `Ink_Map_Loop` file adds a gentle looping illumination sweep. The supplied Dyson Logos drawing was a style reference, not copied artwork.
- **Align:** 25 mm physical grid, numbered crosshairs, green receiving edges and amber furniture tops. Exact target coordinates are in `calibration_points.json`.
- **Height contours:** animated levels use the final mesh's actual top-surface height and distance from edges.
- **Surface ripples:** circular waves use a 3D distance field, so their phase changes over raised furniture.
- **Architecture scan:** moving light responds to height and surface normals. These are modeled-geometry effects inspired by Lightform's depth/normal/edge workflow, not a Lightform scan or a replacement for its software.

## Projection setup

The native artwork is 1024 x 786, representing an **830 x 637.08984375 mm** canvas centered at printed XY **398 / 289 mm**. The 2048 x 1572 masks in `../print/` and `../rooms/` use the same registration. North is up. Do not stretch the image to fill a 16:9 screen; black side margins are expected.

Place the projector directly overhead, perpendicular to the assembled model. Match rotation, size and position using Align. Aim for optical/lens-shift alignment before keystone correction. Match the physical model to the green edges and the furniture to amber patches; check at least four distant numbered targets. Project fullscreen with F; Escape/F exits. Only the canvas is shown in fullscreen, with no focus outline or controls. Physical calibration and acrylic glare remain untested.

Artwork excludes wall tops, exterior ground and clear acrylic. Acrylic door lights sit in closed-door print datums; logical game movement follows the original open architectural portals. The person can briefly disappear behind these black threshold strips, which is intentional blackout rather than a route through a wall. Screens and steep vertical sides cannot receive light from a strictly vertical projector; effects primarily address floors and upward-facing furniture surfaces.

## Files and video color

`examples/*_1024x786_RGB.mp4` are lossless RGB masters. Every decoded frame was checked against its source and receiver mask; first/last frames are identical. Four effect loops are 8 seconds / 24 fps. `Explorer_Demo` is a longer automatic tour showing the same navigation/display behavior.

`*_Browser.mp4` are H.264 YUV420 BT.709 compatibility copies. Some browser/GPU combinations display lossless RGB H.264 with incorrect colors. The player therefore uses compatibility copies and **reapplies the receiver mask after decoding** to remove chroma bleed. For direct playback outside this player, use the RGB masters in a correctly color-managed player and check black margins before projection. Do not use an unmasked compatibility copy as the final projection feed.

All modes preserve the same geometry. `assets/surface_data.npz` contains rasterized final-STL height in mm, normal vectors, edge distance and masks. `assets/navigation.npz` contains logical navigation derived separately from the architectural plan and printed furniture. `map.json` documents room IDs, targets, image locations and the gym panel. Black margins are geometric masks, not a promise that a real projector emits zero light.

## References

Style: https://dysonlogos.blog/wp-content/uploads/2021/06/clue-mansion.png?w=600

Effect concepts: https://lightform.notion.site/Lightform-Creator-Overview-ce40b9518ed44605bbf0b88bde161fed and https://lightform.notion.site/Built-in-Asset-Library-9267a452b51d44a98cca354d0baaeb91

No reference-site assets or Lightform code are redistributed. Existing building textures and artwork remain governed by the project's existing source/attribution records.

## Cinematic display and H3 references — r07

The gym uses five ImageGen photographs, including a new wide iLab image. Related-area photographs are shared where a room has no unique cinematic shot; the gym caption explicitly says RELATED VIEW. No gym assignment uses a Blender cutaway. Source provenance is in cinematic/Provenance.md. Room reference packs at ../rooms/index.html list exact H3 upload order, including nine references for the iLab and walking students in fixed overhead loops.

## r08 print correction

The innovation-lab patio is open at its free edges. Its platform and adjacent building walls are preserved. Both three-row gym bleacher banks are removed. All six print tiles remain single connected, watertight solids, with no elevated downward-facing faces. The scale, assembly registration, 40 acrylic pane dimensions and 1.85 mm slots remain unchanged. Updated masks, previews and projection videos match this geometry. The full architectural Blender source remains unchanged.
