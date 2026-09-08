# Campus Center - Cycles Studio v03

Open `Campus_Center_Cycles_Studio.blend`. All textures used by the scene are packed. This is an isolated detail revision of v02; the blue paint, commons carpet, building geometry and original walkthrough are retained.

## Details added

- Three navy King banners using the official school seal, with hanging rails and bottom weights.
- Six framed original geometric compositions in the existing upstairs gallery locations. These are decorative interpretations, not reproductions of actual student work.
- Two potted ficus-style plants in the commons, two entry-planter trees with underplanting, and grasses in the three existing terrace planters.
- Six lounge clusters rebuilt with rounded upholstery, cushion welts, tapered legs and table bases. Sage, ochre and slate fabric colors follow the supplied interior appearance references. The previously corrected offset of cluster 3 is retained.
- Cleaner Bambu H2D / AMS 2 Pro representations (two sets), BigRep ONE, Epson-style garment printer and representative UV flatbed. Added glass, machine frames, print beds, rods, nozzle assemblies, controls, spools and material differentiation. Existing planning envelopes and supports were used; these remain representative visualization assets, not manufacturer CAD. Bambu fronts are arranged toward the north aisle for the detail view.
- Amber hood / dark base material separation on the existing Formlabs CAD meshes.

New work is organized into four `V03` collections: Graphics and art, Planting, Refined commons furniture, Refined iLab equipment. Replaced objects are retained, hidden in render and viewport, and listed in `build_report.json`. Do not enable old and new representations together.

## Review

Six 1920 x 1080 images in `stills/`: entrance, commons, iLab, upper gallery, printer detail and entry planting. PNGs are 16-bit; EXRs retain multilayer render passes. JPEG copies and `Six_Views.jpg` are convenient previews. Cycles CUDA, 256-sample cap, adaptive threshold 0.01, denoising, AgX and f/8 depth of field. These are Blender renders, with no AI image enhancement.

The original walkthrough remains available; this revision does not render a new video. Review camera additions do not change its route. Exterior context remains sparse; this pass plants the existing containers rather than reconstructing the surrounding site.

## Rebuild and checks

`Source_Copy.blend` is the v02 input. Run `build_details.py` against that file using Blender 5.0, then run `render_stills.py` against the saved output. `make_graphics.py` uses Pillow and PyMuPDF to rasterize the included official SVG; the finished PNG texture is already included and packed. `render_contract.json` defines the batch.

`scene_validation.json` verifies original mesh counts and transforms, hidden replacements, unchanged v02 source, packed dependencies, retained route, paint and carpet. `image_validation.json` verifies all final image dimensions, bit depth and EXR channels. Visual review was performed on representative previews and final images.

See `SOURCES.md` for asset provenance and the free-model search.
