# Campus Center - Cycles Studio v04

Open `Campus_Center_Cycles_Studio.blend`. This version preserves the v03 source and original walkthrough while improving the exterior and commons. All used image assets are packed.

## Changes

- Photographically textured potted plants, shrubs and grasses replace the V03 procedural foliage. Indoor pots stand at floor level. Entry containers use dense varied shrub instances over mulch; balcony containers use grass clumps. Shared geometry keeps plant instances economical.
- A continuous lawn replaces the empty exterior background at ground level. Concrete entry plaza and connecting walks meet the modeled approach. The lawn uses a 2K grass surface blended in two orientations plus near-field geometry blades; concrete has aggregate variation and control joints. These are simplified visual landscape surfaces informed by the supplied L-200 / L-400 sheets and existing model, not a fully surveyed site or a complete landscape-plan reconstruction.
- The curved seating group immediately in front of the fireplace is retained but disabled to clear the view. Other seating remains. Enable `V15_Commons_curved_lounge` only if the original obstructing arrangement is wanted.
- A photographic fire-and-log image, created with the built-in Imagegen tool, sits inside the existing fireplace recess with warm area-light illumination on the hearth. This is a static emissive billboard, not a simulated or animated fire. The generated asset and full prompt are in `assets/fire_insert.png` and `FIRE_PROMPT.md`.
- Commons banners are exactly twice the previous width and height: approximately 1.4 x 4.2 m each. Centers and logo aspect ratio are preserved; rails and bottom weights follow the enlarged fabric.
- Brick colors now vary per brick and over broad wall areas; continuous world-space paint microtexture and oak grain replace the conspicuous short bitmap repeats. Blue paint and commons carpeting remain. The wood treatment is a procedural visualization finish, not a manufacturer finish specification.
- A packed 4K Greenwich Park HDRI provides a photographic sky, horizon and reflections, balanced with a soft directional daylight source. This panorama is illustrative scenery, not a photograph of the actual school grounds.

## Images and controls

`stills/Seven_Views.jpg` is the overview. Seven 1920 x 1080 16-bit PNGs and multilayer EXRs cover entrance, commons, iLab, gallery, printer detail, exterior planting and fireplace. JPEG viewing copies are included. Cycles CUDA, 256-sample cap, adaptive threshold 0.01, denoising, AgX. The existing walkthrough has not been rendered as a new video.

New content is in `V04 Site grass and concrete`, `V04 Textured planting` and `V04 Fireplace fire`. Plant source collections prefixed `V04 ASSET` are shared templates referenced by collection instances. V03 foliage and the curved lounge are retained hidden.

## Rebuild and validation

Run `build_environment.py` against `Source_Copy.blend`, then `render_stills.py` against the saved output using Blender 5.0. `render_contract.json` records the output specification. All referenced input assets are included or packed.

`scene_validation.json` records unchanged source hash, retained original objects/topology/transforms, intentional visibility changes, banner dimensions, packed image dependencies, fire and HDRI setup, and retained camera route. `image_validation.json` checks final dimensions, PNG bit depth and EXR channels. Representative previews and final views were also visually inspected.

See `SOURCES.md` and `assets/DOWNLOADS.json` for provenance and download checksums.
