# Cycles Studio v02 - blue interior palette

Open `Campus_Center_Cycles_Studio.blend`. This packed scene is a separate revision of v01 with light blue matte interior paint and muted blue-gray carpet in the ground-floor commons. Oak, sage upholstery, exterior masonry, and the brick fireplace accent remain.

The carpet is a spatially bounded shader on the existing slab, with fine fiber bump, mottling and sheen. It adds no geometry and preserves furniture floor contacts. Interior paint is assigned by wall face; structural geometry and the existing walkthrough are retained. Mannequins remain available in their hidden collection.

`stills/` contains entrance, commons, and iLab views as 1080p 16-bit PNGs, multilayer EXRs and JPEG viewing copies. Cycles uses CUDA, adaptive sampling with a 256-sample cap, denoising, AgX and subtle f/8 depth of field.

Rebuild from `Source_Copy.blend` using `build_colors.py`; render the saved scene with `render_stills.py` in headless Blender. `build_report.json` records the paint assignments and exact carpet bounds. Validation reports check packed images, source preservation, render outputs and retained walkthrough.

Suggested next pass: improve recognizable foreground assets and graphics, especially the iLab equipment, King banners and furniture details. Those stand-ins now limit realism more than the lighting or render settings. Then render a short camera-motion test before the full walkthrough.
