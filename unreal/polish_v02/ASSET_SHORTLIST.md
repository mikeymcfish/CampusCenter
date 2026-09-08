# Replacement model candidates

Reviewed September 7, 2026. The floor plans and existing equipment footprints remain authoritative. These are candidates, not claims about the school's final selected equipment.

| Priority | Asset | License / size | Current status |
|---|---|---|---|
| 1 | [Trophy — JeremyWoods](https://opengameart.org/content/trophy) | CC0; measured 3,028 triangles, one material | Downloaded, converted to GLB, normalized to 30 cm high, visually checked. `Trophy_Optimized.glb` is ready for a placement pass; not yet inserted. |
| 1 | [LowPoly Crossfit Treadmill — 3DLAND](https://sketchfab.com/3d-models/free-lowpoly-crossfit-treadmill-e0b9da4ef4504617bd58539bd450532d) | CC Attribution; publisher lists 1,200 triangles / 757 vertices | Shortlisted. Download, console/belt geometry, dimensions and appearance still need inspection. Attribution must accompany use. Low triangle count alone does not establish visual suitability. |
| 2 | [School Chair 01 — Ethan Place / Poly Haven](https://polyhaven.com/a/SchoolChair_01) | CC0; publisher lists about 5K triangles | Possible classroom chair. Its older scuffed school-chair style may conflict with the design references; do not replace the commons lounge seating with it. Use 1K textures and shared instances if selected. |
| 3 | [Trophy — GimmeTheGucci](https://sketchfab.com/3d-models/trophy-b2c21f7c7c0c46f28b98967dd55a8865) | CC Attribution; publisher lists 67.5K triangles | Higher-detail alternative for close shots; excessive for repeated cabinet props without simplification and LODs. Not downloaded. |

## Import approach

Keep each selected prop as one shared mesh asset with instances for repeated placements. Preserve the existing footprint, orientation and floor/shelf contact. Keep decorative trophies non-colliding; use simple collision for fitness equipment. Aim for 1–3 materials and 1K texture maps for small props; increase only for demonstrated close-up needs. Inspect normals, silhouette, pivot, scale and texture dependencies before replacing grouped stand-ins. Do not layer replacement props on top of the original geometry.

## Material sources used now

- [ambientCG Fabric030](https://ambientcg.com/view?id=Fabric030): CC0, 1K color/DirectX normal/roughness maps. Tinted to the existing sage upholstery palette.
- [ambientCG PaintedPlaster017](https://ambientcg.com/view?id=PaintedPlaster017): CC0, 1K color/DirectX normal/roughness maps. Subtle painted-plaster response with warm white tint.

Source URLs, download hashes and author/license records are preserved in `assets/SOURCES.json`. The existing wood, brick and stone textures retain their architectural mapping; this pass changes their material response, not their dimensions.
