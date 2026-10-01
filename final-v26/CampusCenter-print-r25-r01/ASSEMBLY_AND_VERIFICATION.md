# CampusCenter revised print package - approved v25

Editable source: `CampusCenter_Revised_Print_Edit.blend` (metres). The Outliner holds four large print variants, three matched stack layers, two optional partition states, and hidden acrylic reference panes. Show only the desired objects. Printable exports are in millimetres; do not apply fit-to-bed scaling.

The large display variants use **1:87.5**, 0.5 mm source sampling, 4.8 mm floors and the established supported-furniture convention: furniture surfaces are filled vertically to their supporting floor. No labels, QA footprint planes, people or artwork are printed. Missing detailed furniture/art remains deferred. Source iLab dimensions/layout and actual accepted equipment placements are retained; its print furniture is a simplified envelope, not manufacturer CAD.

## Print and assembly

Use individual files in each variant's `print_tiles` folder. Six three-column/two-row split regions cover each large floor; disconnected islands have numbered individual files. Every individual tile is one connected solid on Z=0 and within the project's conservative 290 x 300 x 315 mm limit. Check bed space for your brim in the slicer.

A1-A3 form the south row; B1-B3 form the north row. Use the exact offsets below and each assembly 3MF as the alignment reference. Butt-join flat cut edges on a level supporting board. No new pins, sockets or interlocks are included. Assembly 3MFs and full STLs are whole-display references, not single-bed print jobs. Small disconnected upper rail/stair accessories have their own files and offsets; place them with the board-supported assembly.

Ground furnished: open display shell. Ground enclosed: solid perimeter substitution. Ground acrylic: top-loading acrylic frames with the r08 open iLab patio convention and bleachers omitted. Upper enclosed: solid glazing substitutions and low terrace/bridge parapets; gym, commons and gallery voids remain open. These 1:87.5 displays have no stacking interface or removable roof. The below-grade patio landing/steps are flattened into the supported footprint; their real elevations are not represented in these display prints.

Interior door leaves and overhead headers are omitted, leaving accepted interior apertures open. Some external glazing/door apertures are deliberately filled or changed to acrylic channels, as established by the original display workflow. Primary raised features are reinforced by one 0.5 mm cell per side; nominal isolated narrow relief is generally 1.5 mm, subject to clipping at floors/cuts. Acrylic frames are 5.2 mm wide with 1.85 mm channels (nominal side walls 1.675 mm). Tiny tips, local joints and tall narrow accessories still require slicer review.

## Acrylic

Use `ground_acrylic/Acrylic_Fit_Coupon.stl` or its 3MF first. Five coupon channels are 1.65, 1.75, 1.85, 1.95 and 2.05 mm. Nominal acrylic is 1.5875 mm (1/16 inch). Model channels are 1.85 mm: 0.2625 mm total thickness clearance. Pane length includes 0.20 mm total end clearance. All 40 nominal pane solids and their vertical insertion envelopes are collision-free digitally. `Acrylic_Cut_List.csv`, `glazing_schedule.json` and millimetre SVG cut sheets define the inserts; SVG text is a separate group to hide before cutting. Do not print `Acrylic_Panes_REFERENCE_ONLY.stl`. No physical coupon, cutting or printer operation was performed.

## Optional research partition

The approved model is open. The folded bank and closed partition are **loose removable alternatives**; install exactly one state. Source height is 2.7432 m, or 31.3509 mm at 1:87.5. Panels are strengthened from the nominal 0.6286 mm scaled thickness to 1.5 mm. The closed insert has 0.10 mm end clearance at each end. Print the ordinary `Partition_Closed.stl` on its broad side; its `Assembly_Orientation` file is an installation reference. The folded bank prints upright. Put the assembly reference at the recorded XY offset and Z=4.8 mm, on the floor. No operating hinge, track or guessed mechanism is included.

## Matched removable set

