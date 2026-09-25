# iLab V06 — furniture, metal tool boards, and TRELLIS equipment

Open the editable `CampusCenter_Dusk` map with `Edit_Commons_Dusk.cmd`, or launch the current walkthrough with `Walk_Commons_Dusk.cmd` from the Campus Center workspace root. The older packaged executable is not updated.

## Furniture

- 14 molded black chairs replace the basic straight-backed chairs. A shared mesh and texture set is reused across all seats.
- 9 new navy drafting stools have upholstered seats/backs, gas-lift columns, steel foot rings, five-star feet, and floor glides.
- 3 new modular worktables replace the plain collaboration table bank. Oak veneer PBR surfaces, beveled edges, steel T-legs, cable trays, and power strips add detail.
- 5 metal-framed pegboards are mounted on the east and west walls. Tools are an ImageGen texture; the panel and folded frame are geometry. This avoids rendering dozens of separate tool meshes.

Actors are under `iLab / V06 Furniture and tools`. Original furniture is retained but hidden and collision-disabled under `iLab / Original furniture (inactive)`. Repeated furniture uses shared static meshes. Textures are capped at 2K with Unreal texture-group mipmap generation.

## Equipment

Six new image-to-3D jobs were downloaded from Microsoft's hosted TRELLIS.2 demo, using 512 geometry resolution, 16 shape and texture sampling steps, seed 37, 100,000-triangle extraction, and 2K textures. The higher-resolution attempt aborted on the hosted GPU. No paid assets or GPU rentals were used.

Visual selection, not job success, determined placement:

- New Epson F2100, WAZER, representative Mimaki UV flatbed, and spray booth reconstructions selected for Unreal.
- The earlier textured Bambu reconstruction looked cleaner than the new generation. Its rear enclosure is repaired with an authored panel.
- Existing AMS approximation reused with a darker authored finish.
- New BigRep result rejected for distorted frame and filled open areas. The clean V05 approximation remains active.

These are approximate visualization assets, not manufacturer CAD. Small labels and unseen surfaces can be inaccurate. The UV printer photo is a representative reference, not a confirmed school make. See `tech_review.json` and `technology_manifest.json`.

Retained assets use at most about 80,000 triangles per type. Shared meshes serve repeated Bambu/AMS placements. WebP textures were losslessly re-encoded as PNG for Unreal's importer; geometry was preserved by that conversion. Maps use automatic mipmaps and a 2K cap. This is not a full-building FPS certification.

## Files and sources

- Editable upgrade sources: `ILab_Furniture.blend`, `ILab_Trellis.blend`.
- Interchange files: `ILab_Furniture.glb`, `ILab_Trellis_UE.glb`.
- Original raw generated models remain under `models/`; none replace manufacturer source files.
- Original campus `.blend` is preserved; hash is recorded in `furniture_manifest.json`.
- Eames chair by **Ar41k**, [Sketchfab](https://sketchfab.com/3d-models/eames-chair-5cde9f53b44040f596b3f2ebc15a9a8d), CC BY 4.0. Existing prepared asset reused; scale/origin adjusted in prior preparation.
- Oak veneer: [Poly Haven oak_veneer_01](https://polyhaven.com/a/oak_veneer_01), CC0.
- TRELLIS: [Microsoft TRELLIS.2](https://github.com/microsoft/TRELLIS.2), [hosted demo](https://huggingface.co/spaces/microsoft/TRELLIS.2). Project reference photos and generated references are listed in the generation progress reports and the earlier `output_v9/equipment/reference_sources.json`.
- Pegboard texture: built-in ImageGen, prompt recorded in `pegboard_prompt.txt`. Stool, table, and panel geometry authored for this project.

Original/superseded actors remain hidden and non-colliding. To move furniture, select its V06 actor and use W/E/R. To change crowd versus player boundaries, use `EDIT_WALKABLE_AREA.md` at the workspace root.
