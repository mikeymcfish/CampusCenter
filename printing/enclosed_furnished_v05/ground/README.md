# Campus Center — enclosed ground floor

Standalone furnished projection-mapping print, version 05. Scale **1:87.5**. Units **millimetres**. This is a schematic display model, not construction documentation.

The exterior perimeter is closed with solid walls, including external door and glazing openings. Original internal openings, furniture, stairs and lower patio geometry remain.

## Print and assemble

- Use the six individual STL or 3MF files in `print_tiles`. They are already flat on Z=0 and oriented for support-free printing. Each file contains one connected solid.
- The largest tile footprint is 247.7 x 281.0 mm. Check available bed area including any brim. Do not use automatic fit-to-bed scaling unless every part and the projection scale are changed together.
- Furniture is filled to the floor/bed beneath seats, tables and equipment. It is intentionally simplified; no floating furniture or under-table overhangs.
- A 4.8 mm floor supports the rooms. There is no supplemental ground plane and no stacking interface. Exterior walls are solid, with no overhead lintels bridging empty openings.
- Keep north at the top of `Tile_Assembly.png`. A1–A3 form the south row; B1–B3 form the north row. Align and butt-join the flat cut edges on a level surface. No added pins, sockets or interlocking features are included.
- The assembly 3MF preserves all six parts at their correct global positions. It is an alignment reference, not a one-bed plate arrangement. Print the individual part files.
- Use matte white material for the receiving surfaces. Verify bed adhesion and thin details in your slicer. Geometry checks passed; a physical test print has not been performed.

| Piece | Size X x Y x Z (mm) | Assembly offset X / Y / Z (mm) |
|---|---|---|
| Ground_A1 | 247.7 x 197.0 x 48.8 | 13.000 / 92.000 / 0.000 |
| Ground_A2 | 247.7 x 270.0 x 48.8 | 260.667 / 19.000 / 0.000 |
| Ground_A3 | 247.7 x 281.0 x 53.6 | 508.333 / 8.000 / 0.000 |
| Ground_B1 | 247.7 x 281.0 x 48.8 | 13.000 / 289.000 / 0.000 |
| Ground_B2 | 247.7 x 281.0 x 48.8 | 260.667 / 289.000 / 0.000 |
| Ground_B3 | 219.7 x 281.0 x 53.6 | 508.333 / 289.000 / 0.000 |

Assembled size: 743.0 x 562.0 x 53.6 mm. The full STL, STEP and assembly 3MF use the same coordinates. The STEP is a valid closed faceted B-representation, not a reconstructed parametric architectural model. Blender files use metres.

## Projection show

Open `information/index.html` to review the six-chapter, silent **42-second loop**. The RGB masters are 2048 x 1572 and 1024 x 786. Use an RGB master in mapping software; the smaller review MP4 is for convenient playback, not pixel-exact blackout.

Both new levels use a common **830 x 637.08984375 mm** projection canvas, centered at print XY **398 / 289 mm**, north up. This differs from the older v04 canvas. Do not mix v04 video or masks with these parts. Keep the full black margins and image aspect ratio.

Use `Calibration_25mm.png` for alignment. Assume a direct vertical overhead projector. Aim, focus, keystone/perspective and lens calibration must be adjusted on the physical model; the files alone cannot guarantee registration. Walls, voids and the surrounding table are black. Illuminated content is limited to modeled floor and furniture receiving surfaces, inset by a small pixel safety margin. There are no moving sun shadows or projected crowd videos.

`Campus_Center_Furnished_Print.blend` is the isolated print mesh; `Campus_Center_Projection_Receiver.blend` contains the fixed overhead mask camera. Source architecture and furnished studio files were preserved.

Validation reports record watertightness, connectedness, support geometry, assembly equivalence, reopened STEP solids, and lossless-video decoding.
