# Furnished ground-floor print and informational projection â€” v04

Created September 14, 2026. An isolated derivative of the current ground-floor structure and furnished projection scene. Earlier building, printing and projection files are preserved.

## Start here

Print the six individual STL or 3MF files in `print_tiles/` at 100% scale in millimetres, flat underside down. The two formats contain equivalent geometry. The assembled 3MF is an alignment reference; the STEP contains the complete furnished floor as a single CAD solid.

## Physical model

| Property | Value |
|---|---|
| Scope | Ground floor, fixed furniture, supported stairs and existing structural footprint |
| Scale | 1:87.5; the same size as the earlier 4Ã— projection print |
| Assembled size | 743 Ã— 562 Ã— 53.568 mm |
| Floor thickness | 4.8 mm |
| Tile arrangement | 3 columns Ã— 2 rows; six independent closed solids |
| Furniture sampling | 0.5 mm in plan; heights rounded upward in 0.2 mm steps |
| Fine-feature reinforcement | 0.5 mm outward in plan, restricted to the existing floor |
| Extra ground plane | None |
| Print orientation | Flat underside directly on the bed; Z upward |

The furniture is physical geometry. It includes simplified commons tables and seating, cafÃ© counters and equipment, classroom tables/desks/chairs, iLab worktables and machines, office furnishings, locker banks and benches, bathroom fixtures, and floor-connected fixed elements present in the source scene.

Tables and chairs have filled undersides rather than open legs. Machines and fixtures are solid blocks or relief forms that extend down to the floor. Fine internal mechanisms, foliage, people and overhead objects are omitted. The result prioritizes robust recognizable silhouettes and receiving surfaces at this scale, rather than miniature moving parts. Adjacent small components may merge after reinforcement.

The structural outline, wall heights and stair geometry come from the existing support-free ground-floor print. This revision adds the furniture; it is not a new dimensional survey of the blueprints.

## Print and assemble

1. Use a matte white material so projected colors remain readable. Orient each tile as supplied, with its flat underside at Z = 0. Do not rotate it onto a side. Print at 100% scale in millimetres.
2. Turn supports off. Start with your established PLA profile; 0.16â€“0.20 mm layers and a 0.4 mm nozzle are reasonable starting settings for these reinforced forms. Adjust walls/infill to your material and printer. The CAD volume describes the outer solid, not a requirement to print at 100% infill.
3. Check the slicer preview, particularly narrow walls and chair backs. Each tile needs up to about 248 Ã— 281 mm of bed area before any brim. A smaller printer will need new subdivisions; shrinking just one tile breaks the fit and projection registration.
4. Arrange the north row **B1 Â· B2 Â· B3** above the south row **A1 Â· A2 Â· A3**. Match the shared cut edges in `Assembly_Map.png`. The east-side entrance is on the right.
5. Butt the six seams together on a flat surface. The tiles have no additional interlocking tabs or alignment pins. Their irregular outside edges do not all share the same local origin; use the assembly map or the assembled 3MF rather than aligning bounding-box corners.
6. Secure the arrangement so it cannot shift during projection. Avoid glossy paint on receiving surfaces.

![Tile assembly, viewed from above](Assembly_Map.png)

| Tile | Size X Ã— Y Ã— Z (mm, rounded) | Position of tile's local origin in assembly (X, Y mm) |
|---|---|---|
| A1 | 247.667 Ã— 197 Ã— 48.768 | 13, 92 |
| A2 | 247.667 Ã— 270 Ã— 48.768 | 260.667, 19 |
| A3 | 247.667 Ã— 281 Ã— 53.568 | 508.333, 8 |
| B1 | 247.667 Ã— 281 Ã— 48.768 | 13, 289 |
| B2 | 247.667 Ã— 281 Ã— 48.768 | 260.667, 289 |
| B3 | 219.667 Ã— 281 Ã— 53.568 | 508.333, 289 |


## Digital checks

All seven STL files and seven 3MF files were independently reopened. Every individual tile is watertight, connected and consistently wound, with no elevated downward-facing surface. The STEP reopened as one valid CAD solid. Physical printing remains to be tested. See the included JSON reports.
