# Campus Center — matched three-layer print set

Print `Campus_Center_Ground_v12.stl`, `Campus_Center_Upper_v12.stl`, and `Campus_Center_Roof_v12.stl` separately in millimetres at their supplied 1:350 scale, flat undersides on the bed. Stack in that order, aligning the gym perimeter and the west building edge. No extra rectangular ground planes or locking pins are included.

**Use the updated upper STL with this roof.** The ground STL is unchanged from revision 10. The upper piece now incorporates the single-storey athletics roof cap and has matching seating surfaces beneath the new roof. The third piece combines the main roof, gym roof and partial balcony canopy, with printable parapet relief and a solid corridor skylight strip. The skylight is an interpretation retained from the existing Blender model, rather than manufacturer roof CAD.

To make the roof one support-free print, its underside is flat and its thickness varies with the roof elevations. Corresponding upper wall tops are shortened beneath it. This changes the removable-piece split and the roof's underside thickness, while preserving the assembled roof elevations. Minimum roof thickness is 1.2 mm. Small details are broadened for printing; roofs and stair voids are solid. The openings in the floors remain visible when the roof is removed.

Digital assembly offsets, retaining original shared XY coordinates:

| Piece | Z offset in mm |
|---|---:|
| Ground | 0 |
| Upper | 12.192 |
| Roof | 23.077714 |

The included Blender file shows assembled placement; the exploded preview uses additional separation only for illustration. Each STL was reopened and checked as one closed manifold component. Both stacking interfaces passed zero-penetration checks and projected-centroid support checks. Supports are unnecessary by the heightfield geometry, but no slicer run, physical print or fit test has been performed.

The original building model and earlier print revisions are preserved. If the earlier upper floor has already been printed, it must be replaced with this matched upper piece for the new roof to seat as shown.