`stacked_1_350` preserves the **1:350** original three-layer convention: print ground, upper and roof separately and stack in that order. Floors are at least 1.2 mm. Align the original shared XY coordinates; ground Z=0, upper Z=12.192 mm and roof Z=23.077714 mm. Revised structural floors are strengthened and trimmed to the established seating planes. The unchanged low athletics roof is in the upper layer. The existing supported roof recipe and solid display skylight are retained; all five authoritative roof-part bounds match accepted v25 within 0.000002 m. There is no supplemental rectangular base or new locking feature.

Both seating interfaces passed contact-area and projected-centroid checks. Numerical intersection volumes are below 0.001 mm3; these are floating-point residue, not a physical fit test. Remove the upper and roof pieces to inspect the revised room layout.

## Source and validation

Approved visual geometry: `scene/Campus_Center_New_Plans_Audit_v25.blend`, SHA-256 `c39e7b686b56603f38500f1b22d6ebbb459362e66fa255da1a4b315e4a216721`. Metres, unit scale 1; the original file's hash is unchanged after this work. Desktop/Vive task files were never modified. The full visual source is not duplicated in this print package; its extracted accepted surfaces, inventory and print dispositions are supplied.

Historic print geometry and conventions: `output_3d_v4/model_geometry.json`, `projection_furnished_v04`, `projection_enclosed_v05`, `projection_acrylic_v06` and `output_v12_roof_set`. New rooms/walls/floors/furniture are reconstructed from active accepted v25 surfaces, not imported wholesale from the old print solids. Historic roof/window datums and generators retained for traceability are under `workflow_inputs`.

Each full large variant has STL, assembly 3MF and a reopened STEP. STEP is a closed faceted B-representation, not parametric building CAD. Upper STEP has four valid closed solids corresponding to actual disconnected supported components; the ground STEPs each have one. Editable Blender meshes, heightfield NPZs and generators are the editing sources.

Final checks cover 41 STL files and 40 reopened 3MF files: watertight meshes, consistent normals, no zero-area faces, explicit component counts, flat undersides, no elevated downward-facing triangles, per-piece bed fit, assembly volume equivalence and dimensions. All four STEP files reopen with valid solids and matching mesh volume/dimensions. The editable Blender file reopens with ten mesh objects and matching dimensions. A zero-area corner triangle in the upper glazing union was removed using 0.001 mm coordinate quantization and 0.005 mm bounded simplification; evidence is in `corner_cleanup.json`.

`review` contains actual top, isometric and 18 mm section images, split maps, and actual STL sections 1 m above floor over the registered governing AV plans. Source registration RMS is 0.0717 m ground / 0.0614 m upper; endpoint allowances are 0.159 m / 0.130 m. These inherited source limits remain. Mesh sampling and print reinforcement intentionally broaden small features. This is a schematic display model; no slicer run, physical fit, print, material purchase or order was performed. Old projection masks/videos should not be used with the revised geometry without regeneration/calibration.

## Regeneration

The generators use Python 3.10, NumPy 2.2.6, SciPy 1.15.3, trimesh 5.1.0, manifold3d 3.5.4 and Shapely 2.1.2. Use the supplied `workflow_inputs` and accepted surface NPZ; run `build_revised.py ground upper`, then `build_acrylic_revised.py`, `build_auxiliary.py` and `build_stack_revised.py`. STEP export uses the existing OCP 7.9.3 dependency at `C:/Users/mikef/Documents/ChatGPT/Campus Center/tmp/cadpackages`; install a compatible OCP separately if running elsewhere. Blender 5.0 creates the edit/review scene. Review scripts additionally use Pillow and PyMuPDF; the verified Tank environment uses KiCad's Python 3.11 with the existing `.pdf-tools` folder. No system dependency was changed.

## Ground furnished: 8 pieces in six bed regions

| Piece | X x Y x Z mm | Assembly X / Y / Z mm |
|---|---|---|
| Ground_Furnished_A1 | 245.500 x 190.000 x 53.568 | 17.500 / 97.000 / 0.000 |
| Ground_Furnished_A2 | 245.500 x 279.000 x 53.568 | 263.000 / 8.000 / 0.000 |
| Ground_Furnished_A3 | 245.500 x 263.000 x 53.568 | 508.500 / 24.000 / 0.000 |
| Ground_Furnished_B1_1 | 224.500 x 191.500 x 53.568 | 17.500 / 287.000 / 0.000 |
| Ground_Furnished_B1_2 | 19.500 x 279.000 x 53.568 | 243.500 / 287.000 / 0.000 |
| Ground_Furnished_B2 | 245.500 x 279.000 x 53.568 | 263.000 / 287.000 / 0.000 |
| Ground_Furnished_B3_1 | 188.000 x 93.500 x 53.568 | 537.000 / 287.000 / 0.000 |
| Ground_Furnished_B3_2 | 27.000 x 279.000 x 53.568 | 508.500 / 287.000 / 0.000 |

## Ground enclosed: 6 pieces in six bed regions

| Piece | X x Y x Z mm | Assembly X / Y / Z mm |
|---|---|---|
| Ground_Enclosed_A1 | 245.500 x 190.000 x 53.568 | 17.500 / 97.000 / 0.000 |
| Ground_Enclosed_A2 | 245.500 x 279.000 x 53.568 | 263.000 / 8.000 / 0.000 |
| Ground_Enclosed_A3 | 245.500 x 263.000 x 53.568 | 508.500 / 24.000 / 0.000 |
| Ground_Enclosed_B1 | 245.500 x 279.000 x 53.568 | 17.500 / 287.000 / 0.000 |
| Ground_Enclosed_B2 | 245.500 x 279.000 x 53.568 | 263.000 / 287.000 / 0.000 |
| Ground_Enclosed_B3 | 216.500 x 279.000 x 53.568 | 508.500 / 287.000 / 0.000 |

## Ground acrylic: 6 pieces in six bed regions

| Piece | X x Y x Z mm | Assembly X / Y / Z mm |
|---|---|---|
| Ground_Acrylic_A1 | 246.424 x 192.795 x 53.568 | 17.500 / 94.205 / 0.000 |
| Ground_Acrylic_A2 | 246.424 x 279.000 x 53.568 | 263.924 / 8.000 / 0.000 |
| Ground_Acrylic_A3 | 246.424 x 265.746 x 53.568 | 510.349 / 21.254 / 0.000 |
| Ground_Acrylic_B1 | 246.424 x 279.000 x 53.568 | 17.500 / 287.000 / 0.000 |
| Ground_Acrylic_B2 | 246.424 x 279.000 x 53.568 | 263.924 / 287.000 / 0.000 |
| Ground_Acrylic_B3 | 217.244 x 279.000 x 53.568 | 510.349 / 287.000 / 0.000 |

## Upper enclosed: 9 pieces in six bed regions

| Piece | X x Y x Z mm | Assembly X / Y / Z mm |
|---|---|---|
| Upper_Enclosed_A1 | 256.319 x 188.117 x 53.568 | 14.500 / 100.000 / 0.000 |
| Upper_Enclosed_A2 | 256.319 x 191.000 x 53.568 | 270.819 / 24.500 / 0.000 |
| Upper_Enclosed_A3_1 | 256.319 x 280.383 x 53.568 | 527.138 / 7.734 / 0.000 |
| Upper_Enclosed_A3_2 | 1.500 x 27.000 x 17.064 | 556.500 / 122.500 / 0.000 |
| Upper_Enclosed_B1 | 256.319 x 280.383 x 53.568 | 14.500 / 288.117 / 0.000 |
| Upper_Enclosed_B2 | 256.319 x 4.500 x 53.568 | 270.819 / 564.000 / 0.000 |
| Upper_Enclosed_B3_1 | 200.292 x 280.383 x 53.568 | 527.138 / 288.117 / 0.000 |
| Upper_Enclosed_B3_2 | 33.000 x 11.000 x 52.032 | 590.500 / 371.500 / 0.000 |
| Upper_Enclosed_B3_3 | 23.000 x 1.500 x 17.152 | 653.500 / 397.500 / 0.000 |

